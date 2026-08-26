"""Audit log, RBAC, and the synthetic validation harness.

Auth tests exercise the *failure* paths — missing token, bad token, wrong jurisdiction —
not only the happy path. The audit test proves tampering is detected, which is the only
claim a hash chain actually supports.
"""

from __future__ import annotations

import json
import sqlite3

import pandas as pd
import pytest

from mplads import config
from mplads.api import auth
from mplads.api.audit import AuditLog


# ------------------------------------------------------------------- audit log


@pytest.fixture
def log(tmp_path):
    return AuditLog(tmp_path / "audit.sqlite")


def test_empty_chain_is_valid(log):
    assert log.verify_chain()["valid"] is True


def test_entries_chain_to_their_predecessor(log):
    for i in range(5):
        log.record("officer", "state", "GET", f"/api/case/W{i}", {"i": i})
    result = log.verify_chain()
    assert result["valid"] is True
    assert result["entries"] == 5


def test_tampering_with_a_row_breaks_the_chain(log):
    for i in range(5):
        log.record("officer", "state", "GET", f"/api/case/W{i}")
    assert log.verify_chain()["valid"] is True

    # Rewrite history directly in the database, bypassing the API.
    with sqlite3.connect(log.path) as conn:
        conn.execute("PRAGMA writable_schema=ON")
        conn.execute("DROP TRIGGER IF EXISTS audit_log_no_update")
        conn.execute("UPDATE audit_log SET actor='someone-else' WHERE seq=3")
        conn.commit()

    result = log.verify_chain()
    assert result["valid"] is False
    assert result["broken_at_seq"] == 3


def test_the_log_refuses_updates_and_deletes(log):
    log.record("officer", "state", "GET", "/api/case/W1")
    with sqlite3.connect(log.path) as conn:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("UPDATE audit_log SET actor='x' WHERE seq=1")
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            conn.execute("DELETE FROM audit_log WHERE seq=1")


def test_verify_states_the_limits_of_the_guarantee(log):
    log.record("officer", "state", "GET", "/api/x")
    assert "not tamper-proof" in log.verify_chain()["note"].lower()


# ------------------------------------------------------------------------ RBAC


def test_a_token_round_trips_its_claims():
    token = auth.issue_token("officer-1", "state", "Bihar")
    principal = auth.decode_token(token)
    assert principal.subject == "officer-1"
    assert principal.role == "state"
    assert principal.scope == "Bihar"
    assert not principal.unrestricted


def test_unrestricted_roles_read_everything():
    for role in ("ministry", "auditor"):
        principal = auth.decode_token(auth.issue_token("x", role))
        assert principal.unrestricted
        assert principal.may_read({"state": "anything"})


def test_a_scoped_role_cannot_read_outside_its_jurisdiction():
    principal = auth.decode_token(auth.issue_token("x", "state", "Bihar"))
    assert principal.may_read({"state": "Bihar"})
    assert not principal.may_read({"state": "Kerala"})


def test_an_invalid_token_is_rejected():
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        auth.decode_token("not-a-real-token")
    assert exc.value.status_code == 401


def test_a_token_signed_with_another_key_is_rejected():
    import jwt
    from fastapi import HTTPException

    forged = jwt.encode({"sub": "attacker", "role": "ministry"}, "wrong-key", algorithm="HS256")
    with pytest.raises(HTTPException) as exc:
        auth.decode_token(forged)
    assert exc.value.status_code == 401


def test_unknown_roles_cannot_be_issued():
    with pytest.raises(ValueError, match="unknown role"):
        auth.issue_token("x", "superuser")


def test_enforced_endpoints_reject_then_accept(monkeypatch):
    """The full HTTP path: 401 without a token, 403 out of scope, 200 in scope."""
    from fastapi.testclient import TestClient

    if not (config.ARTIFACTS / "case_files.json").exists():
        pytest.skip("run the pipeline first")

    monkeypatch.setattr(config, "REQUIRE_AUTH", True)
    from mplads.api.app import app, store

    client = TestClient(app)
    row = store().worklist[0]
    ref, state = row["work_ref"], row["state"]

    assert client.get(f"/api/case/{ref}").status_code == 401
    assert client.get(f"/api/case/{ref}",
                      headers={"Authorization": "Bearer nonsense"}).status_code == 401

    outside = auth.issue_token("x", "state", "__nowhere__")
    assert client.get(f"/api/case/{ref}",
                      headers={"Authorization": f"Bearer {outside}"}).status_code == 403

    inside = auth.issue_token("x", "state", state)
    assert client.get(f"/api/case/{ref}",
                      headers={"Authorization": f"Bearer {inside}"}).status_code == 200


# ------------------------------------------------------- synthetic validation


@pytest.fixture(scope="module")
def report():
    path = config.ARTIFACTS / "validation.json"
    if not path.exists():
        pytest.skip("run `mplads validate` first")
    return json.loads(path.read_text(encoding="utf-8"))


def test_injection_plants_a_known_truth_set():
    from mplads.validation import synthetic

    path = config.ARTIFACTS / "works_scored.parquet"
    if not path.exists():
        pytest.skip("run the pipeline first")
    works = pd.read_parquet(path)
    perturbed, truth = synthetic.inject(works, n_per_type=20)

    assert len(truth) > 40
    assert set(truth.values()) <= set(synthetic.PERTURBATIONS)
    assert len(perturbed) == len(works)


def test_injected_amounts_actually_moved():
    from mplads.validation import synthetic

    path = config.ARTIFACTS / "works_scored.parquet"
    if not path.exists():
        pytest.skip("run the pipeline first")
    works = pd.read_parquet(path).set_index("work_ref")
    perturbed, truth = synthetic.inject(works.reset_index(), n_per_type=20)
    perturbed = perturbed.set_index("work_ref")

    inflated = [r for r, k in truth.items() if k == "inflated_amount"]
    assert (perturbed.loc[inflated, "recommended_amount"]
            > works.loc[inflated, "recommended_amount"]).all()


def test_detection_beats_chance_for_every_perturbation(report: dict):
    """The core claim: the machinery detects the patterns it was built to detect."""
    for name, stats in report["per_perturbation"].items():
        assert stats["detected_rate"] > 0.3, f"{name} detection is no better than noise"


def test_amount_and_stall_injections_are_detected_strongly(report: dict):
    assert report["per_perturbation"]["inflated_amount"]["detected_rate"] > 0.7
    assert report["per_perturbation"]["stalled_lifecycle"]["detected_rate"] > 0.7


def test_the_report_refuses_to_call_itself_a_fraud_rate(report: dict):
    assert "NOT a real-world fraud detection rate" in report["not_a_fraud_rate"]
    assert "no fraud labels exist" in report["not_a_fraud_rate"].lower()
