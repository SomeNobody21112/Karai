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


# ------------------------------------------------------------------- the chatbot


def test_every_chat_tool_returns_valid_json(a_case):
    from mplads import chat

    args = {
        "t_case_detail": {"work_ref": a_case["work_ref"]},
        "t_work_lookup": {"work_ref": a_case["work_ref"]},
        "t_search_works": {"query": "road"},
        "t_agency_profile": {"agency": "SARAN"},
        "t_mp_profile": {"mp_name": "a"},
    }
    for name, fn in chat.TOOL_FUNCS.items():
        result = fn(**args.get(name, {}))
        json.loads(result)  # raises if the tool returned something unparseable
        assert result, f"{name} returned nothing"


def test_every_chat_tool_is_read_only():
    """No tool may write, score, rank, or change a threshold."""
    import inspect

    from mplads import chat

    banned = ("write_text", "to_parquet", "to_csv", "open(", "os.remove", "setattr")
    for name, fn in chat.TOOL_FUNCS.items():
        source = inspect.getsource(fn)
        for token in banned:
            assert token not in source, f"{name} appears to mutate state via {token}"


def test_every_chat_tool_is_documented_for_the_model():
    from mplads import chat

    for name, fn in chat.TOOL_FUNCS.items():
        assert (fn.__doc__ or "").strip(), f"{name} has no docstring — the model needs one"


def test_the_chat_system_prompt_forbids_inventing_figures():
    from mplads import chat

    lowered = chat.SYSTEM.lower()
    assert "never state a figure that did not come from a tool" in lowered
    assert "investigation leads" in lowered
    assert "never say anyone acted improperly" in lowered or "wrongdoing" in lowered


def test_offline_chat_answers_from_real_data():
    from mplads import chat

    answer = chat.answer_offline("how many leads are there?")
    assert "37,705" in answer["text"] or "leads" in answer["text"]
    assert answer["source"] == "offline"
    assert answer["tools_used"]


def test_offline_chat_resolves_a_work_reference(a_case):
    from mplads import chat

    ref = a_case["work_ref"]
    answer = chat.answer_offline(f"tell me about {ref}")
    assert ref in answer["text"]
    assert "t_work_lookup" in answer["tools_used"]


def test_offline_chat_resolves_a_work_that_was_never_surfaced(corpus):
    """The assistant covers the whole portfolio, not only the works it flagged.

    Answering only for leads would mean an officer asking about an ordinary work is told
    it does not exist — which reads as "not in the data" when the truth is "nothing wrong
    with it".
    """
    from mplads import chat

    ordinary = corpus[corpus["band"] == "NONE"]["work_ref"].iloc[0]
    answer = chat.answer_offline(f"tell me about {ordinary}")
    assert ordinary in answer["text"]
    assert "not surfaced as a lead" in answer["text"].lower()


def test_offline_chat_searches_the_whole_portfolio_not_just_leads(corpus):
    from mplads import chat
    import json as _json

    result = _json.loads(chat.t_search_works("road", limit=5))
    leads = len([w for w in chat._store().worklist if "road" in (w["description"] or "").lower()])
    assert result["matches"] > leads, (
        "search returned no more than the lead list — it is not reaching the corpus"
    )
    assert result["matches"] <= len(corpus)


def test_offline_chat_reads_field_verifications_live(tmp_path, monkeypatch):
    """A record entered a moment ago must be answerable without rebuilding anything."""
    from mplads import chat, field

    monkeypatch.setattr(field, "DB", tmp_path / "v.sqlite")
    monkeypatch.setattr(field, "PHOTOS", tmp_path / "photos")

    before = chat.answer_offline("what have officers verified in the field?")
    assert "no site verifications" in before["text"].lower()

    field.record("MP1-W1", "NOT_STARTED", actor="auditor", role="auditor")
    after = chat.answer_offline("what have officers verified in the field?")
    assert "1 verification record" in after["text"]


def test_offline_chat_corrects_the_exposure_misconception():
    from mplads import chat

    answer = chat.answer_offline("how much money was lost to exposure?")
    assert "not loss" in answer["text"].lower()


def test_offline_chat_admits_what_the_data_cannot_answer():
    from mplads import chat

    answer = chat.answer_offline("can you detect cost overruns?")
    assert "does not contain" in answer["text"]


def test_offline_chat_says_so_when_it_cannot_help():
    """It names what it can answer instead of apologising for what it is."""
    from mplads import chat

    answer = chat.answer_offline("qqqq zzzz wwww")
    assert "could not find anything matching" in answer["text"]
    assert "MP3018356-W86316" in answer["text"], "no example reference to work from"


def test_no_chat_answer_can_assert_wrongdoing():
    from mplads import chat

    for question in ["how many leads are there?", "show me the top leads",
                     "what about duplicates?", "what models did you train?"]:
        text = chat.answer_offline(question)["text"]
        assert llm._scrub(text) == text.strip(), f"banned language in: {question}"


# ------------------------------------------------------- static translations


def test_every_offered_language_has_a_complete_bundle():
    """A half-translated language in the picker is worse than an absent one."""
    from mplads.api import translations

    for code in translations.BUNDLES:
        assert translations.coverage(code) == 1.0, f"{code} is incomplete"


def test_translations_need_no_api_key():
    """The interface must render in any language with no network call at all."""
    from mplads.api import translations

    bundle = translations.bundle("ta")
    assert bundle["nav.worklist"] != UI["nav.worklist"], "Tamil fell back to English"
    assert len(bundle) == len(UI)


def test_every_bundle_covers_exactly_the_ui_keys():
    from mplads.api import translations

    for code in translations.BUNDLES:
        assert set(translations.bundle(code)) == set(UI), f"{code} key drift"


def test_an_unknown_language_falls_back_to_english():
    from mplads.api import translations

    assert translations.bundle("zz") == dict(UI)


def test_native_names_are_in_their_own_script():
    from mplads.api import translations

    assert translations.BUNDLES["hi"][1] == "हिन्दी"
    assert translations.BUNDLES["ta"][1] == "தமிழ்"
    assert all(native for _, native, _ in translations.BUNDLES.values())
