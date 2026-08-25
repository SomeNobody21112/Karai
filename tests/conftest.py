"""Shared fixtures. The raw stage rows are loaded once per session."""

from __future__ import annotations

import pandas as pd
import pytest

from mplads import config

KEY_COLUMNS = [
    "tile_label",
    "mp_id",
    "WORK_RECOMMENDATION_DTL_ID",
    "WORK_ID",
    "RECOMMENDATION_DATE",
    "ACTUAL_END_DATE",
    "RECOMMENDED_AMOUNT",
    "ACTUAL_AMOUNT",
    "Total_Amt",
    "FLAG",
]


@pytest.fixture(scope="session")
def raw_stage_rows() -> pd.DataFrame:
    """All three eSAKSHI files concatenated, as strings, key columns only."""
    frames = []
    for house, path in config.RAW_STAGE_FILES.items():
        frame = pd.read_csv(
            path,
            dtype=str,
            usecols=lambda c: c in KEY_COLUMNS,
            low_memory=False,
        )
        frame["house"] = house
        frames.append(frame)
    return pd.concat(frames, ignore_index=True)


@pytest.fixture(scope="session")
def work_rows(raw_stage_rows: pd.DataFrame) -> pd.DataFrame:
    """Stage rows that carry a usable join key, with `work_ref` attached."""
    usable = raw_stage_rows[raw_stage_rows["WORK_RECOMMENDATION_DTL_ID"].notna()].copy()
    usable["work_ref"] = (
        "MP" + usable["mp_id"] + "-W" + usable["WORK_RECOMMENDATION_DTL_ID"]
    )
    return usable
