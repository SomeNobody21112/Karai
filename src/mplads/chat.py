"""The assistant: a chatbot that answers questions by querying the real artifacts.

It does not know anything about MPLADS on its own. Every fact it states comes from a tool
call against the computed artifacts — the same numbers the dashboard renders. That is the
whole design: the model supplies language and navigation, the pipeline supplies truth.

Tools are read-only by construction. There is no tool that writes, scores, ranks, or
changes a threshold; the assistant can look things up and nothing else.

Without API credits the assistant falls back to `answer_offline()`, a deterministic
keyword router over the same tools. It answers the common questions — how many leads, what
is the top case, what does exposure mean — so the feature demos with or without billing.
"""

from __future__ import annotations

import json
import logging
import re
from functools import lru_cache

from mplads import config, llm

LOGGER = logging.getLogger(__name__)

MAX_TURNS = 8

SYSTEM = """You are the assistant inside a government audit dashboard for MPLADS, the \
scheme under which Indian Members of Parliament recommend local public works.

You answer questions by calling the tools provided. You have no independent knowledge of \
this data — if a tool did not tell you a number, you do not know it, and you say so.

Absolute rules:
- Never state a figure that did not come from a tool result in this conversation.
- This system produces INVESTIGATION LEADS. Never say a work involves wrongdoing, misuse, \
dishonesty or crime, and never say anyone acted improperly. Unusual is not wrong; the \
correct phrasing is always "worth checking".
- "Exposure" is money that may be tied up in works that do not finish. It is never loss, \
theft, or missing money. Correct the user gently if they imply otherwise.
- If asked something the data cannot answer (actual expenditure, cost overruns, payments, \
physical progress, photographs), say plainly that the public data does not contain it, and \
say what we measure instead.
- Be brief. Two to four sentences unless asked for detail. Plain language, no markdown \
headings, no bullet characters.
- When you mention a specific work, include its work_ref so the officer can open it."""


# --------------------------------------------------------------------------- data


@lru_cache(maxsize=1)
def _store():
    """The artifacts, loaded once. Mirrors what the API serves."""
    from mplads.api.app import store

    return store()


def _fmt_rupees(value: float | None) -> str:
    if not value:
        return "unknown"
    if value >= 1e7:
        return f"Rs {value / 1e7:,.2f} crore"
    if value >= 1e5:
        return f"Rs {value / 1e5:,.2f} lakh"
    return f"Rs {value:,.0f}"


# --------------------------------------------------------------------------- tools
#
# Each returns a compact JSON string. Kept small deliberately: a tool that returns
# thousands of rows wastes context and makes the model summarise instead of answer.


def t_portfolio_summary() -> str:
    """National totals: works, money, leads, exposure, health index."""
    stats = _store().stats
    n = stats.get("national", {})
    return json.dumps({
        "total_works": n.get("total_works"),
        "completed": n.get("completed"),
        "open": n.get("open"),
        "total_recommended_rupees": n.get("total_recommended_rupees"),
        "exposure_at_risk_rupees": n.get("total_exposure_rupees"),
        "investigation_leads": n.get("surfaced_leads"),
        "high_confidence_leads": (n.get("bands") or {}).get("HIGH"),
        "medium_confidence_leads": (n.get("bands") or {}).get("MEDIUM"),
        "states": n.get("states"),
        "constituencies": n.get("constituencies"),
        "implementing_agencies": n.get("implementing_agencies"),
        "health_index_out_of_100": (stats.get("health_index") or {}).get("score"),
        "snapshot_date": "2026-05-26",
    })


def t_top_leads(limit: int = 5, state: str = "") -> str:
    """The highest Audit-ROI investigation leads, optionally filtered to one state.

    Args:
        limit: How many to return, 1 to 20.
        state: Optional state name, e.g. "Bihar". Empty means all of India.
    """
    rows = _store().worklist
    if state:
        rows = [r for r in rows if (r.get("state") or "").lower() == state.lower()]
    limit = max(1, min(int(limit), 20))
    return json.dumps([
        {
            "work_ref": r["work_ref"],
            "description": (r.get("description") or "")[:160],
            "state": r.get("state"),
            "implementing_agency": r.get("implementing_agency"),
            "confidence_band": r.get("band"),
            "signal_families": r.get("n_families"),
            "recommended_rupees": r.get("recommended_amount"),
            "exposure_rupees": r.get("exposure_rupees"),
            "signals": r.get("signals"),
        }
        for r in rows[:limit]
    ])


def t_case_detail(work_ref: str) -> str:
    """Everything known about one work: evidence, peers, risk, compliance, next step.

    Args:
        work_ref: The work reference, e.g. "MP3018356-W86316".
    """
    case = _store().cases_by_ref.get(work_ref)
    if not case:
        return json.dumps({"error": f"no case file for {work_ref}. It may not be a surfaced lead."})
    return json.dumps({
        "work_ref": case["work_ref"],
        "identity": case["identity"],
        "work_type": case.get("archetype", {}).get("label"),
        "peer_context": case.get("peer_context"),
        "completion_risk": case.get("risk"),
        "exposure_rupees": case.get("exposure_rupees"),
        "confidence_band": case.get("confidence_band"),
        "signal_families": case.get("n_signal_families"),
        "evidence": case.get("evidence"),
        "compliance_findings": case.get("compliance_findings"),
        "early_warning": case.get("early_warning"),
        "duplicate": case.get("duplicate"),
        "recommended_next_step": case.get("recommended_next_step"),
    })


def t_search_works(query: str, limit: int = 5) -> str:
    """Search surfaced leads by description or implementing agency text.

    Args:
        query: Free text, e.g. "solar street light" or "Saran".
        limit: How many to return, 1 to 20.
    """
    needle = query.lower()
    limit = max(1, min(int(limit), 20))
    hits = [
        r for r in _store().worklist
        if needle in (r.get("description") or "").lower()
        or needle in (r.get("implementing_agency") or "").lower()
        or needle in (r.get("state") or "").lower()
    ][:limit]
    return json.dumps({
        "matches": len(hits),
        "results": [
            {"work_ref": r["work_ref"], "description": (r.get("description") or "")[:160],
             "state": r.get("state"), "band": r.get("band"),
             "exposure_rupees": r.get("exposure_rupees")}
            for r in hits
        ],
    })


def t_state_breakdown(limit: int = 10) -> str:
    """Exposure and lead counts per state, highest exposure first.

    Args:
        limit: How many states, 1 to 36.
    """
    rows = _store().stats.get("by_state", [])[: max(1, min(int(limit), 36))]
    return json.dumps([
        {"state": r.get("state_name"), "works": r.get("works"),
         "exposure_rupees": r.get("exposure"), "leads": r.get("leads")}
        for r in rows
    ])


def t_compliance_summary() -> str:
    """The lifecycle compliance checks, how many works each flagged, and its authority."""
    return json.dumps(_store().stats.get("compliance", {}))


def t_duplicate_summary() -> str:
    """Near-duplicate detection totals and how 'concerning' is defined."""
    return json.dumps(_store().stats.get("duplicates", {}))


def t_archetype_list(limit: int = 10) -> str:
    """The learned work types, largest first, with completion rate and exposure.

    Args:
        limit: How many archetypes, 1 to 50.
    """
    rows = _store().stats.get("archetype_intelligence", [])[: max(1, min(int(limit), 50))]
    return json.dumps([
        {"label": r.get("label"), "works": r.get("n_works"),
         "completion_rate": r.get("completion_rate"),
         "median_amount_rupees": r.get("median_amount"),
         "flagged_rate": r.get("lead_rate")}
        for r in rows
    ])


def t_model_metrics() -> str:
    """How the three trained models performed, with their honest caveats."""
    return json.dumps(_store().metrics)


def t_data_limitations() -> str:
    """Which fields the public data does NOT contain, and what we use instead."""
    transparency = _store().transparency
    return json.dumps({
        "unavailable": [
            {"metric": m["metric"], "why": m["note"]}
            for m in transparency.get("metrics", [])
            if m.get("type") == "Unavailable"
        ],
        "statement": transparency.get("statement"),
    })


TOOL_FUNCS = {
    "t_portfolio_summary": t_portfolio_summary,
    "t_top_leads": t_top_leads,
    "t_case_detail": t_case_detail,
    "t_search_works": t_search_works,
    "t_state_breakdown": t_state_breakdown,
    "t_compliance_summary": t_compliance_summary,
    "t_duplicate_summary": t_duplicate_summary,
    "t_archetype_list": t_archetype_list,
    "t_model_metrics": t_model_metrics,
    "t_data_limitations": t_data_limitations,
}


@lru_cache(maxsize=1)
def _decorated_tools():
    """Wrap the plain functions with @beta_tool so the SDK derives their schemas."""
    from anthropic import beta_tool

    return [beta_tool(fn) for fn in TOOL_FUNCS.values()]


# ------------------------------------------------------------------------ live chat


def answer(question: str, history: list[dict] | None = None, language: str = "en") -> dict:
    """Answer one question, calling tools as needed. Falls back when unavailable."""
    client = llm._client()
    if client is None:
        return answer_offline(question)

    messages = list(history or [])
    messages.append({"role": "user", "content": question})

    system = SYSTEM
    if language != "en":
        system += f"\n\nReply entirely in {llm.LANGUAGES.get(language, language)}."

    used: list[str] = []
    try:
        runner = client.beta.messages.tool_runner(
            model=llm.MODEL,
            max_tokens=2000,
            system=system,
            tools=_decorated_tools(),
            messages=messages,
        )
        final = None
        for turn, message in enumerate(runner):
            final = message
            used += [b.name for b in message.content if b.type == "tool_use"]
            if turn >= MAX_TURNS:
                LOGGER.warning("chat hit the turn cap; returning what we have")
                break
    except Exception as exc:
        LOGGER.warning("chat failed (%s) — falling back", type(exc).__name__)
        return answer_offline(question)

    if final is None:
        return answer_offline(question)
    if getattr(final, "stop_reason", None) == "refusal":
        return {"text": "I could not answer that one. Try rephrasing it.",
                "tools_used": used, "source": "refusal"}

    text = "".join(b.text for b in final.content if b.type == "text")
    cleaned = llm._scrub(text)
    if not cleaned:
        return answer_offline(question)
    return {"text": cleaned, "tools_used": sorted(set(used)), "source": "llm", "model": llm.MODEL}


# --------------------------------------------------------------------- offline mode


WORK_REF = re.compile(r"\bMP\d+-W\d+\b", re.I)


def answer_offline(question: str) -> dict:
    """Deterministic keyword router over the same tools. No model, no credits, no guessing.

    This is not a pretend chatbot — it genuinely answers the common questions from real
    data. It simply cannot handle a phrasing it was not written for, and says so.
    """
    q = question.lower()
    store = _store()
    n = store.stats.get("national", {})

    ref = WORK_REF.search(question)
    if ref:
        case = store.cases_by_ref.get(ref.group(0).upper())
        if not case:
            return {"text": f"{ref.group(0)} is not among the surfaced leads.",
                    "tools_used": ["t_case_detail"], "source": "offline"}
        identity = case["identity"]
        reasons = "; ".join(e["signal"] for e in case.get("evidence", []))
        return {
            "text": (
                f"{case['work_ref']} — {identity.get('description')} in "
                f"{identity.get('state')}. Recommended {_fmt_rupees(identity.get('recommended_amount'))}, "
                f"exposure {_fmt_rupees(case.get('exposure_rupees'))}, confidence "
                f"{case.get('confidence_band')} from {case.get('n_signal_families')} independent "
                f"signal families ({reasons}). {case.get('recommended_next_step')}"
            ),
            "tools_used": ["t_case_detail"], "source": "offline",
        }

    def has(*words): return any(w in q for w in words)

    if has("how many lead", "how many case", "leads are there", "number of lead"):
        return {"text": (
            f"{n.get('surfaced_leads'):,} works were surfaced for review — "
            f"{(n.get('bands') or {}).get('HIGH'):,} at HIGH confidence (three or more "
            f"independent signal families agreed) and "
            f"{(n.get('bands') or {}).get('MEDIUM'):,} at MEDIUM (two)."
        ), "tools_used": ["t_portfolio_summary"], "source": "offline"}

    if has("exposure", "money at risk", "at risk"):
        return {"text": (
            f"Exposure at risk is {_fmt_rupees(n.get('total_exposure_rupees'))}. That is the "
            f"recommended amount multiplied by the chance a work does not finish — money that "
            f"may be tied up in works that stall. It is not loss, not theft, and not missing "
            f"money."
        ), "tools_used": ["t_portfolio_summary"], "source": "offline"}

    if has("top", "highest", "worst", "biggest", "priority"):
        rows = store.worklist[:3]
        listed = " ".join(
            f"{r['work_ref']} ({r.get('state')}, {_fmt_rupees(r.get('exposure_rupees'))} exposure)."
            for r in rows
        )
        return {"text": f"The three highest-ranked leads by Audit-ROI are: {listed}",
                "tools_used": ["t_top_leads"], "source": "offline"}

    if has("duplicate", "repeat", "same work", "copied"):
        d = store.stats.get("duplicates", {})
        return {"text": (
            f"We found {d.get('total_pairs'):,} semantically similar description pairs. "
            f"Repeated descriptions are normal in this scheme, so only "
            f"{d.get('concerning_pairs'):,} are treated as concerning — near-identical, from "
            f"the same implementing agency, for a near-identical amount."
        ), "tools_used": ["t_duplicate_summary"], "source": "offline"}

    if has("expenditure", "spent", "cost overrun", "payment", "photo", "progress %"):
        return {"text": (
            "The public data does not contain verified expenditure, payment tranches, cost "
            "estimates, physical progress or downloadable photographs. We measured this rather "
            "than assumed it: ACTUAL_AMOUNT equals the recommended amount on 98.35% of "
            "completed works. So we report peer-relative amount anomalies and administrative "
            "lifecycle progress instead, and say plainly what is missing."
        ), "tools_used": ["t_data_limitations"], "source": "offline"}

    if has("model", "accuracy", "trained", "c-index", "silhouette"):
        m = store.metrics
        return {"text": (
            f"Three models are trained: clustering into "
            f"{m.get('archetype_clustering', {}).get('k_chosen')} work types (silhouette "
            f"{m.get('archetype_clustering', {}).get('silhouette_at_chosen_k')} — a separation "
            f"measure, never accuracy), a Cox survival model for completion risk (held-out "
            f"C-index {m.get('completion_risk', {}).get('c_index_heldout')}), and an outlier "
            f"detector. None of them predicts wrongdoing — no such labels exist in this "
            f"data, so nothing could be learned from them."
        ), "tools_used": ["t_model_metrics"], "source": "offline"}

    if has("how many work", "total work", "how big", "scale", "overview", "summary"):
        return {"text": (
            f"The portfolio holds {n.get('total_works'):,} works worth "
            f"{_fmt_rupees(n.get('total_recommended_rupees'))} across {n.get('states')} states "
            f"and {n.get('implementing_agencies'):,} implementing agencies. "
            f"{n.get('completed'):,} are complete and {n.get('open'):,} are still open."
        ), "tools_used": ["t_portfolio_summary"], "source": "offline"}

    return {"text": (
        "I can answer that once the API key has credits. Right now I am running in offline "
        "mode, where I can tell you the portfolio totals, the top leads, exposure, duplicates, "
        "the trained models, our data limitations, or the details of any work if you give me "
        "its reference (for example MP3018356-W86316)."
    ), "tools_used": [], "source": "offline"}
