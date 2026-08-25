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

#: Which recommendation row wins when a work has more than one (156 works do).
#: "last" keeps the most recent by `recommendation_date`; "first" keeps the earliest.
#:
#: The supplied data package used "first". We use "last": where the portal has recorded a
#: work twice, the later record is the more current statement of what was recommended.
#: The choice changes 156 of 210,993 works, so it is nearly immaterial — but it must be
#: made once, here, rather than implied in two places.
#:
#: Determinism does not depend on this value. The sort is always tie-broken on
#: `(work_ref, source_file, raw_row_index)`, so the winner never depends on the order the
#: files happened to be concatenated in. See DATA_CONTRACT section 11.4.
DEDUP_KEEP: str = "last"

# --- Snapshot -------------------------------------------------------------
#
# Set in Phase 2 from the data, not guessed. Every censoring decision and every
# "as of" statement in the product resolves to this one value.

#: Censoring anchor = max(RECOMMENDATION_DATE), measured in Phase 0. Every "as of" and
#: every survival duration resolves to this one date. Anchoring on max(all dates) would
#: land in 2044 (out-of-window completion typos) and inflate open durations by ~18 years.
import datetime as _dt

SNAPSHOT_DATE: _dt.date = _dt.date(2026, 5, 26)

# --- Modelling constants --------------------------------------------------

#: Peer group must have at least this many works before it yields a percentile; else the
#: group backs off to a broader level. Groups below it at the global level never fire.
MIN_PEERS: int = 30

#: A peer group must have at least this many observed completions before its survival
#: curve is trusted; else it backs off to the parent level.
MIN_EVENTS: int = 30

#: Completion-risk horizon in days.
RISK_HORIZON_DAYS: int = 365

#: Amount / duration is only "unusual" above this within-peer percentile.
PEER_PERCENTILE_GATE: float = 0.90

#: Transparent fusion weights — NOT a learned model. Each maps a normalised signal in
#: [0,1] to its contribution. A work is only surfaced when >= 2 independent signal
#: *families* fire (the corroboration rule), never on one signal alone.
SIGNAL_WEIGHTS: dict[str, float] = {
    "peer_amount": 0.60,      # family: amount
    "peer_duration": 0.55,    # family: duration
    "completion_risk": 0.60,  # family: duration
    "conformance": 0.75,      # family: lifecycle
    "change_point": 0.50,     # family: behaviour
    "anomaly": 0.40,          # family: multivariate
}

#: Which family each signal belongs to. Confidence counts distinct families, not signals,
#: so two signals reading the same clock cannot manufacture corroboration.
SIGNAL_FAMILY: dict[str, str] = {
    "peer_amount": "amount",
    "peer_duration": "duration",
    "completion_risk": "duration",
    "conformance": "lifecycle",
    "change_point": "behaviour",
    "anomaly": "multivariate",
}


def ensure_dirs() -> None:
    """Create the output directories this pipeline writes to."""
    for path in (DATA_INTERIM, ARTIFACTS, DOCS):
        path.mkdir(parents=True, exist_ok=True)
