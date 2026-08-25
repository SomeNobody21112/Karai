"""Phase 1 ingestion: identity, typing, and the no-silent-drops guarantee.

The counts asserted here are the ones established in docs/DATA_CONTRACT.md. A failure
means either the data changed or the contract is wrong — fix the document, never the
assertion.
"""

from __future__ import annotations

import logging

import pandas as pd
import pytest

from mplads.ingest import loader
from mplads.ingest.schema import CANONICAL_DTYPES, RAW_TO_CANONICAL

RAW_ROWS = 480_768
MP_SUMMARY_ROWS = 3_987
STAGE_ROWS = 476_781
DISTINCT_WORKS = 210_993
ORPHAN_WORKS = 695
DUPLICATE_RECOMMENDATION_ROWS = 156
STAGE_COUNTS = {"RECOMMENDED": 210_454, "SANCTIONED": 180_517, "COMPLETED": 85_810}


# --------------------------------------------------------------------------- identity


def test_work_ref_is_unique(works: pd.DataFrame) -> None:
    """The work table's key. One row per work, no exceptions."""
    assert works["work_ref"].is_unique
    assert works["work_ref"].notna().all()
    assert len(works) == DISTINCT_WORKS


def test_work_ref_is_derived_from_the_composite_key(works: pd.DataFrame) -> None:
    rebuilt = (
        "MP"
        + works["mp_id"].astype("string")
        + "-W"
        + works["work_recommendation_dtl_id"].astype("string")
    )
    assert rebuilt.equals(works["work_ref"])


def test_portal_work_id_is_not_offered_as_a_key(works: pd.DataFrame) -> None:
    """`WORK_ID` is renamed to `portal_work_id` so it cannot be mistaken for the key."""
    assert "work_id" not in works.columns
    assert RAW_TO_CANONICAL["WORK_ID"] == "portal_work_id"


# ------------------------------------------------------------------ no unexpected loss


def test_row_reconciliation_across_the_whole_load(
    raw: pd.DataFrame, stages: pd.DataFrame, mp_totals: pd.DataFrame
) -> None:
    """Every raw row is accounted for: it is either a work-stage row or an MP total."""
    assert len(raw) == RAW_ROWS
    assert len(stages) == STAGE_ROWS
    assert len(mp_totals) == MP_SUMMARY_ROWS
    assert len(stages) + len(mp_totals) == len(raw)


def test_the_two_populations_are_disjoint_and_complementary(
    raw: pd.DataFrame, mp_totals: pd.DataFrame, stages: pd.DataFrame
) -> None:
    """Splitting on work grain is a fact about the data, not a filter that loses rows."""
    assert stages["work_ref"].notna().all()
    assert mp_totals["mp_total_amount"].notna().all()
    # mp_total_amount is populated only on the summary rows.
    assert int(raw.loc[raw["work_ref"].notna(), "mp_total_amount"].notna().sum()) == 0


def test_no_work_is_lost_between_stages_and_works(
    stages: pd.DataFrame, works: pd.DataFrame
) -> None:
    """The work universe is the union of keys across all three stages."""
    assert set(works["work_ref"]) == set(stages["work_ref"])


def test_orphan_works_survive_with_null_attributes(works: pd.DataFrame) -> None:
    """695 works have no recommendation row. They are a conformance signal, not noise."""
    orphans = works[works["recommendation_date"].isna()]
    assert len(orphans) == ORPHAN_WORKS
    # Identity is still known even where attributes are not.
    assert orphans["mp_id"].notna().all()
    assert orphans["recommended_amount"].isna().all()


def test_stage_row_counts_match_the_contract(stages: pd.DataFrame) -> None:
    assert stages["stage"].value_counts().to_dict() == STAGE_COUNTS


def test_dedup_removes_only_the_documented_duplicates(stages: pd.DataFrame) -> None:
    recommended = stages[stages["stage"] == "RECOMMENDED"]
    duplicates = len(recommended) - recommended["work_ref"].nunique()
    assert duplicates == DUPLICATE_RECOMMENDATION_ROWS


# ------------------------------------------------------------------------ determinism


def test_dedup_does_not_depend_on_input_order(stages: pd.DataFrame) -> None:
    """Reversing the input must not change which recommendation row wins."""
    forward = loader.load_works(stages)
    reversed_input = stages.iloc[::-1].reset_index(drop=True)
    backward = loader.load_works(reversed_input)

    left = forward.sort_values("work_ref").reset_index(drop=True)
    right = backward.sort_values("work_ref").reset_index(drop=True)
    pd.testing.assert_frame_equal(left, right)


# ----------------------------------------------------------------------------- typing


def test_dates_are_real_datetimes_and_nothing_was_lost(stages: pd.DataFrame) -> None:
    for column in ("recommendation_date", "completion_date"):
        assert pd.api.types.is_datetime64_any_dtype(stages[column])
    # DATA_CONTRACT section 4: 0 unparseable values under %d-%b-%Y. Every dated raw value
    # survives into the stage table, because the MP summary rows carry no dates at all.
    assert int(stages["recommendation_date"].notna().sum()) == 390_971
    assert int(stages["completion_date"].notna().sum()) == 85_810


def test_canonical_dtypes_are_applied(stages: pd.DataFrame) -> None:
    for column, dtype in CANONICAL_DTYPES.items():
        if column in stages.columns:
            assert str(stages[column].dtype) == dtype, column


def test_every_column_is_snake_case(works: pd.DataFrame, stages: pd.DataFrame) -> None:
    for frame in (works, stages):
        for column in frame.columns:
            assert column == column.lower(), column
            assert " " not in column, column


def test_stage_labels_are_canonical(stages: pd.DataFrame) -> None:
    assert set(stages["stage"].unique()) == set(STAGE_COUNTS)


# ---------------------------------------------------------------------------- logging


def test_every_transform_logs_entry_and_exit_counts(
    raw: pd.DataFrame, caplog: pytest.LogCaptureFixture
) -> None:
    with caplog.at_level(logging.INFO, logger="mplads.ingest.loader"):
        loader.load_stages(raw)
    logged = [r.message for r in caplog.records]
    assert any(m.startswith("load_stages: in=") and "out=" in m for m in logged)
    assert any("reason=" in m for m in logged)


def test_a_row_count_change_without_a_reason_is_an_error() -> None:
    """The guard that makes a silent drop impossible rather than merely discouraged."""
    loader._log_counts("noop", 10, 10)
    loader._log_counts("explained", 10, 4, reason="documented")
    with pytest.raises(AssertionError, match="silent drop"):
        loader._log_counts("unexplained", 10, 4)


# --------------------------------------------------------------- reconciliation oracle


def test_mp_totals_reconcile_against_summed_work_amounts(
    works: pd.DataFrame, mp_totals: pd.DataFrame
) -> None:
    """DATA_CONTRACT section 3 / Q3: does Total_Amt equal the sum of that MP's works?

    This is the free oracle the previous pipeline discarded. It is asserted loosely — the
    point is to detect a *systemic* break in our ingestion, not to demand the portal be
    internally consistent to the rupee.
    """
    ours = works.groupby("mp_id", dropna=True)["recommended_amount"].sum()
    theirs = (
        mp_totals[mp_totals["stage"] == "RECOMMENDED"]
        .drop_duplicates("mp_id")
        .set_index("mp_id")["mp_total_amount"]
    )
    paired = pd.concat([ours.rename("ours"), theirs.rename("theirs")], axis=1).dropna()
    paired = paired[paired["theirs"] > 0]

    assert len(paired) > 1_000, "too few MPs matched to be a meaningful check"
    ratio = paired["ours"] / paired["theirs"]

    # Answered in Phase 1: the median MP reconciles exactly, which establishes what
    # Total_Amt means. The ~18% that do not are real portal inconsistencies and become
    # data-quality leads — they are not permitted to grow silently.
    assert abs(ratio.median() - 1.0) < 1e-6
    exact = ((ratio - 1).abs() < 0.001).mean()
    assert exact > 0.75, (
        f"only {exact:.1%} of MPs reconcile exactly — "
        "our per-MP sums have diverged from the portal's own totals"
    )
