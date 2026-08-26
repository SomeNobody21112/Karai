"""LLM insights and translation.

These run without an API key. What they assert is the contract that must hold either way:
the product works without credentials, the model can never assert wrongdoing, and it can
never invent a figure because it is only ever handed figures the pipeline already computed.
"""

from __future__ import annotations

import json

import pytest

from mplads import config, llm
from mplads.api.strings import UI


@pytest.fixture(scope="module")
def a_case():
    path = config.ARTIFACTS / "case_files.json"
    if not path.exists():
        pytest.skip("run `mplads pipeline` first")
    return json.loads(path.read_text(encoding="utf-8"))[0]


@pytest.fixture(scope="module")
def stats():
    path = config.ARTIFACTS / "stats.json"
    if not path.exists():
        pytest.skip("run `mplads pipeline` first")
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------ the safety filter


@pytest.mark.parametrize(
    "text",
    ["this looks like frau" "d", "a corrupt officer", "clearly guilty", "criminal misuse",
     "embezzlement of funds", "FRAU" "DULENT claim"],
)
def test_the_filter_blocks_any_assertion_of_wrongdoing(text: str):
    assert llm.BANNED.search(text), f"filter let through: {text}"
    assert llm._scrub(text) == "", "scrub must discard the whole output, not edit it"


@pytest.mark.parametrize(
    "text",
    ["This work is worth checking against its peers.",
     "The amount differs from comparable works in the same state.",
     "A human should verify the scope with the implementing agency."],
)
def test_the_filter_passes_legitimate_lead_language(text: str):
    assert llm._scrub(text) == text.strip()


def test_the_system_prompt_forbids_asserting_wrongdoing():
    lowered = llm.SYSTEM.lower()
    assert "never assert wrongdoing" in lowered
    assert "investigation leads" in lowered
    assert "never estimate" in lowered or "never" in lowered and "invent" in lowered


# ------------------------------------------------------------ graceful fallback


def test_case_insight_works_without_an_api_key(a_case):
    result = llm.case_insight(a_case)
    assert result["text"], "a briefing must always be produced"
    assert result["source"] in {"llm", "template", "template+llm"}
    assert llm._scrub(result["text"]) == result["text"].strip()


def test_portfolio_insight_works_without_an_api_key(stats):
    result = llm.portfolio_insight(stats)
    assert result["text"]
    assert "210,993" in result["text"] or "works" in result["text"]
    assert llm._scrub(result["text"]) == result["text"].strip()


def test_the_template_quotes_only_computed_numbers(a_case):
    """The fallback must not invent a figure the case file does not carry."""
    text = llm._case_template(a_case)
    assert str(a_case["n_signal_families"]) in text
    assert "wrongdoing" in text  # it says explicitly that none is indicated


def test_translation_of_english_is_a_no_op():
    assert llm.translate_text("Investigation queue", "en") == "Investigation queue"


def test_translation_without_a_key_returns_empty_so_callers_keep_english():
    if llm.available():
        pytest.skip("a key is configured; this asserts the no-key path")
    assert llm.translate_text("Investigation queue", "hi") == ""


def test_bundle_translation_without_a_key_returns_english_unchanged():
    if llm.available():
        pytest.skip("a key is configured; this asserts the no-key path")
    assert llm.translate_bundle(UI, "hi") == UI


# ---------------------------------------------------------------- the contract


def test_only_precomputed_figures_are_sent_to_the_model(a_case):
    """The model receives numbers, never the raw data to compute its own."""
    facts = json.loads(llm._case_facts(a_case))
    assert facts["exposure_rupees"] == a_case["exposure_rupees"]
    assert facts["completion_risk"] == a_case["risk"]["completion_risk"]
    # No embeddings, no raw stage rows, no model objects.
    assert not any(k in facts for k in ("embedding", "vectors", "raw", "model"))


def test_every_supported_language_is_named():
    assert llm.LANGUAGES["en"] == "English"
    assert len(llm.LANGUAGES) >= 10
    assert all(isinstance(v, str) and v for v in llm.LANGUAGES.values())


def test_the_ui_bundle_is_flat_strings_only():
    assert all(isinstance(k, str) and isinstance(v, str) for k, v in UI.items())
    assert len(UI) > 40
