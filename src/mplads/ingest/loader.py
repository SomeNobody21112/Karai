"""Load and type the raw eSAKSHI stage-wise CSVs. No business logic lives here.

The FRD assumes a works file and a separate stage-rows file. This dataset has neither:
there are three stage-wise exports at one grain (one row per work-stage), with per-MP
summary rows interleaved. DATA_CONTRACT sections 2 and 3 establish the structure. The
loaders below map onto that reality:

    load_raw()        480,768  every raw row, typed and renamed, nothing removed
    load_mp_totals()    3,987  the per-MP portfolio totals (no work grain)
    load_stages()     476,781  work-stage rows, the lifecycle event grain
    load_works()      210,993  one row per work, recommendation attributes attached

Splitting summary rows from work rows is a statement about grain, not a business rule:
the two populations have disjoint columns. The single selection rule in this module is the
deterministic dedup inside `load_works()`, which exists because a work must have exactly
one row; it is documented at the call site. Everything else — sanction/completion flags,
derived durations, censoring — belongs to `normalise.py`.

Every transform logs its row count at entry and exit. Rows are never dropped silently.
"""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

from mplads import config
from mplads.ingest.schema import (
    CANONICAL_DTYPES,
    DATE_COLUMNS,
    DATE_FORMAT,
    RAW_TO_CANONICAL,
    STAGE_LABELS,
    WORK_ATTRIBUTE_COLUMNS,
)

LOGGER = logging.getLogger(__name__)


def _log_counts(transform: str, rows_in: int, rows_out: int, reason: str | None = None) -> None:
    """Record a transform's row count at entry and exit, and account for any difference."""
    delta = rows_out - rows_in
    message = f"{transform}: in={rows_in:,} out={rows_out:,} delta={delta:+,}"
    if delta:
        if reason is None:
            raise AssertionError(
                f"{transform} changed the row count by {delta:+,} with no reason given — "
                "this is the silent drop the contract forbids"
            )
        message += f" reason={reason}"
    LOGGER.info(message)


def _cast(frame: pd.DataFrame) -> pd.DataFrame:
    """Apply canonical dtypes. Values that fail to cast become null and are counted."""
    for column, dtype in CANONICAL_DTYPES.items():
        if column not in frame.columns:
            continue
        before_null = int(frame[column].isna().sum())

        if dtype == "boolean":
            lowered = frame[column].str.strip().str.lower()
            cast = lowered.map({"true": True, "false": False}).astype("boolean")
        else:
            numeric = pd.to_numeric(frame[column], errors="coerce")
            cast = numeric.round().astype(dtype) if dtype == "Int64" else numeric.astype(dtype)

        coerced = int(cast.isna().sum()) - before_null
        if coerced:
            LOGGER.warning(
                "cast %s -> %s: %s value(s) unparseable, set to null", column, dtype, f"{coerced:,}"
            )
        frame[column] = cast
    return frame


def _parse_dates(frame: pd.DataFrame) -> pd.DataFrame:
    """Parse date columns with an explicit format. Unparseable values become NaT, counted."""
    for column in DATE_COLUMNS:
        if column not in frame.columns:
            continue
        present = int(frame[column].notna().sum())
        parsed = pd.to_datetime(frame[column], format=DATE_FORMAT, errors="coerce")
        unparseable = present - int(parsed.notna().sum())
        LOGGER.info(
            "parse %s: present=%s unparseable=%s -> NaT",
            column,
            f"{present:,}",
            f"{unparseable:,}",
        )
        if unparseable:
            LOGGER.warning(
                "%s: %s value(s) did not match %s and became NaT",
                column,
                f"{unparseable:,}",
                DATE_FORMAT,
            )
        frame[column] = parsed
    return frame


def _read_file(house: str, path: Path) -> pd.DataFrame:
    """Read one raw CSV as strings, rename to snake_case, cast, and parse dates."""
    frame = pd.read_csv(path, dtype=str, low_memory=False)
    rows_in = len(frame)
    LOGGER.info("read %s: rows=%s cols=%s", path.name, f"{rows_in:,}", len(frame.columns))

    unknown = set(frame.columns) - set(RAW_TO_CANONICAL)
    if unknown:
        raise ValueError(
            f"{path.name} carries columns absent from the data contract: {sorted(unknown)}. "
            "Document them in docs/DATA_CONTRACT.md before ingesting."
        )

    frame = frame.rename(columns=RAW_TO_CANONICAL)
    frame = _cast(frame)
    frame = _parse_dates(frame)

    unmapped = set(frame["stage"].dropna().unique()) - set(STAGE_LABELS)
    if unmapped:
        raise ValueError(f"{path.name} has unmapped tile_label values: {sorted(unmapped)}")
    frame["stage"] = frame["stage"].map(STAGE_LABELS).astype("string")

    frame["source_file"] = path.name
    frame["house_code"] = house
    frame["raw_row_index"] = range(len(frame))

    _log_counts(f"read[{house}]", rows_in, len(frame))
    return frame


def load_raw() -> pd.DataFrame:
    """Every raw stage row from all three files, typed and renamed. Nothing removed."""
    frames = [_read_file(house, path) for house, path in config.RAW_STAGE_FILES.items()]
    rows_in = sum(len(frame) for frame in frames)
    combined = pd.concat(frames, ignore_index=True)

    combined["work_ref"] = (
        "MP"
        + combined["mp_id"].astype("string")
        + "-W"
        + combined["work_recommendation_dtl_id"].astype("string")
    )
    # A work_ref built from a null key component is not an identifier; blank it so that
    # `work_ref.notna()` is the single, honest test for "this row belongs to a work".
    combined.loc[combined["work_recommendation_dtl_id"].isna(), "work_ref"] = pd.NA

    _log_counts("load_raw", rows_in, len(combined))
    return combined


def load_mp_totals(raw: pd.DataFrame | None = None) -> pd.DataFrame:
    """The per-MP, per-stage portfolio totals — the rows with no work grain.

    These carry `mp_total_amount` and nothing else of substance (DATA_CONTRACT section 3).
    They are the reconciliation oracle for Phase 1, not a work-level input.
    """
    raw = load_raw() if raw is None else raw
    rows_in = len(raw)
    totals = raw[raw["work_ref"].isna()].copy()
    columns = [
        "house_code", "source_file", "raw_row_index", "stage", "mp_id", "mp_name",
        "state_name", "constituency_name", "tenure_label", "mp_total_amount",
    ]
    totals = totals[[c for c in columns if c in totals.columns]].reset_index(drop=True)

    _log_counts("load_mp_totals", rows_in, len(totals), reason="selected rows with no work grain")
    return totals


def load_stages(raw: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per work-stage: the lifecycle event grain, 476,781 rows.

    Duplicates are preserved. Deduplication is a normalisation decision, not a load one.
    Pass `raw` to reuse an already-loaded frame instead of re-reading the CSVs.
    """
    raw = load_raw() if raw is None else raw
    rows_in = len(raw)
    stages = raw[raw["work_ref"].notna()].copy().reset_index(drop=True)

    _log_counts(
        "load_stages",
        rows_in,
        len(stages),
        reason=f"{rows_in - len(stages):,} MP summary rows split off to load_mp_totals()",
    )
    LOGGER.info(
        "load_stages: works=%s stages=%s",
        f"{stages['work_ref'].nunique():,}",
        stages["stage"].value_counts().to_dict(),
    )
    return stages


def load_works(stages: pd.DataFrame | None = None) -> pd.DataFrame:
    """One row per work, with its recommendation-stage attributes attached.

    The work universe is the **union of keys across all three stages**, so the 695 works
    that have no recommendation row (DATA_CONTRACT section 2) survive with null attributes
    rather than vanishing. They are a conformance signal, not noise.

    The one selection rule in this module lives here: where a work has more than one
    recommendation row, the earliest by `recommendation_date` wins, tie-broken on
    `(work_ref, source_file, raw_row_index)` so the result never depends on the order the
    files happened to be concatenated in. DATA_CONTRACT section 11.4 records why.
    """
    stages = load_stages() if stages is None else stages
    rows_in = len(stages)

    # `mp_id` and the work serial are non-null on every stage row, so the identity of an
    # orphan work is knowable even when its attributes are not. Take them from the
    # universe rather than the recommendation row.
    identity = ["work_ref", "mp_id", "work_recommendation_dtl_id", "house_code"]
    universe = (
        stages[[*identity, "source_file", "raw_row_index"]]
        .sort_values(["work_ref", "source_file", "raw_row_index"], kind="mergesort")
        .drop_duplicates("work_ref", keep="first")
        .loc[:, identity]
        .reset_index(drop=True)
    )
    LOGGER.info("load_works: work universe = %s distinct work_ref", f"{len(universe):,}")

    recommended = stages[stages["stage"] == "RECOMMENDED"]
    deduped = recommended.sort_values(
        ["recommendation_date", "work_ref", "source_file", "raw_row_index"],
        na_position="last",
        kind="mergesort",
    ).drop_duplicates("work_ref", keep="first")
    _log_counts(
        "load_works.dedup_recommended",
        len(recommended),
        len(deduped),
        reason=f"{len(recommended) - len(deduped):,} duplicate recommendation rows per work_ref",
    )

    attributes = [c for c in WORK_ATTRIBUTE_COLUMNS if c in deduped.columns]
    works = universe.merge(
        deduped[["work_ref", *attributes]], on="work_ref", how="left", validate="one_to_one"
    )

    orphans = int(works["recommendation_date"].isna().sum())
    LOGGER.info(
        "load_works: %s work(s) have no recommendation row and carry null attributes",
        f"{orphans:,}",
    )

    _log_counts(
        "load_works",
        rows_in,
        len(works),
        reason="collapsed stage grain to work grain (union of keys across all stages)",
    )
    return works
