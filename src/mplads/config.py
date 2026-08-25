"""Single source of paths, seeds and the snapshot date.

Nothing in this repo may hardcode a path, a seed, or a date. Import it from here.
"""

from __future__ import annotations

from pathlib import Path

# --- Paths ----------------------------------------------------------------
#
# The supplied data package lives in `Dataset/`, not `data/raw/` as sketched in
# the FRD section 1.5. `Dataset/` is treated as READ-ONLY: we never write into
# it. Our own outputs go to `data/interim/` and `data/artifacts/`.

REPO_ROOT = Path(__file__).resolve().parents[2]

DATASET = REPO_ROOT / "Dataset"

#: The three eSAKSHI stage-wise exports. These are the ONLY inputs our pipeline
#: reads. Everything else under `Dataset/` is a previous team's derived output
#: and is used for cross-checking, never as an input.
DATA_RAW = DATASET / "raw"

#: A previous pipeline's processed tables, features, model artifacts and
#: outputs. Read-only reference used to validate our own numbers. Nothing here
#: may be consumed by our pipeline as an input.
REFERENCE = DATASET

DATA_INTERIM = REPO_ROOT / "data" / "interim"
ARTIFACTS = REPO_ROOT / "data" / "artifacts"
DOCS = REPO_ROOT / "docs"

#: The raw stage-wise files, by house. All three share a common column core;
#: the Rajya Sabha file has 29 columns to the Lok Sabha files' 31.
RAW_STAGE_FILES: dict[str, Path] = {
    "ls17": DATA_RAW / "esakshi_stagewise_works_ls17_raw.csv",
    "ls18": DATA_RAW / "esakshi_stagewise_works_ls18_raw.csv",
    "rs": DATA_RAW / "esakshi_stagewise_works_rs_raw.csv",
}

#: Present in `Dataset/raw/` but NOT read by the pipeline: it carries only the
#: recommendation stage, so it cannot support the lifecycle join. Kept for
#: provenance and possible cross-validation of recommendation records.
UNUSED_RAW_FILES: dict[str, Path] = {
    "vonter": DATA_RAW / "vonter_mplads_recommendations_raw.csv",
}

# --- Determinism ----------------------------------------------------------

RANDOM_SEED = 42

# --- Snapshot -------------------------------------------------------------
#
# Set in Phase 2 from the data, not guessed. Every censoring decision and every
# "as of" statement in the product resolves to this one value.

SNAPSHOT_DATE = None  # type: ignore[assignment]  # set in Phase 2


def ensure_dirs() -> None:
    """Create the output directories this pipeline writes to."""
    for path in (DATA_INTERIM, ARTIFACTS, DOCS):
        path.mkdir(parents=True, exist_ok=True)
