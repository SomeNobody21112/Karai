"""FastAPI service over the pre-computed intelligence artifacts.

Everything is loaded into memory once at startup (210k rows is nothing) and served
read-only. No model runs here — the pipeline produced the artifacts; this just serves them.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from mplads import config

app = FastAPI(title="MPLADS Intelligence", version="1.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)


class Store:
    def __init__(self, artifacts: Path):
        self.stats = json.loads((artifacts / "stats.json").read_text(encoding="utf-8"))
        cases = json.loads((artifacts / "case_files.json").read_text(encoding="utf-8"))
        self.cases_by_ref = {c["work_ref"]: c for c in cases}
        # Worklist summary rows, already ranked by audit-ROI in the pipeline.
        self.worklist = [
            {
                "work_ref": c["work_ref"],
                "description": c["identity"]["description"],
                "state": c["identity"]["state"],
                "implementing_agency": c["identity"]["implementing_agency"],
                "archetype": c["archetype"]["label"],
                "band": c["confidence_band"],
                "n_families": c["n_signal_families"],
                "priority": c["priority"],
                "exposure_rupees": c["exposure_rupees"],
                "audit_roi": c["audit_roi"],
                "recommended_amount": c["identity"]["recommended_amount"],
            }
            for c in cases
        ]


@lru_cache(maxsize=1)
def store() -> Store:
    return Store(config.ARTIFACTS)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "leads": len(store().worklist)}


@app.get("/api/stats")
def stats() -> dict:
    return store().stats


@app.get("/api/worklist")
def worklist(
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
    state: str | None = None,
    band: str | None = None,
    q: str | None = None,
) -> dict:
    rows = store().worklist
    if state:
        rows = [r for r in rows if r["state"] == state]
    if band:
        rows = [r for r in rows if r["band"] == band]
    if q:
        needle = q.lower()
        rows = [
            r for r in rows
            if (r["description"] or "").lower().find(needle) >= 0
            or (r["implementing_agency"] or "").lower().find(needle) >= 0
        ]
    return {"total": len(rows), "items": rows[offset : offset + limit]}


@app.get("/api/case/{work_ref}")
def case(work_ref: str) -> dict:
    found = store().cases_by_ref.get(work_ref)
    if not found:
        raise HTTPException(status_code=404, detail="case file not found")
    return found


@app.get("/api/states")
def states() -> list[dict]:
    return store().stats["by_state"]
