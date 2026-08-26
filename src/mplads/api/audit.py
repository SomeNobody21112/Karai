"""Append-only, hash-chained audit log.

Every request that reads intelligence is recorded. Each row carries the SHA-256 of its own
contents **plus the previous row's hash**, so the log is a chain: altering or deleting any
historical row breaks every hash after it, and `verify_chain()` reports exactly where.

This is tamper-*evident*, not tamper-proof. A writer with database access can rewrite the
whole chain from the edit point forward. Detecting that would need the head hash published
somewhere the writer does not control (a WORM store, or a notary). The architecture allows
it; this prototype does not implement it, and the UI says so.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path

LOGGER = logging.getLogger(__name__)

GENESIS = "0" * 64
_LOCK = threading.Lock()

SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    seq        INTEGER PRIMARY KEY AUTOINCREMENT,
    ts         TEXT NOT NULL,
    actor      TEXT NOT NULL,
    role       TEXT NOT NULL,
    action     TEXT NOT NULL,
    resource   TEXT NOT NULL,
    detail     TEXT NOT NULL,
    prev_hash  TEXT NOT NULL,
    row_hash   TEXT NOT NULL
);
-- Append-only enforced in the database itself, not merely in application code.
CREATE TRIGGER IF NOT EXISTS audit_log_no_update
BEFORE UPDATE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_log_no_delete
BEFORE DELETE ON audit_log
BEGIN SELECT RAISE(ABORT, 'audit_log is append-only'); END;
"""


def _digest(ts: str, actor: str, role: str, action: str, resource: str,
            detail: str, prev_hash: str) -> str:
    payload = json.dumps(
        [ts, actor, role, action, resource, detail, prev_hash], separators=(",", ":")
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class AuditLog:
    def __init__(self, path: Path):
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def head(self) -> str:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT row_hash FROM audit_log ORDER BY seq DESC LIMIT 1"
            ).fetchone()
        return row["row_hash"] if row else GENESIS

    def record(self, actor: str, role: str, action: str, resource: str,
               detail: dict | None = None) -> str:
        """Append one entry and return its hash."""
        ts = datetime.now(timezone.utc).isoformat()
        body = json.dumps(detail or {}, separators=(",", ":"), sort_keys=True)
        with _LOCK:
            prev = self.head()
            row_hash = _digest(ts, actor, role, action, resource, body, prev)
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO audit_log (ts, actor, role, action, resource, detail,"
                    " prev_hash, row_hash) VALUES (?,?,?,?,?,?,?,?)",
                    (ts, actor, role, action, resource, body, prev, row_hash),
                )
                conn.commit()
        return row_hash

    def verify_chain(self) -> dict:
        """Recompute every hash. Reports the first row where the chain breaks."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM audit_log ORDER BY seq").fetchall()

        expected_prev = GENESIS
        for row in rows:
            if row["prev_hash"] != expected_prev:
                return {
                    "valid": False, "entries": len(rows), "broken_at_seq": row["seq"],
                    "reason": "previous-hash link does not match the row before it",
                }
            recomputed = _digest(
                row["ts"], row["actor"], row["role"], row["action"],
                row["resource"], row["detail"], row["prev_hash"],
            )
            if recomputed != row["row_hash"]:
                return {
                    "valid": False, "entries": len(rows), "broken_at_seq": row["seq"],
                    "reason": "row contents do not match their recorded hash",
                }
            expected_prev = row["row_hash"]

        return {
            "valid": True, "entries": len(rows), "head": expected_prev,
            "note": "Tamper-evident: any edit to a historical row breaks every hash after "
                    "it. Not tamper-proof — publishing the head hash externally would be "
                    "needed to detect a full-chain rewrite.",
        }

    def tail(self, limit: int = 50) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT seq, ts, actor, role, action, resource, row_hash"
                " FROM audit_log ORDER BY seq DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(r) for r in rows]
