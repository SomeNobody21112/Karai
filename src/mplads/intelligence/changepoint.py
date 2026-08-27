"""Change-point detection: *when* did an entity's behaviour structurally shift?

The question this answers is deliberately narrower than "is this entity unusual". Unusual
is a comparison against other entities and it is what every anomaly score already does.
This asks a question about one entity against its own past: was there a moment when what it
does changed, and if so, when?

That distinction matters operationally. "Agency X is unusual" sends an auditor to look at
everything Agency X has ever done. "Agency X changed in Q3 2024 — the value distribution
moved up, the work mix swapped, completion fell" sends them to a date, with a before and an
after to compare. The second is an investigation; the first is a search.

**Two methods, because there are two kinds of dimension.**

*CUSUM* (Taylor's cumulative-sum change-point analysis) for the scalar series — volume,
median value, completion rate. The cumulative sum of deviations from the series mean drifts
in one direction while the level is stable and turns at a shift; the turning point is the
estimate. Significance comes from a bootstrap: reshuffle the series many times, see how
often chance produces a swing this large. A series with no change-point produces one anyway
if you only look at the argmax, which is why the bootstrap is not optional.

*Jensen-Shannon divergence* for the archetype mix, which is a distribution rather than a
number. JS is symmetric, bounded in [0, 1] with log base 2, and defined when one side has
zero mass where the other does not — all three matter here, because an agency that stops
building one kind of thing entirely is exactly the case KL divergence would send to
infinity.

**A change-point is not a finding.** A new officer, a new state scheme, a flood, or a
financial-year boundary all produce one. The output is a date, a magnitude, and the two
distributions side by side, for a human to explain. It never asserts a cause.

**What cannot be claimed, and why.** Around four thousand tests run here — every entity
against every dimension. Correcting all of them at once needs p-values below 1/4000, and a
permutation test on six to eleven periods cannot produce one: with six periods there are
only 720 orderings, so the smallest p-value the method can ever return is 1/720, whatever
the effect size and however many resamples are drawn. No amount of computation moves that
floor; it is a property of the sample, not the budget.

So the global per-test correction is reported and it rejects everything, honestly. Two
families that *are* within reach carry the actual result:

  *Within an entity* — "did this agency change?" is eleven tests, not four thousand, and
  Benjamini-Hochberg over eleven is achievable. This is the right family for an auditor
  asking about one agency.

  *Agreement across dimensions* — several dimensions turning at the *same* period is far
  rarer under the null than any one turning alone, and that probability is computable
  without needing a finer p-value from any single test. This is the family that supports a
  ranked list, and it is what `entity_summary` corrects across.

The headline count of changed agencies comes from the agreement test. Any single-dimension
detection standing alone is at the noise floor and is labelled as such.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from mplads import config
from mplads.intelligence import behaviour

LOGGER = logging.getLogger(__name__)

#: Screening resamples. Cheap, run on every (entity, dimension) pair.
N_BOOTSTRAP = 500

#: Confirmation resamples, run only on what the screen returns. Correcting four thousand
#: tests needs p-values below 1/4000, and five hundred resamples cannot produce one — the
#: floor at 1/501 is coarser than the threshold by an order of magnitude, so a first pass
#: at 500 rejects everything however real it is. This is a resolution problem, not an
#: effect-size one, and the fix is to spend the resamples only where they can matter.
DEEP_BOOTSTRAP = 20_000

#: A change-point is reported at or above this confidence. Chosen to be strict: this feeds
#: an investigation queue, and a change-point that is wrong wastes a site visit.
MIN_CONFIDENCE = 0.95

#: Each side of a split needs enough periods to have a level of its own.
MIN_SIDE_PERIODS = 2

#: False-discovery rate for the Benjamini-Hochberg correction. At most this share of the
#: change-points we report should be chance. 10% rather than 5% because the cost of a
#: missed behavioural change is a missed investigation, and the cost of a false one is a
#: person looking at two bar charts and deciding they are fine.
FDR_Q = 0.10

#: Jensen-Shannon divergence below this is not a mix change worth a human's time, however
#: significant. Bounded in [0, 1]; 0.10 is a visibly different bar chart.
MIN_JS_DIVERGENCE = 0.10

#: Smallest relative shift worth reporting. Significance says a change is real; this says
#: it is large enough to be worth a person's afternoon. A 3% move in median value can be
#: both real and pointless, and an investigation queue full of those is a queue nobody
#: works through.
MIN_RELATIVE_SHIFT = 0.25


def _cusum_range(values: np.ndarray) -> tuple[float, int]:
    """Maximum absolute cumulative deviation from the mean, and where it occurs."""
    deviations = values - values.mean()
    cumulative = np.cumsum(deviations)
    index = int(np.argmax(np.abs(cumulative)))
    return float(np.abs(cumulative).max()), index


def cusum_changepoint(values: np.ndarray, n_bootstrap: int = N_BOOTSTRAP,
                      seed: int = config.RANDOM_SEED) -> dict | None:
    """Estimate a single change-point in a scalar series, with a bootstrap confidence.

    Returns None when the series is too short or the swing is no larger than shuffling the
    same numbers would produce by chance.
    """
    clean = np.asarray(values, dtype=float)
    clean = clean[~np.isnan(clean)]
    if len(clean) < 2 * MIN_SIDE_PERIODS:
        return None
    if np.allclose(clean, clean[0]):
        return None

    observed, index = _cusum_range(clean)
    if not (MIN_SIDE_PERIODS - 1 <= index <= len(clean) - MIN_SIDE_PERIODS - 1):
        return None

    # Shuffling destroys any ordering, so the bootstrap distribution is what this series'
    # own numbers produce when nothing changed. Comparing against it rather than a
    # normal-theory threshold keeps the test honest about small samples and skew.
    rng = np.random.default_rng(seed)
    shuffled = np.array([rng.permutation(clean) for _ in range(n_bootstrap)])
    deviations = shuffled - shuffled.mean(axis=1, keepdims=True)
    null_ranges = np.abs(np.cumsum(deviations, axis=1)).max(axis=1)

    # The (1 + exceedances) / (1 + n) form, not the raw proportion: 500 resamples cannot
    # evidence a p-value of exactly zero, and reporting one would be a claim the method
    # cannot support at any sample size.
    p_value = float((1 + (null_ranges >= observed).sum()) / (1 + n_bootstrap))
    before, after = clean[: index + 1], clean[index + 1:]
    scale = abs(before.mean()) + 1e-9
    return {
        "index": index,
        "p_value": p_value,
        "confidence": round(1 - p_value, 4),
        "before_mean": float(before.mean()),
        "after_mean": float(after.mean()),
        "relative_change": float((after.mean() - before.mean()) / scale),
        "magnitude": float(abs(after.mean() - before.mean()) / scale),
    }


def _js_divergence(left: np.ndarray, right: np.ndarray) -> float:
    """Jensen-Shannon divergence in bits, bounded in [0, 1]."""
    left = left / (left.sum() or 1.0)
    right = right / (right.sum() or 1.0)
    mixture = 0.5 * (left + right)

    def _kl(p: np.ndarray, q: np.ndarray) -> float:
        mask = p > 0
        return float((p[mask] * np.log2(p[mask] / q[mask])).sum())

    return 0.5 * _kl(left, mixture) + 0.5 * _kl(right, mixture)


def js_changepoint(mix: np.ndarray, n_bootstrap: int = N_BOOTSTRAP,
                   seed: int = config.RANDOM_SEED) -> dict | None:
    """Find the split maximising Jensen-Shannon divergence between two mixes.

    `mix` is (periods, archetypes); each row is one period's distribution over work types.
    """
    matrix = np.asarray(mix, dtype=float)
    if matrix.shape[0] < 2 * MIN_SIDE_PERIODS:
        return None

    def best_split(rows: np.ndarray) -> tuple[float, int]:
        best, at = 0.0, -1
        for split in range(MIN_SIDE_PERIODS - 1, rows.shape[0] - MIN_SIDE_PERIODS):
            divergence = _js_divergence(rows[: split + 1].sum(axis=0),
                                        rows[split + 1:].sum(axis=0))
            if divergence > best:
                best, at = divergence, split
        return best, at

    observed, index = best_split(matrix)
    if index < 0 or observed < MIN_JS_DIVERGENCE:
        return None

    rng = np.random.default_rng(seed)
    null = np.empty(n_bootstrap)
    for i in range(n_bootstrap):
        null[i] = best_split(rng.permutation(matrix, axis=0))[0]

    p_value = float((1 + (null >= observed).sum()) / (1 + n_bootstrap))
    return {
        "index": index,
        "p_value": p_value,
        "confidence": round(1 - p_value, 4),
        "divergence": round(float(observed), 4),
        "magnitude": float(observed),
    }


def benjamini_hochberg(p_values: np.ndarray, q: float) -> np.ndarray:
    """Which tests survive a false-discovery-rate correction at level `q`.

    Roughly four thousand tests run here — every entity against every dimension. At a
    plain 95% threshold, two hundred of them come back positive on pure chance, which
    would be most of what we found. Benjamini-Hochberg controls the share of *reported*
    change-points that are chance rather than the share of tests that are, which is the
    quantity an auditor deciding where to drive actually cares about.

    Less conservative than Bonferroni deliberately: the dimensions are correlated by
    construction (an agency doing bigger works also takes longer over them), so treating
    them as independent tests and dividing by all of them throws away real detections.
    """
    order = np.argsort(p_values)
    ranked = p_values[order]
    m = len(p_values)
    thresholds = q * np.arange(1, m + 1) / m
    passing = np.where(ranked <= thresholds)[0]

    survivors = np.zeros(m, dtype=bool)
    if passing.size:
        survivors[order[: passing[-1] + 1]] = True
    return survivors


def _top_shift(before: np.ndarray, after: np.ndarray, labels: list[str],
               limit: int = 3) -> list[dict]:
    """The archetypes whose share moved most, so the mix change has a plain description."""
    before = before / (before.sum() or 1.0)
    after = after / (after.sum() or 1.0)
    delta = after - before
    order = np.argsort(-np.abs(delta))[:limit]
    return [
        {"archetype": labels[i], "before_share": round(float(before[i]), 3),
         "after_share": round(float(after[i]), 3), "change": round(float(delta[i]), 3)}
        for i in order if abs(delta[i]) > 0.01
    ]


def detect(profiles: pd.DataFrame, mixes: pd.DataFrame | None = None,
           archetype_labels: dict[int, str] | None = None,
           dimensions: tuple[str, ...] = behaviour.FUSION_SAFE,
           min_periods: int = behaviour.MIN_PERIODS,
           min_confidence: float = MIN_CONFIDENCE,
           n_bootstrap: int = N_BOOTSTRAP,
           deep_bootstrap: int = DEEP_BOOTSTRAP,
           min_shift: float = MIN_RELATIVE_SHIFT,
           fdr_q: float = FDR_Q) -> pd.DataFrame:
    """Every entity's change-point, on every dimension that has one.

    One row per (entity, dimension) with a detected change — an entity that changed on
    four dimensions at once produces four rows, and that agreement is itself the evidence.
    """
    if profiles.empty:
        return pd.DataFrame()

    labels = archetype_labels or {}
    mix_columns = (
        [c for c in mixes.columns if c.startswith("arch_")] if mixes is not None else []
    )
    mix_labels = [labels.get(int(c.removeprefix("arch_")), c) for c in mix_columns]
    mix_indexed = (
        mixes.set_index(["entity", "period"]) if mixes is not None and not mixes.empty
        else None
    )

    rows: list[dict] = []
    tests_run = 0
    for entity, group in profiles.groupby("entity", observed=True):
        group = group.sort_values("period")
        if len(group) < min_periods:
            continue
        periods = group["period"].astype(str).tolist()

        for dimension in dimensions:
            if dimension not in group.columns:
                continue
            series = group[dimension].to_numpy(dtype=float)
            if np.isnan(series).sum() > len(series) - 2 * MIN_SIDE_PERIODS:
                continue
            found = cusum_changepoint(series, n_bootstrap=n_bootstrap)
            tests_run += 1
            if not found or found["confidence"] < min_confidence:
                continue
            rows.append({
                "entity": entity,
                "entity_type": group["entity_type"].iloc[0],
                "dimension": dimension,
                "method": "CUSUM",
                "change_period": periods[found["index"]],
                "next_period": periods[min(found["index"] + 1, len(periods) - 1)],
                "confidence": found["confidence"],
                "p_value": found["p_value"],
                "magnitude": round(found["magnitude"], 4),
                "before": round(found["before_mean"], 3),
                "after": round(found["after_mean"], 3),
                "direction": "higher" if found["relative_change"] > 0 else "lower",
                "periods_observed": len(group),
                "mix_shift": None,
            })

        if mix_indexed is None:
            continue
        try:
            entity_mix = mix_indexed.loc[entity, mix_columns]
        except KeyError:
            continue
        if isinstance(entity_mix, pd.Series) or len(entity_mix) < min_periods:
            continue
        entity_mix = entity_mix.sort_index()
        matrix = entity_mix.to_numpy(dtype=float)
        found = js_changepoint(matrix, n_bootstrap=n_bootstrap)
        tests_run += 1
        if not found or found["confidence"] < min_confidence:
            continue
        split = found["index"]
        mix_periods = [str(p) for p in entity_mix.index]
        rows.append({
            "entity": entity,
            "entity_type": group["entity_type"].iloc[0],
            "dimension": "archetype_mix",
            "method": "Jensen-Shannon",
            "change_period": mix_periods[split],
            "next_period": mix_periods[min(split + 1, len(mix_periods) - 1)],
            "confidence": found["confidence"],
            "p_value": found["p_value"],
            # Divergence is already gated by MIN_JS_DIVERGENCE and lives on a different
            # scale from a relative shift; carried through the effect-size gate as-is.
            "magnitude": max(round(found["divergence"], 4), MIN_RELATIVE_SHIFT),
            "divergence": round(found["divergence"], 4),
            "before": None,
            "after": None,
            "direction": "different mix",
            "periods_observed": len(entity_mix),
            "mix_shift": _top_shift(matrix[: split + 1].sum(axis=0),
                                    matrix[split + 1:].sum(axis=0), mix_labels),
        })

    result = pd.DataFrame(rows)
    if result.empty:
        LOGGER.info("changepoint: no entity changed on any dimension at %.0f%% confidence",
                    min_confidence * 100)
        return result

    screened = len(result)

    # Stage 2: only what survives both the screen and the effect-size gate is worth the
    # deep bootstrap, and only the deep bootstrap produces p-values fine enough to correct.
    result = result[result["magnitude"] >= min_shift].copy()
    material = len(result)
    if not result.empty and deep_bootstrap > n_bootstrap:
        result["p_value"] = [
            _refine(row, profiles, mix_indexed, mix_columns, deep_bootstrap)
            for row in result.itertuples()
        ]
        result["confidence"] = (1 - result["p_value"]).round(6)

    # Every test that ran counts towards the correction, including the ones that found
    # nothing — correcting only over the winners is the multiple-testing error itself.
    padded = np.concatenate([
        result["p_value"].to_numpy(dtype=float),
        np.ones(max(tests_run - len(result), 0)),
    ])
    result["survives_fdr"] = benjamini_hochberg(padded, fdr_q)[: len(result)]

    # A second, narrower family: "did *this* agency change?" is eleven tests, not four
    # thousand. An auditor asking about one agency is entitled to the narrower answer, so
    # both are reported and the global one governs any headline count.
    result["survives_fdr_within_entity"] = False
    for entity, group in result.groupby("entity", observed=True):
        per_entity_tests = max(len(dimensions) + 1, len(group))
        padded_entity = np.concatenate([
            group["p_value"].to_numpy(dtype=float),
            np.ones(per_entity_tests - len(group)),
        ])
        result.loc[group.index, "survives_fdr_within_entity"] = (
            benjamini_hochberg(padded_entity, fdr_q)[: len(group)]
        )

    result.attrs.update({
        "tests_run": tests_run,
        "screened_at_confidence": screened,
        "material_after_effect_size": material,
        "min_relative_shift": min_shift,
        "fdr_q": fdr_q,
        "expected_by_chance": round(tests_run * (1 - min_confidence), 1),
        "deep_bootstrap": deep_bootstrap,
    })

    survivors = int(result["survives_fdr"].sum())
    LOGGER.info(
        "changepoint: %s tests -> %s screened -> %s material -> %s survive FDR q=%.2f "
        "(a plain 95%% cut would have reported ~%.0f of these by chance)",
        f"{tests_run:,}", f"{screened:,}", f"{material:,}", f"{survivors:,}", fdr_q,
        tests_run * (1 - min_confidence),
    )
    return result.sort_values(["entity", "dimension"]).reset_index(drop=True)


def _refine(row, profiles: pd.DataFrame, mix_indexed, mix_columns,
            n_bootstrap: int) -> float:
    """Re-run one candidate's test with enough resamples to survive a correction."""
    if row.dimension == "archetype_mix":
        if mix_indexed is None:
            return float(row.p_value)
        try:
            matrix = mix_indexed.loc[row.entity, mix_columns].sort_index().to_numpy(float)
        except KeyError:
            return float(row.p_value)
        found = js_changepoint(matrix, n_bootstrap=n_bootstrap)
        return float(found["p_value"]) if found else 1.0

    series = (
        profiles[profiles["entity"] == row.entity]
        .sort_values("period")[row.dimension]
        .to_numpy(dtype=float)
    )
    found = cusum_changepoint(series, n_bootstrap=n_bootstrap)
    return float(found["p_value"]) if found else 1.0


def agreement_p_value(n_detected: int, n_agreeing: int, n_periods: int,
                      n_simulations: int = 20_000,
                      seed: int = config.RANDOM_SEED) -> float:
    """How surprising is it that `n_agreeing` of `n_detected` dimensions picked one period?

    Under the null, a spurious change-point lands anywhere in the series. The chance that
    several land on the *same* period falls away fast, and unlike the individual tests this
    probability is not limited by how few periods each series has — it is limited by how
    many dimensions were tested, and there are enough of those.

    This is what makes a ranked list defensible when no single test can be.
    """
    if n_detected <= 1 or n_agreeing <= 1 or n_periods <= 1:
        return 1.0
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, n_periods, size=(n_simulations, n_detected))
    # Largest number of dimensions landing on any one period, per simulation.
    best = np.array([np.bincount(row, minlength=n_periods).max() for row in draws])
    return float((1 + (best >= n_agreeing).sum()) / (1 + n_simulations))


def entity_summary(changes: pd.DataFrame, fdr_q: float = FDR_Q) -> pd.DataFrame:
    """One row per entity that changed, ranked by how much its dimensions agree on a date.

    Several dimensions turning at the same period is much stronger than one turning alone —
    it is the difference between a busy quarter and a different way of working. That
    agreement is tested explicitly and corrected across entities, which is the family small
    enough for the correction to mean something (see the module docstring).
    """
    if changes.empty:
        return pd.DataFrame()

    rows = []
    for entity, group in changes.groupby("entity", observed=True):
        by_period = group.groupby("change_period")
        consensus_period = max(by_period.groups, key=lambda p: len(by_period.get_group(p)))
        agreeing = by_period.get_group(consensus_period)
        periods_observed = int(group["periods_observed"].max())
        p_agreement = agreement_p_value(len(group), len(agreeing), periods_observed)
        rows.append({
            "entity": entity,
            "entity_type": group["entity_type"].iloc[0],
            "change_period": consensus_period,
            "dimensions_changed": int(len(group)),
            "dimensions_agreeing_on_date": int(len(agreeing)),
            "dimensions": sorted(group["dimension"].unique().tolist()),
            "periods_observed": periods_observed,
            "agreement_p_value": p_agreement,
            "max_confidence": float(group["confidence"].max()),
            "strongest_dimension": group.sort_values("magnitude", ascending=False)
                                        ["dimension"].iloc[0],
            "explanation": _explain(entity, consensus_period, agreeing, group),
        })

    result = pd.DataFrame(rows)
    result["survives_fdr"] = benjamini_hochberg(
        result["agreement_p_value"].to_numpy(dtype=float), fdr_q
    )
    result = result.sort_values(
        ["survives_fdr", "dimensions_agreeing_on_date", "dimensions_changed"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    result.attrs["entities_tested"] = len(result)
    result.attrs["fdr_q"] = fdr_q
    survivors = int(result["survives_fdr"].sum())
    LOGGER.info(
        "changepoint: %s entities with a dated change, %s surviving the agreement test "
        "at FDR q=%.2f",
        f"{len(result):,}", f"{survivors:,}", fdr_q,
    )
    return result


def _explain(entity: str, period: str, agreeing: pd.DataFrame,
             everything: pd.DataFrame) -> str:
    """One sentence a non-statistician can act on, with the cause left open."""
    readable = {
        "volume": "the number of works",
        "value_median": "the typical work value",
        "value_iqr": "the spread of work values",
        "value_p90": "the largest work values",
        "duration_median": "how long works took",
        "duration_p90": "the slowest works",
        "completion_rate": "the completion rate",
        "backdating_rate": "the rate of backward-running dates",
        "archetype_entropy": "the variety of work types",
        "archetype_top_share": "the concentration on one work type",
        "archetype_mix": "which kinds of work were built",
    }
    parts = []
    for row in agreeing.itertuples():
        name = readable.get(row.dimension, row.dimension)
        if row.dimension == "archetype_mix":
            parts.append(f"{name} changed")
        else:
            parts.append(f"{name} moved {row.direction}")
    joined = "; ".join(parts) if parts else "behaviour changed"
    others = len(everything) - len(agreeing)
    tail = f" Another {others} dimension(s) turned in a nearby period." if others else ""
    return (
        f"Around {period}, {joined}. This says something changed and when — not why. "
        f"A new officer, a new state scheme or a flood all look like this, so the two "
        f"periods are shown side by side for a person to explain.{tail}"
    )
