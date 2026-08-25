"""`mplads <phase>` — one entry point per pipeline phase.

Phases are added as they are implemented. Nothing here does work; each subcommand
delegates to its module so the CLI stays a thin, testable shell.
"""

from __future__ import annotations

import argparse
import sys

from mplads import config


def cmd_paths(_: argparse.Namespace) -> int:
    """Print resolved paths — the fastest way to confirm a fresh clone is wired up."""
    print(f"repo root     {config.REPO_ROOT}")
    print(f"raw stage csv {config.DATA_RAW}")
    print(f"interim       {config.DATA_INTERIM}")
    print(f"artifacts     {config.ARTIFACTS}")
    print(f"reference     {config.REFERENCE}  (read-only)")
    print(f"snapshot date {config.SNAPSHOT_DATE}  (set in Phase 2)")
    print(f"random seed   {config.RANDOM_SEED}")
    missing = [p.name for p in config.RAW_STAGE_FILES.values() if not p.exists()]
    if missing:
        print(f"\nMISSING RAW FILES: {missing}")
        return 1
    print("\nall raw stage files present")
    return 0


def cmd_profile(_: argparse.Namespace) -> int:
    """Re-run the Phase 0 data profile."""
    import runpy

    runpy.run_path(str(config.REPO_ROOT / "scripts" / "profile_data.py"), run_name="__main__")
    return 0


def cmd_ingest(_: argparse.Namespace) -> int:
    """Phase 1: build the canonical works and stages tables and write them to interim."""
    import logging

    from mplads.ingest import normalise

    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    normalise.run()
    return 0


def cmd_pipeline(_: argparse.Namespace) -> int:
    """Run Learn -> Compare -> Predict -> Explain -> Prioritise into data/artifacts."""
    import logging

    from mplads import pipeline

    logging.basicConfig(level=logging.INFO, format="%(levelname)-7s %(message)s")
    pipeline.run()
    return 0


def cmd_api(args: argparse.Namespace) -> int:
    """Serve the API over the pre-computed artifacts."""
    import uvicorn

    uvicorn.run("mplads.api.app:app", host="127.0.0.1", port=args.port)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="mplads", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("paths", help="print resolved paths and check the raw files exist")
    sub.add_parser("profile", help="profile the raw CSVs into docs/data_profile.txt")
    sub.add_parser("ingest", help="build canonical works/stages parquet in data/interim")
    sub.add_parser("pipeline", help="run the full intelligence pipeline into data/artifacts")
    api_p = sub.add_parser("api", help="serve the API over the computed artifacts")
    api_p.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    handlers = {
        "paths": cmd_paths,
        "profile": cmd_profile,
        "ingest": cmd_ingest,
        "pipeline": cmd_pipeline,
        "api": cmd_api,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
