"""Temporal intelligence: trends, spikes, drops, emerging and declining work types.

Every series here is built from **recommendation-time** fields only. Completion-derived
series (completion rate, delay) are censoring-contaminated — recent periods have not had
time to complete — so including them makes every recent quarter look like it "changed".
That mistake produces convincing nonsense and is deliberately avoided.

Classification vocabulary, shown in the UI:
    NORMAL           — within the usual range for this series
    EMERGING         — sustained growth from a small base
    SUDDEN_CHANGE    — a single-period spike or drop beyond the series' own volatility
    PERSISTENT_CHANGE— the level shifted and stayed shifted
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from mplads import config

LOGGER = logging.getLogger(__name__)

MIN_PERIODS = 6
SPIKE_Z = 2.5
PERSISTENT_RATIO = 0.35


def _monthly(works: pd.DataFrame) -> pd.DataFrame:
    frame = works.dropna(subset=["recommendation_date"]).copy()
    frame["period"] = frame["recommendation_date"].dt.to_period("M").dt.to_timestamp()
    return frame


def national_series(works: pd.DataFrame) -> pd.DataFrame:
    """Monthly national volume and median recommended amount."""
    frame = _monthly(works)
    series = (
        frame.groupby("period")
        .agg(
            works=("work_ref", "size"),
            median_amount=("recommended_amount", "median"),
            total_amount=("recommended_amount", "sum"),
        )
        .reset_index()
    )
    # The final period is usually partial (the extract stops mid-month) and would read as a
    # collapse in volume for everyone. Drop it rather than explain it away.
    return series.iloc[:-1] if len(series) > 1 else series


def classify_series(values: pd.Series) -> tuple[str, str]:
    """Label a numeric series and explain the label in one sentence."""
    clean = values.dropna().astype(float)
    if len(clean) < MIN_PERIODS:
        return "INSUFFICIENT_HISTORY", f"Only {len(clean)} periods of history available."

    array = clean.to_numpy()
    baseline, recent = array[:-3], array[-3:]
    mu, sigma = baseline.mean(), baseline.std() or 1e-9

    z_last = (array[-1] - mu) / sigma
    shift = (recent.mean() - mu) / (abs(mu) + 1e-9)

    if abs(shift) >= PERSISTENT_RATIO and abs(recent.mean() - mu) > sigma:
        direction = "higher" if shift > 0 else "lower"
        return (
            "PERSISTENT_CHANGE",
            f"The recent level is {abs(shift) * 100:.0f}% {direction} than the historical "
            f"average and has stayed there for three periods.",
        )
    if abs(z_last) >= SPIKE_Z:
        kind = "spike" if z_last > 0 else "drop"
        return (
            "SUDDEN_CHANGE",
            f"The latest period is a {kind} of {abs(z_last):.1f} standard deviations "
            f"against this series' own history.",
        )
    if shift > 0.20 and baseline.mean() < np.median(array):
        return "EMERGING", f"Growing steadily from a small base (+{shift * 100:.0f}%)."
    return "NORMAL", "Within the usual range for this series."


def entity_trends(works: pd.DataFrame, key: str, label: str) -> pd.DataFrame:
    """Per-entity monthly volume trend with a classification and an explanation."""
    frame = _monthly(works).dropna(subset=[key])
    counts = (
        frame.groupby([key, "period"])
        .agg(works=("work_ref", "size"), median_amount=("recommended_amount", "median"))
        .reset_index()
    )
    rows = []
    for entity, group in counts.groupby(key):
        group = group.sort_values("period")
        if len(group) < MIN_PERIODS:
            continue
        state, why = classify_series(group["works"])
        rows.append(
            {
                "entity_type": label,
                "entity": entity,
                "periods": len(group),
                "total_works": int(group["works"].sum()),
                "latest_works": int(group["works"].iloc[-1]),
                "mean_works": round(float(group["works"].mean()), 1),
                "classification": state,
                "explanation": why,
            }
        )
    result = pd.DataFrame(rows)
    if not result.empty:
        LOGGER.info(
            "trends[%s]: %s entities — %s",
            label,
            f"{len(result):,}",
            result["classification"].value_counts().to_dict(),
        )
    return result


def archetype_radar(works: pd.DataFrame) -> pd.DataFrame:
    """Emerging / declining work types — the 'Emerging Public Works Radar'.

    Compares each archetype's share of works in the most recent 12 months against its share
    in the preceding period. Share, not raw count, so overall scheme growth does not make
    everything look like it is emerging.
    """
    frame = _monthly(works).dropna(subset=["archetype_id"])
    if frame.empty:
        return pd.DataFrame()

    latest = frame["period"].max()
    cutoff = latest - pd.DateOffset(months=12)
    recent = frame[frame["period"] > cutoff]
    earlier = frame[frame["period"] <= cutoff]
    if earlier.empty or recent.empty:
        return pd.DataFrame()

    def share(subset: pd.DataFrame) -> pd.Series:
        counts = subset.groupby("archetype_id").size()
        return counts / counts.sum()

    recent_share, earlier_share = share(recent), share(earlier)
    labels = works.dropna(subset=["archetype_id"]).groupby("archetype_id")["archetype_label"].first()

    combined = pd.DataFrame(
        {"recent_share": recent_share, "earlier_share": earlier_share}
    ).fillna(0.0)
    combined["label"] = labels
    combined["recent_works"] = recent.groupby("archetype_id").size()
    combined["delta"] = combined["recent_share"] - combined["earlier_share"]
    combined["growth"] = combined["delta"] / (combined["earlier_share"] + 1e-6)

    def state(row: pd.Series) -> str:
        if row["earlier_share"] < 0.002 and row["recent_share"] > 0.005:
            return "EMERGING"
        if row["growth"] > 0.5:
            return "GROWING"
        if row["growth"] < -0.4:
            return "DECLINING"
        return "STABLE"

    combined["classification"] = combined.apply(state, axis=1)
    combined = combined.reset_index().sort_values("delta", ascending=False)
    LOGGER.info("radar: %s", combined["classification"].value_counts().to_dict())
    return combined


def build(works: pd.DataFrame) -> dict:
    """Everything the temporal dashboard needs."""
    national = national_series(works)
    volume_state, volume_why = classify_series(national["works"])
    amount_state, amount_why = classify_series(national["median_amount"])

    agencies = entity_trends(works, "implementing_agency", "Implementing agency")
    states = entity_trends(works, "state_name", "State")
    radar = archetype_radar(works)

    changed = agencies[agencies["classification"].isin(["SUDDEN_CHANGE", "PERSISTENT_CHANGE"])]

    return {
        "national_series": [
            {
                "period": p.strftime("%Y-%m"),
                "works": int(w),
                "median_amount": float(m) if pd.notna(m) else None,
            }
            for p, w, m in zip(
                national["period"], national["works"], national["median_amount"]
            )
        ],
        "national_volume": {"classification": volume_state, "explanation": volume_why},
        "national_amount": {"classification": amount_state, "explanation": amount_why},
        "agency_trends": changed.head(50).to_dict("records"),
        "state_trends": states.to_dict("records"),
        "archetype_radar": radar.head(25).to_dict("records"),
        "counts": {
            "agencies_analysed": int(len(agencies)),
            "agencies_changed": int(len(changed)),
            "states_analysed": int(len(states)),
        },
        "method_note": (
            "All series use recommendation-time fields only. Completion-derived series are "
            "censoring-contaminated and would make every recent period appear to change."
        ),
    }
