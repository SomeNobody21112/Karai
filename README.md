# mplads-intel

AI-assisted forensic monitoring and decision support over MPLADS / eSAKSHI work-lifecycle
data. It learns what normal work looks like across the national portfolio, compares each
work against its true peers, predicts completion risk, detects behavioural change, fuses
those signals into an explainable case file, and ranks case files by audit
return-on-investment.

**SIH 2026 · PS 26102 (MoSPI) · Team Morior Invictus**

> **This system produces investigation leads, never fraud verdicts.** There are no fraud
> labels in MPLADS public data. Nothing here is a supervised fraud model and no output is a
> fraud probability. Every case file ends in an action for a human to take.

## Status

Phase 0 of 11 complete: repository bootstrap and data contract. The full README — with the
architecture diagram, quickstart, and a results table drawn from real artifacts — is a
Phase 11 deliverable.

## Quickstart (development)

```bash
python -m uv venv --python 3.11 .venv
python -m uv pip install --python .venv/Scripts/python.exe -e ".[dev]"
.venv/Scripts/python.exe -m mplads.cli paths
.venv/Scripts/python.exe -m pytest
```

## Data

The supplied data package lives in `Dataset/` and is **not** committed. Our pipeline reads
only the three eSAKSHI stage-wise CSVs in `Dataset/raw/`; everything else in that directory
is a previous pipeline's derived output, used to cross-check our numbers and never as an
input.

Start with **[docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md)** — what the data actually
contains, measured, including what must never be used and why.

## Documentation

| Document | Contents |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Standing context: constraints, conventions, layout, phase list |
| [docs/DATA_CONTRACT.md](docs/DATA_CONTRACT.md) | Every column, the join key, orphan counts, the DO-NOT-USE list |
| `docs/data_profile.txt` | Generated profile of every raw file |
