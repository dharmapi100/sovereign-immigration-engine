"""
Sovereign Audit Ledger
======================
Tamper-evident, PIPA-compliant audit trail for immigration processing.

Every entry is cryptographically chained to the previous one:
    hash_n = SHA256(entry_payload || hash_{n-1})

This mirrors the guardrail-proxy audit ledger (Go) so both products emit
the same evidence format. The genesis hash is 32 zero-hex chars.

PIPA mapping:
    - Art. 21 (Consent):    every access recorded with actor + purpose
    - Art. 22 (Minimization): payload is pre-redacted, only hashes stored
    - Art. 39 (Retention):  entries are append-only and KISA-timestamped
"""

from __future__ import annotations

import hashlib
import json
import os
import sqlite3
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

GENESIS_HASH = "0" * 32

SCHEMA = """
CREATE TABLE IF NOT EXISTS audit_log (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp      TEXT    NOT NULL,
    entry_id       TEXT    NOT NULL,
    action         TEXT    NOT NULL,
    actor          TEXT    NOT NULL,
    purpose        TEXT,
    payload_hash   TEXT    NOT NULL,
    hash           TEXT    NOT NULL,
    prev_hash      TEXT    NOT NULL,
    pii_detected   INTEGER NOT NULL DEFAULT 0,
    kisa_timestamp TEXT
);
CREATE INDEX IF NOT EXISTS idx_audit_hash ON audit_log(hash);
"""


@dataclass
class AuditEntry:
    """A single audit record. Only non-sensitive metadata is persisted."""
    entry_id: str
    action: str
    actor: str
    purpose: str = ""
    pii_detected: bool = False
    payload: Optional[dict] = field(default=None, repr=False)

    def payload_hash(self) -> str:
        """SHA-256 of the full payload — the payload itself is never stored."""
        blob = json.dumps(self.payload or {}, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class AuditLedger:
    """
    Append-only, hash-chained audit ledger backed by SQLite.

    Thread-safe: a single lock serialises appends so the chain never forks.
    """

    def __init__(self, db_path: str = "sovereign_audit.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.executescript(SCHEMA)
        self._conn.commit()
        self._last_hash = self._recover_last_hash()

    # ------------------------------------------------------------------ #
    # internals
    # ------------------------------------------------------------------ #
    def _recover_last_hash(self) -> str:
        row = self._conn.execute(
            "SELECT hash FROM audit_log ORDER BY id DESC LIMIT 1"
        ).fetchone()
        return row[0] if row else GENESIS_HASH

    @staticmethod
    def _chain(payload_hash: str, prev_hash: str) -> str:
        h = hashlib.sha256()
        h.update(payload_hash.encode("utf-8"))
        h.update(prev_hash.encode("utf-8"))
        return h.hexdigest()

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    # ------------------------------------------------------------------ #
    # public API
    # ------------------------------------------------------------------ #
    def append(self, entry: AuditEntry) -> str:
        """Append an entry and return its chain hash."""
        with self._lock:
            payload_hash = entry.payload_hash()
            new_hash = self._chain(payload_hash, self._last_hash)
            self._conn.execute(
                """INSERT INTO audit_log
                   (timestamp, entry_id, action, actor, purpose,
                    payload_hash, hash, prev_hash, pii_detected)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    self._now(),
                    entry.entry_id,
                    entry.action,
                    entry.actor,
                    entry.purpose,
                    payload_hash,
                    new_hash,
                    self._last_hash,
                    1 if entry.pii_detected else 0,
                ),
            )
            self._conn.commit()
            self._last_hash = new_hash
            return new_hash

    def record_transaction(self, entry_id: str, status: str) -> str:
        """Backwards-compatible helper used by earlier tests."""
        return self.append(
            AuditEntry(entry_id=entry_id, action=status, actor="system")
        )

    def attach_kisa_timestamp(self, chain_hash: str, kisa_ts: str) -> None:
        """Store a KISA RFC-3161 timestamp for a given chain hash."""
        with self._lock:
            self._conn.execute(
                "UPDATE audit_log SET kisa_timestamp = ? WHERE hash = ?",
                (kisa_ts, chain_hash),
            )
            self._conn.commit()

    def verify_chain(self) -> bool:
        """Recompute the chain. Returns True if the ledger is intact."""
        prev = GENESIS_HASH
        for payload_hash, stored_hash, prev_hash in self._conn.execute(
            "SELECT payload_hash, hash, prev_hash FROM audit_log ORDER BY id ASC"
        ):
            if prev_hash != prev:
                return False
            if self._chain(payload_hash, prev) != stored_hash:
                return False
            prev = stored_hash
        return True

    def get(self, chain_hash: str) -> Optional[dict]:
        row = self._conn.execute(
            """SELECT timestamp, entry_id, action, actor, purpose,
                      payload_hash, hash, prev_hash, pii_detected, kisa_timestamp
               FROM audit_log WHERE hash = ?""",
            (chain_hash,),
        ).fetchone()
        if not row:
            return None
        keys = [
            "timestamp", "entry_id", "action", "actor", "purpose",
            "payload_hash", "hash", "prev_hash", "pii_detected",
            "kisa_timestamp",
        ]
        return dict(zip(keys, row))

    def count(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM audit_log").fetchone()[0]

    def close(self) -> None:
        self._conn.close()


if __name__ == "__main__":
    import sys

    path = sys.argv[1] if len(sys.argv) > 1 else "sovereign_audit.db"
    ledger = AuditLedger(path)
    h1 = ledger.append(AuditEntry("v-1001", "VISA_APPLICATION", "officer.kim",
                                  purpose="D-8-4 review", pii_detected=True))
    h2 = ledger.append(AuditEntry("v-1001", "DOC_CLASSIFIED", "ocr.worker",
                                  purpose="passport extraction"))
    print(f"entries={ledger.count()} intact={ledger.verify_chain()}")
    print(f"h1={h1}\nh2={h2}")
    ledger.close()