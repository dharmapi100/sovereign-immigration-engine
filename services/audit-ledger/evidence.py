"""
Evidence Service
================
Single entry point that writes to the audit ledger and, when KISA is
configured, attaches a trusted timestamp. This is the module every other
pipeline stage calls so the evidence format stays consistent.

Usage:
    svc = EvidenceService(ledger, kisa_client)
    svc.record("VISA_APPLICATION", "officer.kim", payload={...}, purpose="D-8-4")
"""

from __future__ import annotations

from typing import Optional

from ledger import AuditEntry, AuditLedger
from kisa_client import KISATimestampClient


class EvidenceService:
    def __init__(self, ledger: AuditLedger, kisa: Optional[KISATimestampClient] = None):
        self.ledger = ledger
        self.kisa = kisa or KISATimestampClient(enabled=False)

    def record(
        self,
        entry_id: str,
        action: str,
        actor: str,
        payload: Optional[dict] = None,
        purpose: str = "",
        pii_detected: bool = False,
    ) -> dict:
        """
        Append an audit entry and (best-effort) attach a KISA timestamp.

        Returns the stored record plus a boolean `timestampped` flag so
        callers can see whether the TSA confirmed in time.
        """
        chain_hash = self.ledger.append(
            AuditEntry(
                entry_id=entry_id,
                action=action,
                actor=actor,
                purpose=purpose,
                pii_detected=pii_detected,
                payload=payload,
            )
        )

        timestampped = False
        ts = self.kisa.request_timestamp(chain_hash)
        if ts:
            self.ledger.attach_kisa_timestamp(chain_hash, ts)
            timestampped = True

        record = self.ledger.get(chain_hash) or {}
        record["timestampped"] = timestampped
        return record