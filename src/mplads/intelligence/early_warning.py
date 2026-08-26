"""Early-warning / stalling risk scoring, with a reason attached to every warning.

This is **not** presented as a validated prediction of failure. It is a risk score built
from a trained survival model plus interpretable lifecycle signals, and every level carries
the sentence that produced it.

Levels: LOW / MEDIUM / HIGH / CRITICAL.
"""

from __future__ import annotations

import logging

import numpy as np
import pandas as pd

from mplads import config

LOGGER = logging.getLogger(__name__)

SNAPSHOT = pd.Timestamp(config.SNAPSHOT_DATE)

LEVELS = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]


def score(works: pd.DataFrame) -> pd.DataFrame:
    """Blend the Cox risk with lifecycle-stall evidence into an explained warning level."""
    frame = works.copy()

    # How long has this work been open, relative to comparable works of the same type in
    # the same state that actually completed? A ratio of 2.4 means "2.4x the peer norm".
    peer_median = (
        frame[frame["is_completed"]]
        .groupby(["activity_category", "state_name"])["duration_days"]
        .median()
        .rename("peer_median_days")
    )
    frame = frame.merge(peer_median, on=["activity_category", "state_name"], how="left")
    national_median = float(
        frame.loc[frame["is_completed"], "duration_days"].median() or 400.0
    )
    frame["peer_median_days"] = frame["peer_median_days"].fillna(national_median)
    frame["stall_ratio"] = frame["duration_days"] / frame["peer_median_days"].clip(lower=30)
    frame.loc[~frame["is_open"], "stall_ratio"] = np.nan

    cox = frame["risk_score"].fillna(0.0).clip(0, 1)
    stall = frame["stall_ratio"].fillna(0.0)

    # Composite in [0,1]: the model's view, raised when a work is visibly overdue.
    stall_component = (stall / 3.0).clip(0, 1)
    composite = (0.6 * cox + 0.4 * stall_component).clip(0, 1)
    composite[~frame["is_open"]] = 0.0
    frame["early_warning_score"] = composite

    conditions = [
        frame["is_open"] & (composite >= 0.75) & (stall >= 2.0),
        frame["is_open"] & (composite >= 0.60),
        frame["is_open"] & (composite >= 0.40),
    ]
    frame["early_warning_level"] = np.select(
        conditions, ["CRITICAL", "HIGH", "MEDIUM"], default="LOW"
    )
    frame.loc[~frame["is_open"], "early_warning_level"] = "LOW"

    frame["early_warning_reason"] = [
        _reason(row) for _, row in frame[
            ["is_open", "stall_ratio", "risk_score", "peer_median_days",
             "duration_days", "early_warning_level", "activity_category", "state_name"]
        ].iterrows()
    ]

    LOGGER.info(
        "early warning: %s",
        frame.loc[frame["is_open"], "early_warning_level"].value_counts().to_dict(),
    )
    return frame


def _reason(row: pd.Series) -> str:
    if not row["is_open"]:
        return "Work is recorded as completed; no early warning applies."

    parts = []
    ratio = row["stall_ratio"]
    if pd.notna(ratio) and ratio >= 1.2:
        parts.append(
            f"open {ratio:.1f}x longer than the typical completed work of this type in "
            f"{row['state_name']} ({int(row['peer_median_days'])} days)"
        )
    risk = row["risk_score"]
    if pd.notna(risk) and risk >= 0.4:
        parts.append(
            f"the survival model puts a {risk * 100:.0f}% chance it will not complete "
            f"within {config.RISK_HORIZON_DAYS} days"
        )
    if not parts:
        return "No stalling indicators; the work is progressing within normal ranges."
    return f"{row['early_warning_level']} — " + "; and ".join(parts) + "."


def summary(works: pd.DataFrame) -> dict:
    open_works = works[works["is_open"]]
    counts = open_works["early_warning_level"].value_counts().to_dict()
    return {
        "levels": {level: int(counts.get(level, 0)) for level in LEVELS},
        "open_works": int(len(open_works)),
        "exposure_by_level": {
            level: float(
                open_works.loc[open_works["early_warning_level"] == level, "rs_exposure"].sum()
            )
            for level in LEVELS
        },
        "method_note": (
            "A risk score, not a validated prediction of failure. It blends a trained Cox "
            "survival model with how long the work has been open relative to comparable "
            "completed works. Every level shows the sentence that produced it."
        ),
    }
