"""Profile every raw CSV without loading a whole file into memory at once.

Writes a full report to docs/data_profile.txt and prints a short summary.
Run:  python scripts/profile_data.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from mplads import config  # noqa: E402

CHUNK = 100_000
SAMPLE_VALUES = 5
DATE_HINTS = ("DATE",)
NUM_HINTS = ("AMOUNT", "Total_Amt", "RATING", "_id", "_ID", "Sno")


def profile_file(path: Path, sep: str = ",") -> dict:
    """Stream a CSV and accumulate per-column statistics."""
    n_rows = 0
    columns: list[str] = []
    nulls: dict[str, int] = {}
    uniques: dict[str, set] = {}
    unique_capped: dict[str, bool] = {}
    samples: dict[str, list] = {}

    reader = pd.read_csv(
        path, sep=sep, dtype=str, chunksize=CHUNK, keep_default_na=True, low_memory=False
    )
    for chunk in reader:
        if not columns:
            columns = list(chunk.columns)
            for col in columns:
                nulls[col] = 0
                uniques[col] = set()
                unique_capped[col] = False
                samples[col] = []
        n_rows += len(chunk)
        for col in columns:
            series = chunk[col]
            nulls[col] += int(series.isna().sum())
            if not unique_capped[col]:
                uniques[col].update(series.dropna().unique().tolist())
                # Stop tracking exact cardinality past 200k distinct values.
                if len(uniques[col]) > 200_000:
                    unique_capped[col] = True
            if len(samples[col]) < SAMPLE_VALUES:
                for value in series.dropna().unique()[:SAMPLE_VALUES]:
                    if value not in samples[col]:
                        samples[col].append(value)
                    if len(samples[col]) >= SAMPLE_VALUES:
                        break

    stats = []
    for col in columns:
        entry = {
            "column": col,
            "nulls": nulls[col],
            "null_pct": 100.0 * nulls[col] / n_rows if n_rows else 0.0,
            "n_unique": (">200000" if unique_capped[col] else len(uniques[col])),
            "samples": samples[col],
            "min": None,
            "max": None,
        }
        if any(h in col for h in DATE_HINTS):
            parsed = pd.to_datetime(pd.Series(sorted(uniques[col])[:200_000]), errors="coerce")
            parsed = parsed.dropna()
            if len(parsed):
                entry["min"], entry["max"] = str(parsed.min().date()), str(parsed.max().date())
        elif any(h in col for h in NUM_HINTS):
            parsed = pd.to_numeric(pd.Series(list(uniques[col])[:200_000]), errors="coerce")
            parsed = parsed.dropna()
            if len(parsed):
                entry["min"], entry["max"] = float(parsed.min()), float(parsed.max())
        stats.append(entry)

    return {"path": path, "rows": n_rows, "cols": len(columns), "stats": stats}


def render(report: dict) -> str:
    lines = [
        "=" * 100,
        f"FILE   {report['path'].name}",
        f"SHAPE  {report['rows']:,} rows x {report['cols']} columns",
        "=" * 100,
        f"{'column':<32} {'null%':>8} {'n_unique':>12}  {'min':<12} {'max':<12} samples",
        "-" * 100,
    ]
    for s in report["stats"]:
        n_unique = s["n_unique"]
        n_unique = f"{n_unique:,}" if isinstance(n_unique, int) else str(n_unique)
        lo = "" if s["min"] is None else str(s["min"])[:12]
        hi = "" if s["max"] is None else str(s["max"])[:12]
        sample = " | ".join(str(v)[:28] for v in s["samples"])[:150]
        lines.append(
            f"{s['column']:<32} {s['null_pct']:>7.3f}% {n_unique:>12}  {lo:<12} {hi:<12} {sample}"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    config.ensure_dirs()
    out = config.DOCS / "data_profile.txt"
    chunks = []

    targets = [(p, ",") for p in config.RAW_STAGE_FILES.values()]
    targets += [(p, ";") for p in config.UNUSED_RAW_FILES.values()]

    for path, sep in targets:
        print(f"profiling {path.name} ...", flush=True)
        report = profile_file(path, sep=sep)
        chunks.append(render(report))
        print(f"  {report['rows']:,} rows x {report['cols']} cols")

    out.write_text("\n".join(chunks), encoding="utf-8")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
