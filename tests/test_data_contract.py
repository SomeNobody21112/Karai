"""The data contract, as executable assertions.

Every number here is stated in docs/DATA_CONTRACT.md. If a test fails, either the data
changed or the contract is wrong — in both cases the document must be updated, not the
assertion loosened.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mplads import config

RAW_ROW_COUNT = 480_768
ROWS_PER_FILE = {"ls17": 242_358, "ls18": 179_415, "rs": 58_995}
MP_SUMMARY_ROWS = 3_987
WORK_STAGE_ROWS = 476_781
DISTINCT_WORKS = 210_993
ORPHAN_WORKS = 695
COMPLETED_WITHOUT_SANCTION = 70
CENSORING_ANCHOR = pd.Timestamp("2026-05-26")


def test_every_raw_file_is_present() -> None:
    for name, path in config.RAW_STAGE_FILES.items():
        assert path.exists(), f"missing raw stage file for {name}: {path}"


def test_raw_row_counts(raw_stage_rows: pd.DataFrame) -> None:
    assert len(raw_stage_rows) == RAW_ROW_COUNT
    counts = raw_stage_rows["house"].value_counts().to_dict()
    assert counts == ROWS_PER_FILE


def test_row_reconciliation_has_no_silent_drops(
    raw_stage_rows: pd.DataFrame, work_rows: pd.DataFrame
) -> None:
    """480,768 = 3,987 MP summary rows + 476,781 work-stage rows. Nothing unaccounted."""
    summary = raw_stage_rows["WORK_RECOMMENDATION_DTL_ID"].isna().sum()
    assert summary == MP_SUMMARY_ROWS
    assert len(work_rows) == WORK_STAGE_ROWS
    assert summary + len(work_rows) == RAW_ROW_COUNT


def test_join_key_is_composite_and_work_id_is_not_a_key(work_rows: pd.DataFrame) -> None:
    """WORK_RECOMMENDATION_DTL_ID alone is not unique; the (dtl_id, mp_id) pair is."""
    assert work_rows["WORK_RECOMMENDATION_DTL_ID"].nunique() < DISTINCT_WORKS
    assert work_rows["work_ref"].nunique() == DISTINCT_WORKS
    # WORK_ID is null on every non-completion row, so it can never be the join key.
    non_completed = work_rows[work_rows["tile_label"] != "Works Completed"]
    assert non_completed["WORK_ID"].notna().sum() == 0


def test_orphan_counts_are_stated(work_rows: pd.DataFrame) -> None:
    by_stage = work_rows.groupby("tile_label")["work_ref"]
    recommended = set(by_stage.get_group("Works Recommended"))
    sanctioned = set(by_stage.get_group("Works Sanctioned"))
    completed = set(by_stage.get_group("Works Completed"))

    all_works = recommended | sanctioned | completed
    assert len(all_works) == DISTINCT_WORKS
    assert len(all_works - recommended) == ORPHAN_WORKS
    assert len(completed - sanctioned) == COMPLETED_WITHOUT_SANCTION


def test_mp_summary_rows_carry_total_amt_and_nothing_else(
    raw_stage_rows: pd.DataFrame,
) -> None:
    """The 3,987 dropped rows are MP-level totals, not corrupt work rows."""
    summary = raw_stage_rows[raw_stage_rows["WORK_RECOMMENDATION_DTL_ID"].isna()]
    work = raw_stage_rows[raw_stage_rows["WORK_RECOMMENDATION_DTL_ID"].notna()]

    assert summary["Total_Amt"].notna().all()
    assert summary["mp_id"].notna().all()
    assert summary["RECOMMENDED_AMOUNT"].isna().all()
    # Total_Amt and the work grain are perfectly complementary.
    assert work["Total_Amt"].notna().sum() == 0


def test_dates_parse_without_loss(raw_stage_rows: pd.DataFrame) -> None:
    """0 unparseable dates. Missingness here is structural, never malformation."""
    for column in ("RECOMMENDATION_DATE", "ACTUAL_END_DATE"):
        present = raw_stage_rows[column].dropna()
        parsed = pd.to_datetime(present, format="%d-%b-%Y", errors="coerce")
        assert parsed.isna().sum() == 0, f"{column} has unparseable values"


def test_censoring_anchor_is_max_recommendation_date(raw_stage_rows: pd.DataFrame) -> None:
    """Anchoring on max(all dates) would land in 2044 and inflate every open duration."""
    recommended = pd.to_datetime(
        raw_stage_rows["RECOMMENDATION_DATE"].dropna(), format="%d-%b-%Y"
    )
    completed = pd.to_datetime(
        raw_stage_rows["ACTUAL_END_DATE"].dropna(), format="%d-%b-%Y"
    )
    assert recommended.max() == CENSORING_ANCHOR
    assert completed.max() > CENSORING_ANCHOR
    assert (completed > CENSORING_ANCHOR).sum() == 9


def test_sanction_rows_carry_a_copy_of_the_recommendation_date(
    work_rows: pd.DataFrame,
) -> None:
    """There is no sanction date in any source. This proves the tempting column is a copy."""
    frame = work_rows[["work_ref", "tile_label", "RECOMMENDATION_DATE"]]
    recommended = (
        frame[frame.tile_label == "Works Recommended"]
        .drop_duplicates("work_ref")
        .set_index("work_ref")["RECOMMENDATION_DATE"]
    )
    sanctioned = (
        frame[frame.tile_label == "Works Sanctioned"]
        .drop_duplicates("work_ref")
        .set_index("work_ref")["RECOMMENDATION_DATE"]
    )
    paired = pd.concat(
        [sanctioned.rename("sanction"), recommended.rename("recommendation")], axis=1
    ).dropna()
    assert len(paired) > 100_000
    assert (paired["sanction"] == paired["recommendation"]).all()


def test_actual_amount_carries_no_expenditure_variance(work_rows: pd.DataFrame) -> None:
    """FRD hard constraint #4, as evidence rather than assertion."""
    frame = work_rows.copy()
    for column in ("RECOMMENDED_AMOUNT", "ACTUAL_AMOUNT"):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    recommended = (
        frame[frame.tile_label == "Works Recommended"]
        .drop_duplicates("work_ref")
        .set_index("work_ref")["RECOMMENDED_AMOUNT"]
    )
    actual = (
        frame[frame.tile_label == "Works Completed"]
        .drop_duplicates("work_ref")
        .set_index("work_ref")["ACTUAL_AMOUNT"]
    )
    paired = pd.concat([recommended, actual], axis=1).dropna()
    paired = paired[paired["RECOMMENDED_AMOUNT"] > 0]

    ratio = paired["ACTUAL_AMOUNT"] / paired["RECOMMENDED_AMOUNT"]
    identical_share = (paired["ACTUAL_AMOUNT"] == paired["RECOMMENDED_AMOUNT"]).mean()

    assert identical_share > 0.98
    # No overrun exists anywhere in the national portfolio.
    assert (ratio > 1.05).sum() == 0
    # At most one work differs materially; the rest is float noise.
    assert ((ratio < 0.99) | (ratio > 1.01)).sum() <= 1


def test_activity_name_parses_to_the_official_taxonomy(work_rows: pd.DataFrame) -> None:
    """ACTIVITY_NAME is a composite; its suffix is the permissible-works category."""
    path = config.RAW_STAGE_FILES["ls17"]
    activity = pd.read_csv(path, dtype=str, usecols=["ACTIVITY_NAME"])["ACTIVITY_NAME"]
    parsed = activity.dropna().str.extract(r"^WS/MP\d+/\d{4}-\d{4}/\d+-(?P<category>.+)$")
    matched = parsed["category"].notna()

    assert matched.mean() > 0.90
    # A taxonomy, not free text: two orders of magnitude fewer values than descriptions.
    assert parsed["category"].nunique() < 200


@pytest.mark.parametrize(
    "column",
    ["ACTUAL_AMOUNT", "WORK_ID", "AVERAGE_RATING", "FILE_STATUS", "Sno", "MP_NAME"],
)
def test_do_not_use_columns_are_documented(column: str) -> None:
    """Every DO-NOT-USE column must be justified in the contract, by name."""
    contract = (config.DOCS / "DATA_CONTRACT.md").read_text(encoding="utf-8")
    assert f"`{column}`" in contract


def test_no_fraud_language_in_the_source_tree() -> None:
    """FRD hard constraint #1. Enforced from Phase 0, not retrofitted in Phase 7."""
    banned = ("fraud_probability", "is_fraud", "fraud_score", "fraudulent")
    offenders = []
    for path in (config.REPO_ROOT / "src").rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        offenders += [f"{path.name}:{word}" for word in banned if word in text]
    assert not offenders, f"banned fraud language found: {offenders}"
