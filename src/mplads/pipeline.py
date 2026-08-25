"""End-to-end intelligence pipeline: Learn -> Compare -> Predict -> Explain -> Prioritise.

Runs over data/interim/works.parquet (Phase 1 output) and writes every artifact the API
serves into data/artifacts/. Transparent and rule-based throughout: there is no supervised
fraud model, no fraud label, and no output is a probability of wrongdoing. Every surfaced
work carries the evidence that surfaced it and one recommended action for a human.

    python -m mplads.pipeline
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from mplads import config

LOGGER = logging.getLogger(__name__)
SNAPSHOT = pd.Timestamp(config.SNAPSHOT_DATE)

ACTIVITY_RE = re.compile(r"^WS/MP\d+/\d{4}-\d{4}/\d+-(?P<category>.+)$", re.S)


# --------------------------------------------------------------------------- Learn


def add_activity_category(works: pd.DataFrame) -> pd.DataFrame:
    """Parse the official permissible-works category out of ACTIVITY_NAME (93% coverage)."""
    cat = works["activity_name"].str.extract(ACTIVITY_RE)["category"].str.strip()
    works["activity_category"] = cat.fillna("Uncategorised")
    LOGGER.info(
        "activity_category: %s distinct, %.1f%% parsed",
        works["activity_category"].nunique(),
        100 * (works["activity_category"] != "Uncategorised").mean(),
    )
    return works


def add_archetypes(works: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Attach the trained archetype cluster and its label to each work.

    Membership comes from our own MiniBatchKMeans model (see mplads.train); labels are the
    c-TF-IDF distinctive terms produced during training. Run `mplads train` first.
    """
    models = config.ARTIFACTS / "models"
    assign = pd.read_parquet(models / "archetype_assignment.parquet")
    catalog = pd.read_parquet(models / "archetype_catalog.parquet")

    works = works.merge(assign, on="work_description", how="left")
    works["archetype_id"] = works["archetype_id"].astype("Int64")
    labels = dict(zip(catalog["archetype_id"], catalog["label"]))
    works["archetype_label"] = works["archetype_id"].map(labels).fillna("unassigned")

    catalog = catalog.rename(columns={"n_descriptions": "n_works"})
    LOGGER.info("archetypes: %s of %s works assigned (trained KMeans)",
                f"{int(works['archetype_id'].notna().sum()):,}", f"{len(works):,}")
    return works, catalog


# ------------------------------------------------------------------------- features


def add_features(works: pd.DataFrame, stages: pd.DataFrame) -> pd.DataFrame:
    """Lifecycle features with correct right-censoring at the snapshot date."""
    rec = works["recommendation_date"]
    comp = works["completion_date"]

    valid_dates = works["is_backdated"].eq(False) & works["is_future_dated"].eq(False)
    works["event_observed"] = (works["is_completed"] & valid_dates).astype(int)

    duration = np.where(
        works["is_completed"] & valid_dates,
        (comp - rec).dt.days,
        (SNAPSHOT - rec).dt.days,
    )
    works["duration_days"] = pd.to_numeric(duration, errors="coerce")
    # Orphans (no recommendation date) and anomalies cannot enter the survival fit.
    works.loc[works["duration_days"] < 0, "duration_days"] = np.nan
    works["log_amount"] = np.log1p(works["recommended_amount"].astype("float"))
    works["is_open"] = ~works["is_completed"]
    return works


# ------------------------------------------------------------------------- Compare


def _robust_z(values: pd.Series) -> pd.Series:
    """Median/MAD z-score with an IQR fallback for round-number-bunched groups."""
    med = values.median()
    mad = (values - med).abs().median()
    scale = 1.4826 * mad
    if scale <= 0:
        iqr = values.quantile(0.75) - values.quantile(0.25)
        scale = iqr / 1.349
    if scale <= 0:
        return pd.Series(0.0, index=values.index)
    return (values - med) / scale


def _loo_percentile(values: pd.Series) -> pd.Series:
    """Leave-one-out percentile rank: each work ranked against its peers, not itself."""
    n = len(values)
    if n <= 1:
        return pd.Series(np.nan, index=values.index)
    ranks = values.rank(method="average")
    return (ranks - 1) / (n - 1)


def add_peer_comparison(works: pd.DataFrame) -> pd.DataFrame:
    """Score each work against genuinely comparable works via hierarchical back-off.

    Levels: activity_category x state -> activity_category -> state -> global. The first
    level with at least MIN_PEERS works is used, and the level is recorded per work.
    """
    works = works.copy()
    works["peer_level"] = "global"
    works["peer_group_id"] = "GLOBAL"
    works["peer_group_size"] = len(works)

    levels = [
        ("cat_state", ["activity_category", "state_name"]),
        ("cat", ["activity_category"]),
        ("state", ["state_name"]),
    ]
    assigned = pd.Series(False, index=works.index)
    for level_name, keys in levels:
        sizes = works.groupby(keys)["work_ref"].transform("size")
        take = (sizes >= config.MIN_PEERS) & (~assigned)
        gid = works[keys].astype(str).agg("|".join, axis=1)
        works.loc[take, "peer_level"] = level_name
        works.loc[take, "peer_group_id"] = level_name + ":" + gid[take]
        works.loc[take, "peer_group_size"] = sizes[take]
        assigned |= take

    LOGGER.info("peer levels: %s", works["peer_level"].value_counts().to_dict())

    # Amount and open-duration scores computed within the assigned peer group.
    works["amount_pct"] = np.nan
    works["amount_z"] = np.nan
    works["open_duration_pct"] = np.nan
    for _, idx in works.groupby("peer_group_id").groups.items():
        grp = works.loc[idx]
        amt = grp["recommended_amount"].astype("float")
        works.loc[idx, "amount_pct"] = _loo_percentile(amt)
        works.loc[idx, "amount_z"] = _robust_z(amt)
        open_grp = grp[grp["is_open"]]
        if len(open_grp) > 1:
            works.loc[open_grp.index, "open_duration_pct"] = _loo_percentile(
                open_grp["duration_days"]
            )
    return works


# ------------------------------------------------------------------------- Predict


def add_completion_risk(works: pd.DataFrame) -> pd.DataFrame:
    """Attach the trained Cox model's completion-risk score. Not a score of wrongdoing.

    risk_score = 1 - S_i(horizon): the model's estimated chance this work has NOT completed
    within the horizon, given its amount, sanction status, state and archetype. Completed
    works carry 0. Run `mplads train` first.
    """
    works = works.copy()
    risk = pd.read_parquet(config.ARTIFACTS / "models" / "risk_scores.parquet")
    works = works.merge(risk, on="work_ref", how="left")

    works["risk_score"] = works["cox_risk"].fillna(0.0).clip(0, 1)
    works.loc[works["is_completed"], "risk_score"] = 0.0
    works["risk_level_used"] = np.where(works["cox_risk"].notna(), "cox_model", "unscored")
    LOGGER.info(
        "completion risk: Cox scores attached to %s works (open, scored)",
        f"{int((works['risk_score'] > 0).sum()):,}",
    )
    return works


# ------------------------------------------------------ behaviour (light change-point)


def add_change_points(works: pd.DataFrame) -> pd.DataFrame:
    """Flag implementing agencies whose recommendation behaviour shifted between years.

    Deliberately uses recommendation-time volume and median amount only — completion-based
    series are censoring-contaminated and would make every recent period look 'changed'.
    A change point is a lead ('behaviour changed'), never 'misconduct occurred'.
    """
    works = works.copy()
    works["change_point"] = 0.0
    df = works.dropna(subset=["recommendation_date", "implementing_agency"]).copy()
    df["year"] = df["recommendation_date"].dt.year

    agg = (
        df.groupby(["implementing_agency", "year"])
        .agg(n=("work_ref", "size"), med_amt=("recommended_amount", "median"))
        .reset_index()
    )
    agg = agg[agg["n"] >= 5]
    shifted: dict[str, float] = {}
    for agency, g in agg.groupby("implementing_agency"):
        if len(g) < 2:
            continue
        g = g.sort_values("year")
        amt = g["med_amt"].to_numpy()
        rel = np.abs(np.diff(amt)) / (amt[:-1] + 1e-9)
        if rel.size and rel.max() > 0.5:  # >50% median-amount shift year on year
            shifted[agency] = float(min(1.0, rel.max()))

    mask = works["implementing_agency"].isin(shifted)
    works.loc[mask, "change_point"] = works.loc[mask, "implementing_agency"].map(shifted)
    LOGGER.info("change points: %s agencies flagged", len(shifted))
    return works


# ------------------------------------------------------------ Explain & Prioritise


def add_anomaly(works: pd.DataFrame) -> pd.DataFrame:
    """Attach the trained IsolationForest multivariate outlier flag as one signal."""
    works = works.copy()
    iso = joblib.load(config.ARTIFACTS / "models" / "isolation_forest.joblib")
    snap = SNAPSHOT
    feats = pd.DataFrame({
        "log_amount": np.log1p(works["recommended_amount"].fillna(0)),
        "age_days": (snap - works["recommendation_date"]).dt.days.fillna(0).clip(lower=0),
    })
    feats = (feats - feats.mean()) / (feats.std() + 1e-9)
    works["anomaly_flag"] = (iso.predict(feats.values) == -1).astype(float)
    LOGGER.info("anomaly: %s works flagged by trained IsolationForest",
                f"{int(works['anomaly_flag'].sum()):,}")
    return works


def _sigmoid(x: pd.Series) -> pd.Series:
    return 1 / (1 + np.exp(-x))


def add_fusion(works: pd.DataFrame) -> pd.DataFrame:
    """Combine signals into a transparent priority, exposure and audit-ROI ranking."""
    works = works.copy()

    # Normalise each raw signal into [0,1]. Each has a plain-English meaning.
    gate = config.PEER_PERCENTILE_GATE
    works["sig_peer_amount"] = np.where(
        works["amount_pct"] >= gate, _sigmoid((works["amount_z"] - 2).clip(-6, 6)), 0.0
    )
    works["sig_peer_duration"] = np.where(
        works["open_duration_pct"] >= gate, works["open_duration_pct"].fillna(0.0), 0.0
    )
    works["sig_completion_risk"] = np.where(works["risk_score"] >= 0.60, works["risk_score"], 0.0)
    conf = (
        works["is_backdated"].astype(float)
        + works["completed_without_sanction"].astype(float)
        + works["is_future_dated"].astype(float)
        + works["is_orphan"].astype(float)
    ).clip(0, 1)
    works["sig_conformance"] = conf * 0.9
    works["sig_change_point"] = works["change_point"].fillna(0.0)
    works["sig_anomaly"] = works.get("anomaly_flag", pd.Series(0.0, index=works.index)).fillna(0.0)

    signal_cols = {
        "peer_amount": "sig_peer_amount",
        "peer_duration": "sig_peer_duration",
        "completion_risk": "sig_completion_risk",
        "conformance": "sig_conformance",
        "change_point": "sig_change_point",
        "anomaly": "sig_anomaly",
    }

    # Noisy-OR fusion with configured weights. Priority in [0,1).
    one_minus = pd.Series(1.0, index=works.index)
    for name, col in signal_cols.items():
        one_minus *= 1 - config.SIGNAL_WEIGHTS[name] * works[col].clip(0, 1)
    works["priority"] = 1 - one_minus

    # Confidence = number of independent signal FAMILIES firing (>0), not signals.
    fired = pd.DataFrame(index=works.index)
    for name, col in signal_cols.items():
        fired[config.SIGNAL_FAMILY[name]] = fired.get(
            config.SIGNAL_FAMILY[name], 0
        ) + (works[col] > 0).astype(int)
    families = (fired > 0).sum(axis=1)
    works["n_families"] = families

    works["band"] = pd.cut(
        families, bins=[-1, 0, 1, 2, 99], labels=["NONE", "LOW", "MEDIUM", "HIGH"]
    ).astype(str)

    # Exposure at risk (NOT loss, NOT spend): recommended amount weighted by completion risk.
    works["rs_exposure"] = works["recommended_amount"].astype("float").fillna(0.0) * works[
        "risk_score"
    ].clip(0, 1)
    # Audit-ROI: priority x exposure x corroboration. Each factor is traceable.
    works["audit_roi"] = works["priority"] * works["rs_exposure"] * (1 + works["n_families"])

    LOGGER.info("fusion bands: %s", works["band"].value_counts().to_dict())
    return works


# ----------------------------------------------------------------- case files & stats


def _evidence(row: pd.Series) -> list[dict]:
    ev = []
    if row["sig_peer_amount"] > 0:
        ev.append({
            "signal": "Peer amount", "family": "amount",
            "detail": f"Recommended amount at the {row['amount_pct']*100:.0f}th percentile of "
                      f"{int(row['peer_group_size'])} comparable works (robust z {row['amount_z']:.1f}).",
        })
    if row["sig_peer_duration"] > 0:
        ev.append({
            "signal": "Peer duration", "family": "duration",
            "detail": f"Open for longer than {row['open_duration_pct']*100:.0f}% of comparable "
                      f"works still in progress.",
        })
    if row["sig_completion_risk"] > 0:
        ev.append({
            "signal": "Completion risk", "family": "duration",
            "detail": f"Survival model: {row['risk_score']*100:.0f}% of comparable works have not "
                      f"completed within {config.RISK_HORIZON_DAYS} days.",
        })
    if row["sig_conformance"] > 0:
        flags = [n for n, f in [
            ("back-dated completion", row["is_backdated"]),
            ("completed without a sanction record", row["completed_without_sanction"]),
            ("completion date beyond the snapshot", row["is_future_dated"]),
            ("no recommendation record", row["is_orphan"]),
        ] if f]
        ev.append({"signal": "Lifecycle conformance", "family": "lifecycle",
                   "detail": "Lifecycle inconsistency: " + "; ".join(flags) + "."})
    if row["sig_change_point"] > 0:
        ev.append({"signal": "Behavioural change", "family": "behaviour",
                   "detail": f"Implementing agency's recommendation pattern shifted year-on-year "
                             f"(magnitude {row['change_point']:.0%}). A change point is a lead, not a finding."})
    if row.get("sig_anomaly", 0) > 0:
        ev.append({"signal": "Statistical outlier", "family": "multivariate",
                   "detail": "A trained anomaly detector (IsolationForest) flags this work's "
                             "amount-and-age profile as unusual against the national portfolio."})
    return ev


def build_case_file(row: pd.Series) -> dict:
    amt = None if pd.isna(row["recommended_amount"]) else float(row["recommended_amount"])
    return {
        "work_ref": row["work_ref"],
        "identity": {
            "work_ref": row["work_ref"],
            "description": (row["work_description"] or "")[:300] if isinstance(row["work_description"], str) else None,
            "state": row["state_name"],
            "constituency": row["constituency"],
            "implementing_agency": row["implementing_agency"],
            "mp_name": row["mp_name"],
            "recommended_amount": amt,
            "recommendation_date": None if pd.isna(row["recommendation_date"]) else row["recommendation_date"].date().isoformat(),
            "status": "Completed" if row["is_completed"] else ("Sanctioned" if row["is_sanctioned"] else "Recommended"),
        },
        "archetype": {"id": None if pd.isna(row["archetype_id"]) else int(row["archetype_id"]),
                      "label": row["archetype_label"]},
        "peer_context": {"level": row["peer_level"], "group_size": int(row["peer_group_size"]),
                         "amount_percentile": None if pd.isna(row["amount_pct"]) else round(float(row["amount_pct"]), 3)},
        "risk": {"completion_risk": round(float(row["risk_score"]), 3), "basis": row["risk_level_used"]},
        "exposure_rupees": round(float(row["rs_exposure"]), 0),
        "priority": round(float(row["priority"]), 4),
        "confidence_band": row["band"],
        "n_signal_families": int(row["n_families"]),
        "audit_roi": round(float(row["audit_roi"]), 0),
        "evidence": _evidence(row),
        "recommended_next_step": _recommend(row),
        "not_a_fraud_finding": True,
    }


def _recommend(row: pd.Series) -> str:
    if row["is_backdated"] or row["completed_without_sanction"] or row["is_future_dated"]:
        return "A human should check the lifecycle record with the District Authority — the stage dates are inconsistent."
    if row["sig_peer_amount"] > 0:
        return "A human should verify the scope and estimate for this work against its peers via the Implementing Agency."
    if row["sig_completion_risk"] > 0 or row["sig_peer_duration"] > 0:
        return "A human should request a progress update from the Implementing Agency on this long-running work."
    return "A human should review this work's evidence and decide whether a site verification is warranted."


def build_stats(works: pd.DataFrame, catalog: pd.DataFrame) -> dict:
    surfaced = works[works["band"].isin(["MEDIUM", "HIGH"])]
    national = {
        "total_works": int(len(works)),
        "completed": int(works["is_completed"].sum()),
        "open": int(works["is_open"].sum()),
        "states": int(works["state_name"].nunique()),
        "constituencies": int(works["constituency"].nunique()),
        "implementing_agencies": int(works["implementing_agency"].nunique()),
        "total_recommended_rupees": float(works["recommended_amount"].sum()),
        "total_exposure_rupees": float(works["rs_exposure"].sum()),
        "surfaced_leads": int(len(surfaced)),
        "bands": works["band"].value_counts().to_dict(),
    }
    by_state = (
        works.groupby("state_name")
        .agg(
            works=("work_ref", "size"),
            exposure=("rs_exposure", "sum"),
            leads=("band", lambda s: int(s.isin(["MEDIUM", "HIGH"]).sum())),
        )
        .reset_index()
        .sort_values("exposure", ascending=False)
    )
    archetypes = catalog.head(20).to_dict("records")
    return {"national": national, "by_state": by_state.to_dict("records"), "archetypes": archetypes}


# --------------------------------------------------------------------------- run


def run(artifacts_dir: Path | None = None) -> pd.DataFrame:
    out = config.ARTIFACTS if artifacts_dir is None else artifacts_dir
    out.mkdir(parents=True, exist_ok=True)

    works = pd.read_parquet(config.DATA_INTERIM / "works.parquet")
    stages = pd.read_parquet(config.DATA_INTERIM / "stages.parquet")
    LOGGER.info("loaded %s works", f"{len(works):,}")

    works = add_activity_category(works)
    works, catalog = add_archetypes(works)
    works = add_features(works, stages)
    works = add_peer_comparison(works)
    works = add_completion_risk(works)
    works = add_change_points(works)
    works = add_anomaly(works)
    works = add_fusion(works)

    # Worklist: everything with >=2 families (the corroboration rule), ranked by audit-ROI.
    worklist = works[works["band"].isin(["MEDIUM", "HIGH"])].sort_values(
        "audit_roi", ascending=False
    )
    case_files = [build_case_file(r) for _, r in worklist.iterrows()]

    works.to_parquet(out / "works_scored.parquet", index=False)
    (out / "case_files.json").write_text(json.dumps(case_files, default=str), encoding="utf-8")
    catalog.to_parquet(out / "archetypes.parquet", index=False)
    (out / "stats.json").write_text(
        json.dumps(build_stats(works, catalog), default=str), encoding="utf-8"
    )
    LOGGER.info("wrote %s case files; artifacts in %s", f"{len(case_files):,}", out)
    return works


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    run()
