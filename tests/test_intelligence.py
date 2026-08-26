"""Tests for the intelligence engines: duplicates, compliance, early warning, temporal.

These assert the *product invariants* — that leads are corroborated, that authority tiers
are honest, that nothing claims to be a fraud finding — not merely that code runs.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from mplads import config
from mplads.intelligence import compliance, duplicates, early_warning, temporal, transparency


@pytest.fixture(scope="module")
def scored():
    path = config.ARTIFACTS / "works_scored.parquet"
    if not path.exists():
        pytest.skip("run `mplads pipeline` first")
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def pairs():
    path = config.ARTIFACTS / "duplicate_pairs.parquet"
    if not path.exists():
        pytest.skip("run `mplads pipeline` first")
    return pd.read_parquet(path)


@pytest.fixture(scope="module")
def artifacts():
    path = config.ARTIFACTS / "stats.json"
    if not path.exists():
        pytest.skip("run `mplads pipeline` first")
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ duplicates


def test_duplicate_classification_bands_are_ordered():
    assert duplicates.classify(0.999) == "EXACT"
    assert duplicates.classify(0.98) == "NEAR_EXACT"
    assert duplicates.classify(0.93) == "HIGH_SIMILARITY"
    assert duplicates.classify(0.87) == "POSSIBLE_REPEAT"
    assert duplicates.classify(0.50) == "NORMAL"


def test_duplicate_pairs_are_semantic_not_string_matches(pairs: pd.DataFrame):
    """A string matcher would only ever find identical text. We find more than that."""
    assert len(pairs) > 0
    assert (~pairs["identical_text"]).sum() > 0, "no non-identical matches — is this a string match?"
    assert pairs["similarity"].between(0, 1).all()


def test_duplicate_pairs_are_emitted_once_and_never_self_paired(pairs: pd.DataFrame):
    assert (pairs["work_ref_a"] != pairs["work_ref_b"]).all()
    assert (pairs["work_ref_a"] < pairs["work_ref_b"]).all()


def test_concerning_subset_is_stricter_than_raw_similarity(pairs: pd.DataFrame):
    """Repeated descriptions are normal; only same-agency, same-amount pairs are concerning."""
    focus = duplicates.concerning(pairs)
    assert len(focus) < len(pairs)
    assert focus["same_implementing_agency"].all()
    assert (focus["similarity"] >= duplicates.NEAR_EXACT).all()


def test_every_duplicate_pair_carries_an_explanation(pairs: pd.DataFrame):
    assert pairs["explanation"].notna().all()
    assert pairs["explanation"].str.contains("human should confirm").all()


# ------------------------------------------------------------------ compliance


def test_every_compliance_check_declares_an_authority_tier():
    valid = {"OFFICIAL_RULE", "OBSERVED_BASELINE", "STATISTICAL_OUTLIER"}
    for name, (authority, severity, meaning) in compliance.CHECKS.items():
        assert authority in valid, name
        assert severity in {"HIGH", "MEDIUM", "LOW"}, name
        assert len(meaning) > 30, name


def test_no_statistical_check_is_asserted_as_an_official_rule():
    """The core honesty guarantee: we never call an outlier a legal breach."""
    for name, (authority, _, _) in compliance.CHECKS.items():
        assert authority != "OFFICIAL_RULE", (
            f"{name} claims official-rule authority, but no statutory threshold ships "
            "with this dataset"
        )


def test_compliance_counts_match_the_data_contract(scored: pd.DataFrame):
    assert int(scored["chk_completed_without_sanction"].sum()) == 70
    assert int(scored["chk_missing_recommendation_record"].sum()) == 695
    assert int(scored["chk_completion_beyond_snapshot"].sum()) == 9
    assert int(scored["chk_non_positive_amount"].sum()) == 6


def test_compliance_flags_never_drop_rows(scored: pd.DataFrame):
    assert len(scored) == 210_993
    assert scored["compliance_severity"].isin({"NONE", "LOW", "MEDIUM", "HIGH"}).all()


# --------------------------------------------------------------- early warning


def test_early_warning_levels_are_valid_and_explained(scored: pd.DataFrame):
    assert scored["early_warning_level"].isin(early_warning.LEVELS).all()
    assert scored["early_warning_reason"].notna().all()


def test_completed_works_never_carry_an_early_warning(scored: pd.DataFrame):
    completed = scored[scored["is_completed"]]
    assert (completed["early_warning_level"] == "LOW").all()
    assert (completed["early_warning_score"] == 0).all()


def test_high_warnings_explain_themselves_with_a_number(scored: pd.DataFrame):
    high = scored[scored["early_warning_level"].isin(["HIGH", "CRITICAL"])]
    if high.empty:
        pytest.skip("no high warnings in this run")
    assert high["early_warning_reason"].str.contains("longer than|survival model").all()


# -------------------------------------------------------------------- temporal


def test_trend_classification_labels_are_from_the_fixed_vocabulary():
    rising = pd.Series([10, 11, 10, 12, 11, 10, 40, 42, 41])
    label, why = temporal.classify_series(rising)
    assert label in {
        "NORMAL", "EMERGING", "SUDDEN_CHANGE", "PERSISTENT_CHANGE", "INSUFFICIENT_HISTORY"
    }
    assert len(why) > 10


def test_short_series_are_skipped_not_forced():
    label, _ = temporal.classify_series(pd.Series([1, 2, 3]))
    assert label == "INSUFFICIENT_HISTORY"


def test_a_planted_level_shift_is_detected():
    """Synthetic validation: a known injected shift must be found."""
    series = pd.Series([10] * 8 + [45, 47, 46])
    label, _ = temporal.classify_series(series)
    assert label in {"SUDDEN_CHANGE", "PERSISTENT_CHANGE"}


def test_temporal_uses_recommendation_time_only(scored: pd.DataFrame):
    built = temporal.build(scored)
    assert "censoring-contaminated" in built["method_note"]
    assert len(built["national_series"]) > 12


# ---------------------------------------------------------------- transparency


def test_unavailable_fields_are_declared_not_faked(scored: pd.DataFrame):
    report = transparency.build(scored)
    unavailable = {m["metric"] for m in report["metrics"] if m["type"] == transparency.UNAVAILABLE}
    for expected in (
        "Verified actual expenditure", "Payment tranches / releases", "Cost estimate",
        "Physical progress %", "Sanction date",
    ):
        assert expected in unavailable, f"{expected} must be declared unavailable"


def test_future_field_interfaces_exist_for_every_unavailable_metric(scored: pd.DataFrame):
    report = transparency.build(scored)
    assert len(report["future_fields"]) >= 6
    assert all("unlocks" in f for f in report["future_fields"])


# ------------------------------------------------------------- fused artifacts


def test_health_index_components_are_weighted_and_explained(artifacts: dict):
    health = artifacts["health_index"]
    assert 0 <= health["score"] <= 100
    assert abs(sum(c["weight"] for c in health["components"]) - 1.0) < 1e-9
    assert all(c["explanation"] for c in health["components"])
    assert "not an official government measure" in health["note"]


def test_archetype_intelligence_profiles_every_cluster(artifacts: dict):
    profiles = artifacts["archetype_intelligence"]
    assert len(profiles) == 50
    for p in profiles[:5]:
        assert p["label"] and p["label"] != "unassigned"
        assert p["n_works"] > 0
        assert 0 <= p["completion_rate"] <= 1


def test_duplicate_summary_separates_concerning_from_raw(artifacts: dict):
    summary = artifacts["duplicates"]
    assert summary["concerning_pairs"] < summary["total_pairs"]
    assert "never proof" in summary["method_note"]


# --------------------------------------------------------------- archetype labels


def test_labels_strip_transliterated_function_words():
    from mplads.intelligence.labels import build_label

    label, interpretable, _ = build_label(["lai", "ke", "lai ki", "solar light", "solar"])
    assert "lai" not in label.lower() and " ke " not in f" {label.lower()} "
    assert "solar" in label.lower()
    assert interpretable


def test_labels_collapse_nested_ngrams():
    from mplads.intelligence.labels import build_label

    label, _, _ = build_label(["hall", "community hall", "community", "mandap"])
    assert label.lower().count("hall") == 1


def test_a_glue_only_cluster_is_marked_uninterpretable_not_invented():
    from mplads.intelligence.labels import build_label

    label, interpretable, note = build_label(["ke", "ki", "ka", "se", "mein"])
    assert not interpretable
    assert "uninterpretable" in label.lower()
    assert note


def test_hindi_work_nouns_are_glossed_to_english():
    from mplads.intelligence.labels import build_label

    label, _, _ = build_label(["ka nirman", "sadak", "mandir"])
    lowered = label.lower()
    assert "construction" in lowered or "road" in lowered or "temple" in lowered
    assert "nirman" not in lowered


def test_catalog_labels_are_readable(artifacts: dict):
    """No shipped label may be pure transliterated glue."""
    for profile in artifacts["archetype_intelligence"]:
        label = profile["label"].lower()
        if profile.get("interpretable") is False:
            assert "uninterpretable" in label
        else:
            assert not label.startswith(("ke ", "ki ", "lai ", "nu ")), profile["label"]
