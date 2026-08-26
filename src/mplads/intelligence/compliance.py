"""Compliance & lifecycle-deviation engine.

Every check declares its own authority, and the UI shows it. This is the difference between
a defensible system and one that calls a statistical outlier a legal violation:

    OBSERVED_BASELINE  — inconsistent with the workflow the data itself demonstrates
                         (e.g. a completion recorded before the recommendation). These are
                         record-integrity failures: something is wrong with the record, even
                         if the underlying work is fine.
    STATISTICAL_OUTLIER— unusual relative to comparable works. Not a rule, not a breach.
    OFFICIAL_RULE      — a published statutory threshold. **We currently assert none**,
                         because no authoritative machine-readable norm ships with this
                         dataset. The tier exists so a real norm can be added without
                         restructuring anything.

Nothing here is described as a violation, an irregularity, or a breach.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from mplads import config

LOGGER = logging.getLogger(__name__)

SNAPSHOT = pd.Timestamp(config.SNAPSHOT_DATE)

#: check -> (authority tier, severity, plain-English meaning)
CHECKS: dict[str, tuple[str, str, str]] = {
    "completed_without_sanction": (
        "OBSERVED_BASELINE", "HIGH",
        "Recorded as completed with no sanction record. The workflow every other work "
        "follows is recommend -> sanction -> complete.",
    ),
    "completion_before_recommendation": (
        "OBSERVED_BASELINE", "HIGH",
        "The completion date precedes the recommendation date, which is not possible in "
        "the real world. The record's dates are inconsistent.",
    ),
    "completion_beyond_snapshot": (
        "OBSERVED_BASELINE", "MEDIUM",
        "The completion date falls after the data snapshot, in some cases years after. "
        "This is a data-entry error rather than a future plan.",
    ),
    "missing_recommendation_record": (
        "OBSERVED_BASELINE", "HIGH",
        "The work appears at sanction or completion but has no recommendation record at "
        "all, so its origin cannot be traced.",
    ),
    "non_positive_amount": (
        "OBSERVED_BASELINE", "MEDIUM",
        "The recommended amount is zero or negative, so no financial reading is possible.",
    ),
    "missing_description": (
        "OBSERVED_BASELINE", "LOW",
        "No work description was recorded, so the work cannot be classified or compared "
        "with its peers.",
    ),
    "stalled_beyond_peer_norm": (
        "STATISTICAL_OUTLIER", "MEDIUM",
        "Open far longer than comparable works of the same type in the same state.",
    ),
    "amount_outlier_vs_peers": (
        "STATISTICAL_OUTLIER", "MEDIUM",
        "The recommended amount sits far above comparable works of the same type in the "
        "same state.",
    ),
}


def evaluate(works: pd.DataFrame) -> pd.DataFrame:
    """Attach one boolean column per check, plus a rolled-up count and severity."""
    frame = works.copy()

    frame["chk_completed_without_sanction"] = frame["completed_without_sanction"].fillna(False)
    frame["chk_completion_before_recommendation"] = frame["is_backdated"].fillna(False)
    frame["chk_completion_beyond_snapshot"] = frame["is_future_dated"].fillna(False)
    frame["chk_missing_recommendation_record"] = frame["is_orphan"].fillna(False)
    frame["chk_non_positive_amount"] = frame["has_nonpositive_amount"].fillna(False)
    frame["chk_missing_description"] = frame["work_description"].isna()

    # Statistical tiers: only meaningful where a peer comparison actually ran.
    frame["chk_stalled_beyond_peer_norm"] = (
        frame["is_open"] & (frame.get("open_duration_pct", pd.Series(np.nan, index=frame.index)) >= 0.99)
    ).fillna(False)
    frame["chk_amount_outlier_vs_peers"] = (
        frame.get("amount_pct", pd.Series(np.nan, index=frame.index)) >= 0.99
    ).fillna(False)

    columns = [f"chk_{name}" for name in CHECKS]
    frame["compliance_flags"] = frame[columns].sum(axis=1).astype(int)

    severity_rank = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    worst = np.zeros(len(frame), dtype=int)
    for name, (_, severity, _) in CHECKS.items():
        hit = frame[f"chk_{name}"].to_numpy()
        worst = np.maximum(worst, hit * severity_rank[severity])
    frame["compliance_severity"] = pd.Series(worst, index=frame.index).map(
        {0: "NONE", 1: "LOW", 2: "MEDIUM", 3: "HIGH"}
    )

    for name in CHECKS:
        LOGGER.info("compliance: %-34s %s", name, f"{int(frame[f'chk_{name}'].sum()):,}")
    return frame


def findings_for(row: pd.Series) -> list[dict]:
    """The compliance findings for one work, each with its authority tier."""
    out = []
    for name, (authority, severity, meaning) in CHECKS.items():
        if bool(row.get(f"chk_{name}", False)):
            out.append(
                {
                    "check": name.replace("_", " ").capitalize(),
                    "authority": authority,
                    "severity": severity,
                    "meaning": meaning,
                }
            )
    return out


def summary(works: pd.DataFrame) -> dict:
    """Scheme-wide compliance picture for the dashboards."""
    rows = []
    for name, (authority, severity, meaning) in CHECKS.items():
        count = int(works[f"chk_{name}"].sum())
        rows.append(
            {
                "check": name.replace("_", " ").capitalize(),
                "key": name,
                "authority": authority,
                "severity": severity,
                "meaning": meaning,
                "works_affected": count,
                "share_pct": round(100 * count / max(len(works), 1), 3),
            }
        )
    return {
        "checks": sorted(rows, key=lambda r: -r["works_affected"]),
        "works_with_any_flag": int((works["compliance_flags"] > 0).sum()),
        "authority_note": (
            "No official statutory threshold ships with this public dataset, so no check is "
            "asserted as an OFFICIAL_RULE. Observed-baseline checks describe records that "
            "contradict the workflow the data itself demonstrates; statistical checks "
            "describe unusual works. Neither is a finding of wrongdoing."
        ),
    }
