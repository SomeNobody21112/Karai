"""Entity behavioural fingerprints: what an implementing agency's work looks like over time.

Every other signal in this system scores a *row*. This one scores an *actor*. That is the
whole point: a hundred works can each sit comfortably inside their peer norms while the
agency that produced them changes what it does — the value it works at, the kinds of work
it takes on, the rate at which it finishes them. No row-level score can see that, because
the change is not in any row.

The Constitution (§5 UVP-4) names eight dimensions. All eight are computed here:

    volume              how many works, per period
    value               the amount distribution — median, spread, upper tail
    duration            how long completed works took — median and upper tail
    archetype_mix       which learned work-types, as a distribution over archetypes
    completion_rate     the share that reached completion
    anomaly_rate        the share carrying a work-level peer signal
    templating_rate     the share whose description is near-identical to another
    backdating_rate     the share whose dates run backwards

**One coupling is deliberately broken.** `anomaly_rate` and `templating_rate` are built from
other signal families, so a change-point detected on them is not independent evidence — it
is the same evidence counted twice, which is exactly what noisy-OR fusion must never be fed
(§6, §5 UVP-6). `FUSION_SAFE` names the six dimensions that may reach the fusion layer.
All eight are shown to a human, because a human is allowed to notice a correlation.

Granularity is the implementing agency by default — §21 Q3 records this as an open team
decision, and this module settles it by making it a parameter with a stated default rather
than a hidden assumption. The agency is the actor that executes; an MP recommends.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)

#: The eight dimensions §5 UVP-4 specifies, in the order they are reported.
DIMENSIONS: tuple[str, ...] = (
    "volume", "value_median", "value_iqr", "value_p90",
    "duration_median", "duration_p90", "archetype_entropy", "archetype_top_share",
    "completion_rate", "anomaly_rate", "templating_rate", "backdating_rate",
)

#: Dimensions that may feed evidence fusion. `anomaly_rate` and `templating_rate` are
#: derived from other signal families; letting a change in them raise a work's fused
#: priority would corroborate a signal with itself.
FUSION_SAFE: tuple[str, ...] = (
    "volume", "value_median", "value_iqr", "value_p90",
    "duration_median", "duration_p90", "archetype_entropy", "archetype_top_share",
    "completion_rate", "backdating_rate",
)

#: A period needs enough works for a median and a distribution to mean anything. Below
#: this the numbers are noise wearing a statistic's clothes.
MIN_WORKS_PER_PERIOD = 8

#: Fewer periods than this and there is no "before" to compare an "after" against.
MIN_PERIODS = 6

#: Description similarity at or above which two works count as the same template.
TEMPLATING_SIMILARITY = 0.95

#: Entity columns this module knows how to profile, and what each one is.
ENTITIES: dict[str, str] = {
    "implementing_agency": "Implementing agency",
    "constituency": "Constituency",
    "state_name": "State",
}

DEFAULT_ENTITY = "implementing_agency"
DEFAULT_FREQ = "Q"


def _periods(works: pd.DataFrame, freq: str) -> pd.Series:
    dates = pd.to_datetime(works["recommendation_date"], errors="coerce")
    return dates.dt.to_period(freq)


def _entropy(shares: np.ndarray) -> float:
    """Shannon entropy in bits, over a normalised mix.

    High entropy means the agency builds many kinds of thing; low entropy means it builds
    one. Neither is good or bad — a district that only builds roads is not suspicious. It
    is the *change* that carries information.
    """
    nonzero = shares[shares > 0]
    if nonzero.size == 0:
        return 0.0
    return float(-(nonzero * np.log2(nonzero)).sum())


def profiles(works: pd.DataFrame, entity: str = DEFAULT_ENTITY,
             freq: str = DEFAULT_FREQ,
             min_works: int = MIN_WORKS_PER_PERIOD) -> pd.DataFrame:
    """The behavioural vector for every entity, in every period it was active enough.

    One row per (entity, period). Periods with too few works are dropped rather than
    reported thinly — a median of three works is not a distribution.
    """
    if entity not in works.columns:
        raise ValueError(f"no such entity column: {entity}")

    frame = works.copy()
    frame["period"] = _periods(frame, freq)
    frame = frame.dropna(subset=[entity, "period"])

    amount = frame["recommended_amount"].astype(float)
    frame["_amount"] = amount
    frame["_duration"] = pd.to_numeric(frame.get("duration_days"), errors="coerce")
    frame["_completed"] = frame["is_completed"].fillna(False).astype(bool)
    frame["_backdated"] = frame.get("is_backdated", False)
    frame["_backdated"] = frame["_backdated"].fillna(False).astype(bool)

    # A work-level peer signal fired: amount, duration, or the multivariate cross-check.
    signal_columns = [c for c in ("sig_peer_amount", "sig_peer_duration", "sig_anomaly")
                      if c in frame.columns]
    if signal_columns:
        frame["_anomalous"] = (frame[signal_columns].fillna(0.0) > 0).any(axis=1)
    else:
        frame["_anomalous"] = False

    similarity = pd.to_numeric(frame.get("duplicate_similarity"), errors="coerce")
    frame["_templated"] = (similarity.fillna(0.0) >= TEMPLATING_SIMILARITY)

    # Completed-only durations: an unfinished work has no duration, and treating its
    # age as one is the survivorship bias this project exists to avoid.
    frame.loc[~frame["_completed"], "_duration"] = np.nan

    grouped = frame.groupby([entity, "period"], observed=True)
    built = grouped.agg(
        volume=("work_ref", "size"),
        value_median=("_amount", "median"),
        value_p25=("_amount", lambda s: s.quantile(0.25)),
        value_p75=("_amount", lambda s: s.quantile(0.75)),
        value_p90=("_amount", lambda s: s.quantile(0.90)),
        duration_median=("_duration", "median"),
        duration_p90=("_duration", lambda s: s.quantile(0.90)),
        completion_rate=("_completed", "mean"),
        anomaly_rate=("_anomalous", "mean"),
        templating_rate=("_templated", "mean"),
        backdating_rate=("_backdated", "mean"),
    ).reset_index()

    built["value_iqr"] = built["value_p75"] - built["value_p25"]
    built = built.drop(columns=["value_p25", "value_p75"])

    mix = archetype_mix(frame, entity, freq="", min_works=0, already_periodised=True)
    if not mix.empty:
        shares = mix.drop(columns=[entity, "period"]).to_numpy(dtype=float)
        mix_summary = pd.DataFrame({
            entity: mix[entity],
            "period": mix["period"],
            "archetype_entropy": [_entropy(row) for row in shares],
            "archetype_top_share": shares.max(axis=1) if shares.size else [],
        })
        built = built.merge(mix_summary, on=[entity, "period"], how="left")
    else:
        built["archetype_entropy"] = np.nan
        built["archetype_top_share"] = np.nan

    built = built[built["volume"] >= min_works].copy()
    built["entity_type"] = ENTITIES.get(entity, entity)
    built = built.rename(columns={entity: "entity"})
    built = built.sort_values(["entity", "period"]).reset_index(drop=True)

    LOGGER.info(
        "behaviour: %s (entity, period) profiles across %s %ss (>= %s works each)",
        f"{len(built):,}", f"{built['entity'].nunique():,}",
        ENTITIES.get(entity, entity).lower(), min_works,
    )
    return built


def archetype_mix(works: pd.DataFrame, entity: str = DEFAULT_ENTITY,
                  freq: str = DEFAULT_FREQ, min_works: int = MIN_WORKS_PER_PERIOD,
                  already_periodised: bool = False) -> pd.DataFrame:
    """What kinds of work an entity did in a period, as a distribution over archetypes.

    Kept as the full vector rather than collapsed to a summary, because the interesting
    comparison is between two whole distributions — an agency that swaps roads for
    community halls has changed even when its volume, value and entropy all hold steady.
    """
    if "archetype_id" not in works.columns:
        return pd.DataFrame()

    frame = works if already_periodised else works.assign(period=_periods(works, freq))
    frame = frame.dropna(subset=[entity, "period", "archetype_id"])
    if frame.empty:
        return pd.DataFrame()

    counts = (
        frame.pivot_table(index=[entity, "period"], columns="archetype_id",
                          values="work_ref", aggfunc="size", fill_value=0, observed=True)
    )
    if min_works:
        counts = counts[counts.sum(axis=1) >= min_works]
    if counts.empty:
        return pd.DataFrame()

    shares = counts.div(counts.sum(axis=1), axis=0)
    shares.columns = [f"arch_{int(c)}" for c in shares.columns]
    return shares.reset_index()


def summarise(profile_frame: pd.DataFrame) -> dict:
    """Portfolio-level description of the fingerprints, for the transparency screen."""
    if profile_frame.empty:
        return {"entities": 0, "profiles": 0, "dimensions": list(DIMENSIONS)}
    per_entity = profile_frame.groupby("entity")["period"].nunique()
    return {
        "entities": int(profile_frame["entity"].nunique()),
        "profiles": int(len(profile_frame)),
        "entity_type": profile_frame["entity_type"].iloc[0],
        "periods_median": float(per_entity.median()),
        "entities_with_enough_history": int((per_entity >= MIN_PERIODS).sum()),
        "dimensions": list(DIMENSIONS),
        "fusion_safe_dimensions": list(FUSION_SAFE),
        "min_works_per_period": MIN_WORKS_PER_PERIOD,
        "note": (
            "A behavioural fingerprint describes an actor, not a work. Anomaly rate and "
            "templating rate are shown but excluded from evidence fusion: they are built "
            "from other signal families, and corroborating a signal with itself is not "
            "corroboration."
        ),
    }
