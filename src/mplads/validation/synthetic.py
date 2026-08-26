"""Synthetic injection: plant known anomalies in real records and measure recall.

This is the honest answer to "how do you know it works when there are no fraud labels?"

We cannot validate against fraud, because no fraud labels exist in any public MPLADS
source. What we *can* validate is the **machinery**: if we deliberately plant a work whose
amount is wildly out of line with its peers, does the system surface it? If we plant a
stalled work, does the early-warning engine catch it? If we clone a description within one
agency, does the duplicate detector find it?

That is a measurable, reproducible claim. What it is NOT:

    Recall@k on planted anomalies is NOT a real-world fraud detection rate.

It measures whether the technique detects the patterns it was designed to detect. A real
fraudster does not have to produce any of these patterns, and most works that produce them
are perfectly legitimate. Both facts are stated wherever the number is shown.
"""

from __future__ import annotations

import json
import logging

import numpy as np
import pandas as pd

from mplads import config
from mplads.intelligence import compliance, duplicates, early_warning

LOGGER = logging.getLogger(__name__)

#: How many works to perturb per anomaly type.
N_PER_TYPE = 250

PERTURBATIONS = (
    "inflated_amount",
    "stalled_lifecycle",
    "cloned_description",
    "lifecycle_break",
)


def _inflate_amount(frame: pd.DataFrame, idx: np.ndarray, rng) -> pd.DataFrame:
    """Push the recommended amount far above the work's peer group."""
    factor = rng.uniform(8, 25, size=len(idx))
    frame.loc[idx, "recommended_amount"] = (
        frame.loc[idx, "recommended_amount"].astype(float) * factor
    )
    return frame


def _stall_lifecycle(frame: pd.DataFrame, idx: np.ndarray, rng) -> pd.DataFrame:
    """Make an open work far older than its peers, without touching completion."""
    extra = rng.integers(900, 2200, size=len(idx))
    frame.loc[idx, "recommendation_date"] = frame.loc[idx, "recommendation_date"] - pd.to_timedelta(
        extra, unit="D"
    )
    return frame


def _clone_description(frame: pd.DataFrame, idx: np.ndarray, rng) -> pd.DataFrame:
    """Clone a sibling's description, agency and amount — the shape of a repeat claim."""
    for target in idx:
        row = frame.loc[target]
        siblings = frame[
            (frame["state_name"] == row["state_name"])
            & (frame["archetype_id"] == row["archetype_id"])
            & (frame.index != target)
            & frame["work_description"].notna()
        ]
        if siblings.empty:
            continue
        donor = siblings.iloc[int(rng.integers(0, len(siblings)))]
        frame.loc[target, "work_description"] = donor["work_description"]
        frame.loc[target, "implementing_agency"] = donor["implementing_agency"]
        frame.loc[target, "recommended_amount"] = donor["recommended_amount"]
    return frame


def _break_lifecycle(frame: pd.DataFrame, idx: np.ndarray, rng) -> pd.DataFrame:
    """Record a completion with no sanction, and back-date some of them."""
    frame.loc[idx, "is_completed"] = True
    frame.loc[idx, "is_sanctioned"] = False
    frame.loc[idx, "completed_without_sanction"] = True
    half = idx[: len(idx) // 2]
    frame.loc[half, "completion_date"] = frame.loc[half, "recommendation_date"] - pd.to_timedelta(
        rng.integers(30, 400, size=len(half)), unit="D"
    )
    frame.loc[half, "is_backdated"] = True
    return frame


INJECTORS = {
    "inflated_amount": _inflate_amount,
    "stalled_lifecycle": _stall_lifecycle,
    "cloned_description": _clone_description,
    "lifecycle_break": _break_lifecycle,
}


def inject(works: pd.DataFrame, n_per_type: int = N_PER_TYPE, seed: int | None = None):
    """Return (perturbed_frame, truth) where truth maps work_ref -> perturbation type."""
    rng = np.random.default_rng(config.RANDOM_SEED if seed is None else seed)
    frame = works.copy()

    # Only perturb ordinary works: ones that are not already surfaced, so a hit is
    # attributable to the injection rather than to something the work already had.
    eligible = frame[
        (frame["band"].isin(["NONE", "LOW"]))
        & frame["recommended_amount"].notna()
        & frame["recommendation_date"].notna()
        & frame["work_description"].notna()
    ].index.to_numpy()
    rng.shuffle(eligible)

    truth: dict[str, str] = {}
    cursor = 0
    for name in PERTURBATIONS:
        picked = eligible[cursor : cursor + n_per_type]
        cursor += n_per_type
        if name == "stalled_lifecycle":
            open_only = frame.loc[picked]
            picked = open_only[open_only["is_open"]].index.to_numpy()
        frame = INJECTORS[name](frame, picked, rng)
        for ref in frame.loc[picked, "work_ref"]:
            truth[ref] = name
        LOGGER.info("injected %-20s into %s works", name, f"{len(picked):,}")

    return frame, truth


def rescore(frame: pd.DataFrame) -> pd.DataFrame:
    """Re-run the scoring chain on perturbed data, reusing the already-trained models."""
    from mplads import pipeline

    # The baseline frame already carries every derived column. Drop them so the engines
    # recompute cleanly instead of colliding into _x/_y suffixes on merge.
    stale = [
        "peer_median_days", "stall_ratio", "early_warning_score", "early_warning_level",
        "early_warning_reason", "duplicate_similarity", "duplicate_partner",
        "amount_pct", "amount_z", "open_duration_pct", "anomaly_flag",
        "priority", "n_families", "band", "rs_exposure", "audit_roi", "compliance_flags",
        "compliance_severity",
    ]
    frame = frame.drop(columns=[c for c in stale if c in frame.columns], errors="ignore")
    frame = frame.drop(columns=[c for c in frame.columns if c.startswith("chk_")], errors="ignore")

    frame = pipeline.add_features(frame, pd.DataFrame())
    frame = pipeline.add_peer_comparison(frame)
    frame["risk_score"] = frame["risk_score"].fillna(0.0)
    frame.loc[frame["is_completed"], "risk_score"] = 0.0
    frame = pipeline.add_anomaly(frame)

    pairs = duplicates.detect(frame)
    if not pairs.empty:
        signal = duplicates.per_work_signal(pairs, frame)
        frame = frame.drop(columns=[c for c in signal.columns if c != "work_ref"], errors="ignore")
        frame = frame.merge(signal, on="work_ref", how="left")

    frame = compliance.evaluate(frame)
    frame = pipeline.add_fusion(frame)
    frame = early_warning.score(frame)
    return frame


def evaluate(scored: pd.DataFrame, truth: dict[str, str], ks=(100, 500, 1000, 5000)) -> dict:
    """Detection and ranking, measured separately — they answer different questions.

    **Detection** (`surfaced_rate`): did the corroboration rule surface the planted work at
    all? This is the question "does the technique work?".

    **Ranking** (`recall@k`): did it reach the top of the queue? Audit-ROI deliberately
    multiplies by rupee exposure, so a small planted work ranks below a genuinely larger
    real one. A low recall@k with a high surfaced rate is the system behaving *correctly*,
    not failing — so both are reported, by both ranking strategies.
    """
    by_roi = scored.sort_values("audit_roi", ascending=False).reset_index(drop=True)
    by_priority = scored.sort_values("priority", ascending=False).reset_index(drop=True)
    surfaced_refs = set(scored.loc[scored["band"].isin(["MEDIUM", "HIGH"]), "work_ref"])

    def recalls(ranked: pd.DataFrame, planted: set[str]) -> dict:
        return {
            f"recall@{k}": round(len(planted & set(ranked.head(k)["work_ref"])) / len(planted), 4)
            for k in ks
        }

    per_type: dict[str, dict] = {}
    for name in PERTURBATIONS:
        planted = {ref for ref, kind in truth.items() if kind == name}
        if not planted:
            continue
        per_type[name] = {
            "planted": len(planted),
            "detected_rate": round(len(planted & surfaced_refs) / len(planted), 4),
            "by_audit_roi": recalls(by_roi, planted),
            "by_priority": recalls(by_priority, planted),
        }

    all_planted = set(truth)
    overall = {
        "planted_total": len(all_planted),
        "detected_rate": round(len(all_planted & surfaced_refs) / len(all_planted), 4),
        "by_audit_roi": recalls(by_roi, all_planted),
        "by_priority": recalls(by_priority, all_planted),
        "precision@k_by_priority": {
            f"precision@{k}": round(
                len(all_planted & set(by_priority.head(k)["work_ref"])) / k, 4
            )
            for k in ks
        },
    }

    return {
        "overall": overall,
        "per_perturbation": per_type,
        "interpretation": (
            "`detected_rate` is the share of planted anomalies the corroboration rule "
            "surfaced at all — the measure of whether the technique works. `recall@k` is the "
            "share reaching the top k of the queue. Audit-ROI multiplies by rupee exposure "
            "by design, so a small planted work correctly ranks below a larger real one; "
            "recall by priority is therefore the fairer ranking measure."
        ),
        "not_a_fraud_rate": (
            "This is NOT a real-world fraud detection rate. No fraud labels exist in any "
            "public MPLADS source. A real irregularity need not produce any of these "
            "patterns, and the vast majority of works that do produce them are legitimate."
        ),
    }


def run(n_per_type: int = N_PER_TYPE) -> dict:
    """Full harness: inject, rescore, measure, and write the report."""
    works = pd.read_parquet(config.ARTIFACTS / "works_scored.parquet")
    LOGGER.info("validation: baseline %s works", f"{len(works):,}")

    perturbed, truth = inject(works, n_per_type=n_per_type)
    scored = rescore(perturbed)
    report = evaluate(scored, truth)
    report["n_per_type"] = n_per_type
    report["baseline_works"] = int(len(works))

    out = config.ARTIFACTS / "validation.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    LOGGER.info("validation: detected_rate = %s", report["overall"]["detected_rate"])
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    result = run()
    print(json.dumps(result["overall"], indent=2))
    for kind, stats in result["per_perturbation"].items():
        print(f"{kind:<22} {stats}")
