"""Phase 1.2: canonical tables, determinism, idempotence, and the reconciliation report."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd
import pytest

from mplads import config
from mplads.ingest import normalise

DISTINCT_WORKS = 210_993
STAGE_ROWS = 476_781
MP_SUMMARY_ROWS = 3_987
RAW_ROWS = 480_768

# Conformance counts under DEDUP_KEEP = "last" (config.py). See DATA_CONTRACT section 9.
EXPECTED_FLAGS = {
    "is_orphan": 695,
    "has_nonpositive_amount": 6,
    "is_backdated": 1_194,
    "is_future_dated": 9,
    "completed_without_sanction": 70,
}


def _hashes(directory: Path) -> dict[str, str]:
    return {
        path.name: hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.glob("*.parquet"))
    }


@pytest.fixture(scope="module")
def built(raw: pd.DataFrame, tmp_path_factory: pytest.TempPathFactory):
    out = tmp_path_factory.mktemp("interim")
    works, stages, report = normalise.run(interim_dir=out, verbose=False, raw=raw)
    return works, stages, report, out


# ------------------------------------------------------------------------ determinism


def test_running_twice_yields_identical_file_hashes(
    raw: pd.DataFrame, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """The Phase 1 acceptance criterion: byte-identical parquet on rerun."""
    first = tmp_path_factory.mktemp("run1")
    second = tmp_path_factory.mktemp("run2")

    normalise.run(interim_dir=first, verbose=False, raw=raw)
    normalise.run(interim_dir=second, verbose=False, raw=raw)

    left, right = _hashes(first), _hashes(second)
    assert set(left) == {"works.parquet", "stages.parquet", "mp_totals.parquet"}
    assert left == right, f"non-deterministic output:\n  {left}\n  {right}"


def test_rerunning_over_existing_files_is_idempotent(
    raw: pd.DataFrame, tmp_path_factory: pytest.TempPathFactory
) -> None:
    """Writing into a directory that already holds output must not change the result."""
    out = tmp_path_factory.mktemp("idempotent")
    normalise.run(interim_dir=out, verbose=False, raw=raw)
    before = _hashes(out)
    normalise.run(interim_dir=out, verbose=False, raw=raw)
    assert _hashes(out) == before


def test_build_is_pure(raw: pd.DataFrame) -> None:
    """Building twice from one input yields equal frames, independent of any write."""
    from mplads.ingest import loader

    stages = loader.load_stages(raw)
    first = normalise.build_stages(stages)
    second = normalise.build_stages(stages)
    pd.testing.assert_frame_equal(first, second)


# ------------------------------------------------------------------------- work table


def test_works_is_one_row_per_work(built) -> None:
    works, _, _, _ = built
    assert len(works) == DISTINCT_WORKS
    assert works["work_ref"].is_unique
    assert works["work_ref"].notna().all()


def test_works_is_sorted_by_work_ref(built) -> None:
    works, _, _, _ = built
    assert works["work_ref"].is_monotonic_increasing


def test_stage_presence_flags_match_the_stage_table(built) -> None:
    works, stages, _, _ = built
    sanctioned = set(stages.loc[stages["stage"] == "SANCTIONED", "work_ref"])
    completed = set(stages.loc[stages["stage"] == "COMPLETED", "work_ref"])
    assert set(works.loc[works["is_sanctioned"], "work_ref"]) == sanctioned
    assert set(works.loc[works["is_completed"], "work_ref"]) == completed


def test_conformance_flags_are_carried_not_repaired(built) -> None:
    """Every anomaly the contract names is flagged and still present in the table."""
    works, _, _, _ = built
    actual = {column: int(works[column].sum()) for column in EXPECTED_FLAGS}
    assert actual == EXPECTED_FLAGS
    # Flagged rows are still in the table — flagging is not a euphemism for dropping.
    assert len(works) == DISTINCT_WORKS


# ------------------------------------------------------------------------ stage table


def test_stages_are_sorted_in_lifecycle_order(built) -> None:
    _, stages, _, _ = built
    key = stages[["work_ref", "stage_seq"]]
    assert key.equals(key.sort_values(["work_ref", "stage_seq"], kind="mergesort"))


def test_sanction_rows_carry_no_stage_date(built) -> None:
    """No sanction date exists in any source. Copying the recommendation date would
    invent a timeline, so the column is deliberately null for that stage."""
    _, stages, _, _ = built
    sanctioned = stages[stages["stage"] == "SANCTIONED"]
    assert len(sanctioned) == 180_517
    assert sanctioned["stage_date"].isna().all()


def test_dated_stages_carry_their_real_date(built) -> None:
    _, stages, _, _ = built
    assert stages.loc[stages["stage"] == "RECOMMENDED", "stage_date"].notna().sum() == 210_454 - 0
    assert stages.loc[stages["stage"] == "COMPLETED", "stage_date"].notna().sum() == 85_810


# --------------------------------------------------------------------- reconciliation


def test_reconciliation_accounts_for_every_raw_row(built) -> None:
    _, _, report, _ = built
    assert report.raw_rows == RAW_ROWS
    assert report.stages_rows == STAGE_ROWS
    assert report.works_rows == DISTINCT_WORKS
    moved = dict(report.moved)
    assert moved["MP summary rows -> mp_totals.parquet"] == MP_SUMMARY_ROWS
    # Nothing vanishes: stage rows are either MP totals or work-stage rows.
    assert report.stages_rows + MP_SUMMARY_ROWS == report.raw_rows


def test_reconciliation_report_renders_every_reason(built) -> None:
    _, _, report, _ = built
    rendered = report.render()
    for reason, _ in report.moved + report.flagged:
        assert reason in rendered
    assert "480,768" in rendered


def test_all_three_tables_are_written(built) -> None:
    _, _, _, out = built
    for name in ("works.parquet", "stages.parquet", "mp_totals.parquet"):
        assert (out / name).exists()


def test_parquet_round_trips_without_losing_types(built) -> None:
    works, _, _, out = built
    reloaded = pd.read_parquet(out / "works.parquet")
    assert len(reloaded) == len(works)
    assert list(reloaded.columns) == list(works.columns)
    assert pd.api.types.is_datetime64_any_dtype(reloaded["recommendation_date"])
    assert reloaded["is_completed"].dtype == bool


def test_dedup_keep_is_configured_not_hardcoded() -> None:
    assert config.DEDUP_KEEP in {"first", "last"}
