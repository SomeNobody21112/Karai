"""FastAPI service over the pre-computed intelligence artifacts.

Everything is loaded into memory once at startup (210k rows is nothing) and served
read-only. No model runs here — the pipeline produced the artifacts; this serves them.

Role scoping is **simulation**, not authentication: the client declares a role and a scope,
and the API narrows the data accordingly. This is prototype behaviour and is labelled as
such in the UI. Production would put a real identity provider in front of the same filter.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware

from mplads import config, llm
from mplads.api import auth
from mplads.api.strings import UI
from mplads.api.audit import AuditLog
from mplads.api.auth import Principal, current_principal

app = FastAPI(title="MPLADS Intelligence", version="2.0")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

#: role -> which column narrows the data, and what the role is called.
ROLES: dict[str, dict] = {
    "ministry": {"label": "Ministry (MoSPI)", "scope_field": None,
                 "focus": "National aggregates, state comparison, systemic patterns"},
    "state": {"label": "State Nodal Authority", "scope_field": "state",
              "focus": "District and agency comparison within the state"},
    "district": {"label": "District Authority", "scope_field": "implementing_agency",
                 "focus": "Works, delays, duplicates and compliance in this jurisdiction"},
    "mp": {"label": "Member of Parliament", "scope_field": "constituency",
           "focus": "Works recommended in this constituency"},
}


def _read(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


class Store:
    def __init__(self, artifacts: Path):
        self.stats = _read(artifacts / "stats.json")
        self.temporal = _read(artifacts / "temporal.json")
        self.transparency = _read(artifacts / "transparency.json")
        self.metrics = _read(artifacts / "models" / "metrics.json")

        cases = _read(artifacts / "case_files.json")
        self.cases_by_ref = {c["work_ref"]: c for c in cases}
        self.worklist = [
            {
                "work_ref": c["work_ref"],
                "description": c["identity"]["description"],
                "state": c["identity"]["state"],
                "constituency": c["identity"]["constituency"],
                "implementing_agency": c["identity"]["implementing_agency"],
                "mp_name": c["identity"]["mp_name"],
                "archetype": c["archetype"]["label"],
                "band": c["confidence_band"],
                "n_families": c["n_signal_families"],
                "priority": c["priority"],
                "exposure_rupees": c["exposure_rupees"],
                "audit_roi": c["audit_roi"],
                "recommended_amount": c["identity"]["recommended_amount"],
                "early_warning": c.get("early_warning", {}).get("level", "LOW"),
                "compliance_flags": len(c.get("compliance_findings", [])),
                "has_duplicate": c.get("duplicate") is not None,
                "signals": [e["signal"] for e in c.get("evidence", [])],
            }
            for c in cases
        ]

        dupes = artifacts / "duplicate_pairs.parquet"
        self.duplicate_pairs = (
            pd.read_parquet(dupes) if dupes.exists() else pd.DataFrame()
        )


@lru_cache(maxsize=1)
def store() -> Store:
    return Store(config.ARTIFACTS)


@lru_cache(maxsize=1)
def audit() -> AuditLog:
    return AuditLog(config.AUDIT_LOG_PATH)


@app.middleware("http")
async def record_every_request(request: Request, call_next):
    """Every intelligence read is written to the append-only, hash-chained log."""
    response = await call_next(request)
    path = request.url.path
    if path.startswith("/api/") and not path.startswith("/api/audit"):
        principal = getattr(request.state, "principal", None)
        try:
            audit().record(
                actor=getattr(principal, "subject", "anonymous"),
                role=getattr(principal, "role", "open-data"),
                action=request.method,
                resource=path,
                detail={"query": dict(request.query_params), "status": response.status_code},
            )
        except Exception:  # logging must never break the request path
            pass
    return response


def _scope(rows: list[dict], role: str | None, scope: str | None) -> list[dict]:
    """Narrow a worklist to a role's jurisdiction. Role simulation, not authentication."""
    if not role or role == "ministry" or not scope:
        return rows
    field = ROLES.get(role, {}).get("scope_field")
    if not field:
        return rows
    return [r for r in rows if r.get(field) == scope]


# ------------------------------------------------------------------- core endpoints


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok", "leads": len(store().worklist), "version": app.version}


@app.get("/api/roles")
def roles() -> dict:
    """Available roles and the scope values each can select."""
    s = store()
    states = sorted({r["state"] for r in s.worklist if r["state"]})
    constituencies = sorted({r["constituency"] for r in s.worklist if r["constituency"]})
    agencies = sorted({r["implementing_agency"] for r in s.worklist if r["implementing_agency"]})
    return {
        "roles": ROLES,
        "scopes": {
            "state": states,
            "mp": constituencies[:600],
            "district": agencies[:900],
        },
        "note": "Role simulation for the prototype. No authentication is implemented; "
                "production would place an identity provider in front of the same filter.",
    }


@app.get("/api/stats")
def stats(role: str | None = None, scope: str | None = None) -> dict:
    """National statistics, or a role-scoped recomputation of the headline numbers."""
    s = store()
    if not role or role == "ministry" or not scope:
        return s.stats

    rows = _scope(s.worklist, role, scope)
    scoped = dict(s.stats)
    scoped["national"] = {
        **s.stats["national"],
        "scoped": True,
        "scope_role": role,
        "scope_value": scope,
        "surfaced_leads": len(rows),
        "total_exposure_rupees": sum(r["exposure_rupees"] for r in rows),
        "bands": {
            band: sum(1 for r in rows if r["band"] == band) for band in ("HIGH", "MEDIUM")
        },
    }
    return scoped


@app.get("/api/worklist")
def worklist(
    limit: int = Query(25, ge=1, le=200),
    offset: int = Query(0, ge=0),
    state: str | None = None,
    band: str | None = None,
    warning: str | None = None,
    signal: str | None = None,
    q: str | None = None,
    role: str | None = None,
    scope: str | None = None,
) -> dict:
    rows = _scope(store().worklist, role, scope)
    if state:
        rows = [r for r in rows if r["state"] == state]
    if band:
        rows = [r for r in rows if r["band"] == band]
    if warning:
        rows = [r for r in rows if r["early_warning"] == warning]
    if signal:
        rows = [r for r in rows if signal in r["signals"]]
    if q:
        needle = q.lower()
        rows = [
            r for r in rows
            if needle in (r["description"] or "").lower()
            or needle in (r["implementing_agency"] or "").lower()
        ]
    return {"total": len(rows), "items": rows[offset : offset + limit]}


@app.get("/api/case/{work_ref}")
def case(work_ref: str, principal: Principal = Depends(current_principal)) -> dict:
    found = store().cases_by_ref.get(work_ref)
    if not found:
        raise HTTPException(status_code=404, detail="case file not found")
    identity = found["identity"]
    auth.require_scope(
        principal,
        {
            "state": identity.get("state"),
            "implementing_agency": identity.get("implementing_agency"),
            "constituency": identity.get("constituency"),
        },
        f"case file {work_ref}",
    )
    return found


# --------------------------------------------------------------------- audit trail


@app.get("/api/audit/verify")
def audit_verify() -> dict:
    """Recompute the whole hash chain and report whether it is intact."""
    return audit().verify_chain()


@app.get("/api/audit/tail")
def audit_tail(limit: int = Query(50, ge=1, le=500)) -> list[dict]:
    return audit().tail(limit)


@app.get("/api/auth/demo-tokens")
def demo_tokens() -> dict:
    """Seeded tokens for the demo. Never a production issuance mechanism."""
    return {
        "tokens": auth.seed_demo_tokens(),
        "require_auth": config.REQUIRE_AUTH,
        "note": "Set MPLADS_REQUIRE_AUTH=1 to enforce bearer auth and exercise the 403 "
                "paths. Tokens are seeded from a development signing key, not issued by "
                "an identity provider.",
    }


@app.get("/api/states")
def states() -> list[dict]:
    return store().stats.get("by_state", [])


@app.get("/api/models")
def models() -> dict:
    return store().metrics


# ------------------------------------------------------- language & AI briefings


@app.get("/api/languages")
def languages() -> dict:
    """Supported interface languages, and whether live translation is configured."""
    return {
        "languages": llm.LANGUAGES,
        "llm_available": llm.available(),
        "note": "Interface strings are translated once and cached. Without an API key the "
                "interface stays in English and briefings fall back to a deterministic "
                "template built from the same numbers.",
    }


@app.get("/api/strings")
def strings(lang: str = Query("en")) -> dict:
    """The whole UI string bundle in one language. Cached on disk after first use."""
    if lang not in llm.LANGUAGES:
        raise HTTPException(400, f"unsupported language: {lang}")
    return {"lang": lang, "strings": llm.translate_bundle(UI, lang)}


@app.get("/api/insight/portfolio")
def portfolio_insight(lang: str = Query("en"), role: str | None = None,
                      scope: str | None = None) -> dict:
    """A written brief over the national (or scoped) picture."""
    return llm.portfolio_insight(stats(role=role, scope=scope), language=lang)


@app.get("/api/insight/case/{work_ref}")
def case_insight(work_ref: str, lang: str = Query("en"),
                 principal: Principal = Depends(current_principal)) -> dict:
    """A written brief for one case file, in the requested language."""
    found = store().cases_by_ref.get(work_ref)
    if not found:
        raise HTTPException(status_code=404, detail="case file not found")
    identity = found["identity"]
    auth.require_scope(
        principal,
        {
            "state": identity.get("state"),
            "implementing_agency": identity.get("implementing_agency"),
            "constituency": identity.get("constituency"),
        },
        f"case file {work_ref}",
    )
    return llm.case_insight(found, language=lang)


# ----------------------------------------------------------- intelligence endpoints


@app.get("/api/temporal")
def temporal() -> dict:
    return store().temporal


@app.get("/api/transparency")
def transparency() -> dict:
    return store().transparency


@app.get("/api/compliance")
def compliance() -> dict:
    return store().stats.get("compliance", {})


@app.get("/api/early-warning")
def early_warning() -> dict:
    return store().stats.get("early_warning", {})


@app.get("/api/health-index")
def health_index() -> dict:
    return store().stats.get("health_index", {})


@app.get("/api/archetypes")
def archetypes(limit: int = Query(50, ge=1, le=100)) -> list[dict]:
    return store().stats.get("archetype_intelligence", [])[:limit]


@app.get("/api/duplicates")
def duplicate_pairs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    state: str | None = None,
    classification: str | None = None,
    concerning_only: bool = True,
) -> dict:
    frame = store().duplicate_pairs
    summary = store().stats.get("duplicates", {})
    if frame.empty:
        return {"total": 0, "items": [], "summary": summary}

    if concerning_only:
        from mplads.intelligence import duplicates as dup_mod

        frame = dup_mod.concerning(frame)
    if state:
        frame = frame[frame["state_name"] == state]
    if classification:
        frame = frame[frame["classification"] == classification]

    page = frame.iloc[offset : offset + limit]
    return {
        "total": int(len(frame)),
        "items": json.loads(page.to_json(orient="records")),
        "summary": summary,
    }
