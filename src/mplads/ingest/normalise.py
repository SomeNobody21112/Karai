"""Build the canonical works and stages tables and write them to data/interim/.

This is where structural facts about a work are assembled: which stages it reached, its
completion record, and the conformance flags the data contract requires us to carry rather
than repair. Modelling features — durations, censoring, peer scale — belong to Phase 2.

Determinism is a hard requirement. Two runs must produce byte-identical parquet, which
means every sort is fully specified, every dedup is tie-broken on a stable key, and no
column order depends on dict iteration or set ordering.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from mplads import config
from mplads.ingest import loader

LOGGER = logging.getLogger(__name__)

#: Lifecycle order. `stage_date` alone cannot order a work's stages because the sanction
#: stage has no date anywhere in the source (DATA_CONTRACT section 4), so the sequence
#: number carries the ordering and the date carries only what is actually known.
STAGE_SEQUENCE: dict[str, int] = {"RECOMMENDED": 1, "SANCTIONED": 2, "COMPLETED": 3}

STAGES_COLUMNS: tuple[str, ...] = (
    "work_ref", "mp_id", "house_code", "stage", "stage_seq", "stage_date",
    "recommended_amount", "actual_amount", "portal_work_id", "attach_id", "flag",
    "source_file", "raw_row_index",
)

WORKS_COLUMNS: tuple[str, ...] = (
    "work_ref", "mp_id", "work_recommendation_dtl_id", "house_code", "house", "tenure_label",
    "mp_name", "state_name", "state_id", "constituency", "constituency_name",
    "constituency_id", "implementing_agency",
    "recommendation_date", "recommended_amount", "work_description", "activity_name",
    "work_category", "letter_no", "flag", "attach_id",
    "is_sanctioned", "is_completed", "completion_date", "actual_amount", "portal_work_id",
    "is_orphan", "has_nonpositive_amount", "is_backdated", "is_future_dated",
    "completed_without_sanction",
)


@dataclass
class Reconciliation:
    """Input rows, output rows, and every row that changed population, by reason."""

    raw_rows: int = 0
    stages_rows: int = 0
    works_rows: int = 0
    moved: list[tuple[str, int]] = field(default_factory=list)
    flagged: list[tuple[str, int]] = field(default_factory=list)

    def render(self) -> str:
        lines = [
            "",
            "=" * 72,
            "INGEST RECONCILIATION",
            "=" * 72,
            f"  raw stage rows read            {self.raw_rows:>12,}",
            "",
            "  moved out of the work grain (not dropped — retained elsewhere):",
        ]
        for reason, count in self.moved:
            lines.append(f"    {reason:<44} {count:>12,}")
        lines += [
            "",
            f"  canonical stages rows          {self.stages_rows:>12,}",
            f"  canonical works rows           {self.works_rows:>12,}",
            "",
            "  carried and flagged (never dropped):",
        ]
        for reason, count in self.flagged:
            lines.append(f"    {reason:<44} {count:>12,}")
        lines += ["=" * 72, ""]
        return "\n".join(lines)


def build_stages(stages: pd.DataFrame) -> pd.DataFrame:
    """Canonical stage table: one row per work-stage, in lifecycle order.

    `stage_date` is populated only where a real date exists. Sanction rows carry a verbatim
    copy of `recommendation_date` in the source; treating that as a sanction date would
    invent a timeline, so it is deliberately left null here.
    """
    rows_in = len(stages)
    frame = stages.copy()

    frame["stage_seq"] = frame["stage"].map(STAGE_SEQUENCE).astype("Int64")
    frame["stage_date"] = pd.Series(pd.NaT, index=frame.index, dtype="datetime64[us]")
    is_recommended = frame["stage"] == "RECOMMENDED"
    is_completed = frame["stage"] == "COMPLETED"
    frame.loc[is_recommended, "stage_date"] = frame.loc[is_recommended, "recommendation_date"]
    frame.loc[is_completed, "stage_date"] = frame.loc[is_completed, "completion_date"]

    sanction_rows = int((frame["stage"] == "SANCTIONED").sum())
    LOGGER.info(
        "build_stages: %s sanction row(s) carry a null stage_date — no sanction date "
        "exists in any source",
        f"{sanction_rows:,}",
    )

    frame = frame.sort_values(
        ["work_ref", "stage_seq", "stage_date", "source_file", "raw_row_index"],
        na_position="last",
        kind="mergesort",
    ).reset_index(drop=True)

    frame = frame[list(STAGES_COLUMNS)]
    loader._log_counts("build_stages", rows_in, len(frame))
    return frame


def _completion_records(stages: pd.DataFrame) -> pd.DataFrame:
    """One completion record per work, deduplicated on the configured rule."""
    completed = stages[stages["stage"] == "COMPLETED"]
    deduped = completed.sort_values(
        ["work_ref", "completion_date", "source_file", "raw_row_index"],
        na_position="first",
        kind="mergesort",
    ).drop_duplicates("work_ref", keep=config.DEDUP_KEEP)
    loader._log_counts(
        "normalise.dedup_completed",
        len(completed),
        len(deduped),
        reason=f"{len(completed) - len(deduped):,} duplicate completion rows per work_ref",
    )
    return deduped[["work_ref", "completion_date", "actual_amount", "portal_work_id"]]


def build_works(works: pd.DataFrame, stages: pd.DataFrame, report: Reconciliation) -> pd.DataFrame:
    """Canonical work table: one row per work, with stage presence and conformance flags."""
    rows_in = len(works)
    frame = works.copy()

    sanctioned = set(stages.loc[stages["stage"] == "SANCTIONED", "work_ref"])
    completed = set(stages.loc[stages["stage"] == "COMPLETED", "work_ref"])
    frame["is_sanctioned"] = frame["work_ref"].isin(sanctioned)
    frame["is_completed"] = frame["work_ref"].isin(completed)

    frame = frame.merge(_completion_records(stages), on="work_ref", how="left", validate="one_to_one")

    # --- conformance flags: carried, never repaired (DATA_CONTRACT section 9) ---
    anchor = frame["recommendation_date"].max()
    LOGGER.info("build_works: censoring anchor = max(recommendation_date) = %s", anchor.date())

    frame["is_orphan"] = frame["recommendation_date"].isna()
    frame["has_nonpositive_amount"] = (frame["recommended_amount"] <= 0).fillna(False).astype(bool)
    frame["is_backdated"] = (
        frame["completion_date"].notna()
        & frame["recommendation_date"].notna()
        & (frame["completion_date"] < frame["recommendation_date"])
    )
    frame["is_future_dated"] = frame["completion_date"].notna() & (frame["completion_date"] > anchor)
    frame["completed_without_sanction"] = frame["is_completed"] & ~frame["is_sanctioned"]

    for label, column in [
        ("orphan — no recommendation row", "is_orphan"),
        ("recommended_amount <= 0", "has_nonpositive_amount"),
        ("back-dated — completed before recommended", "is_backdated"),
        ("completion date after the anchor", "is_future_dated"),
        ("completed with no sanction record", "completed_without_sanction"),
    ]:
        count = int(frame[column].sum())
        report.flagged.append((label, count))
        LOGGER.info("build_works: %s = %s", column, f"{count:,}")

    frame = frame.sort_values("work_ref", kind="mergesort").reset_index(drop=True)
    frame = frame[list(WORKS_COLUMNS)]
    loader._log_counts("build_works", rows_in, len(frame))
    return frame


def write_parquet(frame: pd.DataFrame, path: Path) -> str:
    """Write deterministically and return the sha256 of the file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(path, engine="pyarrow", index=False, compression="snappy")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    LOGGER.info("wrote %s rows=%s sha256=%s", path.name, f"{len(frame):,}", digest[:16])
    return digest


def run(
    interim_dir: Path | None = None,
    verbose: bool = True,
    raw: pd.DataFrame | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, Reconciliation]:
    """Build both canonical tables, write them, and print the reconciliation report.

    Pass `raw` to reuse an already-loaded frame instead of re-reading the CSVs.
    """
    interim_dir = config.DATA_INTERIM if interim_dir is None else interim_dir
    report = Reconciliation()

    raw = loader.load_raw() if raw is None else raw
    report.raw_rows = len(raw)

    mp_totals = loader.load_mp_totals(raw)
    report.moved.append(("MP summary rows -> mp_totals.parquet", len(mp_totals)))

    raw_stages = loader.load_stages(raw)
    canonical_stages = build_stages(raw_stages)
    canonical_works = build_works(loader.load_works(raw_stages), raw_stages, report)

    report.stages_rows = len(canonical_stages)
    report.works_rows = len(canonical_works)
    report.moved.append(
        ("stage rows collapsed to work grain", len(canonical_stages) - len(canonical_works))
    )

    write_parquet(canonical_works, interim_dir / "works.parquet")
    write_parquet(canonical_stages, interim_dir / "stages.parquet")
    write_parquet(mp_totals, interim_dir / "mp_totals.parquet")

    if verbose:
        print(report.render())
    return canonical_works, canonical_stages, report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    run()
