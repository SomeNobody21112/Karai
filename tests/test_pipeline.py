"""Smoke tests for the intelligence pipeline and the API it feeds.

These assert the product's invariants — the corroboration rule, exposure semantics, and
the human-in-the-loop framing — not just that code runs.
"""

from __future__ import annotations

import json

import pytest

from mplads import config


@pytest.fixture(scope="module")
def artifacts():
    """Require a pipeline run to exist. Skip cleanly if it has not been run."""
    path = config.ARTIFACTS / "case_files.json"
    if not path.exists():
        pytest.skip("run `python -m mplads.pipeline` first")
    cases = json.loads(path.read_text(encoding="utf-8"))
    stats = json.loads((config.ARTIFACTS / "stats.json").read_text(encoding="utf-8"))
    return cases, stats


def test_every_surfaced_work_has_at_least_two_families(artifacts):
    """The corroboration rule: nothing is surfaced on a single signal alone."""
    cases, _ = artifacts
    assert cases
    assert all(c["n_signal_families"] >= 2 for c in cases)


def test_every_case_ends_in_a_human_action(artifacts):
    cases, _ = artifacts
    for c in cases:
        assert c["recommended_next_step"].lower().startswith("a human should")
        assert c["not_a_fraud_finding"] is True


def test_every_case_carries_its_evidence(artifacts):
    cases, _ = artifacts
    for c in cases:
        assert len(c["evidence"]) >= 1
        families = {e["family"] for e in c["evidence"]}
        assert len(families) == c["n_signal_families"]


def test_exposure_is_amount_times_risk_never_exceeds_amount(artifacts):
    """Exposure is a share of the recommended amount, never more. It is not loss."""
    cases, _ = artifacts
    for c in cases:
        amount = c["identity"]["recommended_amount"]
        if amount:
            assert c["exposure_rupees"] <= amount + 1


def test_worklist_is_ranked_by_audit_roi(artifacts):
    cases, _ = artifacts
    rois = [c["audit_roi"] for c in cases]
    assert rois == sorted(rois, reverse=True)


def test_stats_reconcile_with_the_contract(artifacts):
    _, stats = artifacts
    assert stats["national"]["total_works"] == 210_993
    assert stats["national"]["states"] == 36


def test_api_serves_the_artifacts():
    from fastapi.testclient import TestClient

    from mplads.api.app import app

    if not (config.ARTIFACTS / "case_files.json").exists():
        pytest.skip("run the pipeline first")
    client = TestClient(app)
    assert client.get("/api/health").json()["status"] == "ok"
    top = client.get("/api/worklist?limit=1").json()["items"][0]
    case = client.get(f"/api/case/{top['work_ref']}").json()
    assert case["not_a_fraud_finding"] is True
    assert client.get("/api/case/NON-EXISTENT").status_code == 404
