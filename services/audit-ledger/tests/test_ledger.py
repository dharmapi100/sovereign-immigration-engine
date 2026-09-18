import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # services/audit-ledger

from ledger import AuditEntry, AuditLedger, GENESIS_HASH  # noqa: E402
from kisa_client import KISATimestampClient  # noqa: E402
from evidence import EvidenceService  # noqa: E402


class TestAuditLedger(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.ledger = AuditLedger(self.tmp.name)

    def tearDown(self):
        self.ledger.close()
        os.unlink(self.tmp.name)

    def test_append_chains(self):
        h1 = self.ledger.append(AuditEntry("v1", "APPLY", "officer.kim"))
        h2 = self.ledger.append(AuditEntry("v1", "REVIEW", "officer.kim"))
        self.assertNotEqual(h1, h2)
        self.assertEqual(self.ledger.get(h2)["prev_hash"], h1)
        self.assertTrue(self.ledger.verify_chain())

    def test_genesis_prev_hash(self):
        h1 = self.ledger.append(AuditEntry("v1", "APPLY", "system"))
        self.assertEqual(self.ledger.get(h1)["prev_hash"], GENESIS_HASH)

    def test_tamper_detected(self):
        self.ledger.append(AuditEntry("v1", "APPLY", "a"))
        self.ledger.append(AuditEntry("v2", "APPLY", "b"))
        self.assertTrue(self.ledger.verify_chain())
        # corrupt a stored hash directly
        self.ledger._conn.execute(
            "UPDATE audit_log SET hash = 'deadbeef' WHERE id = 1"
        )
        self.ledger._conn.commit()
        self.assertFalse(self.ledger.verify_chain())

    def test_payload_never_stored(self):
        secret = {"rrn": "900101-1234567"}
        self.ledger.append(AuditEntry("v1", "APPLY", "a", payload=secret))
        row = self.ledger.get(
            self.ledger._conn.execute(
                "SELECT hash FROM audit_log LIMIT 1"
            ).fetchone()[0]
        )
        self.assertNotIn("900101-1234567", str(row))

    def test_record_transaction_compat(self):
        self.ledger.record_transaction("T1", "SUCCESS")
        self.assertEqual(self.ledger.count(), 1)
        self.assertTrue(self.ledger.verify_chain())

    def test_kisa_disabled_is_noop(self):
        client = KISATimestampClient(enabled=False)
        self.assertIsNone(client.request_timestamp("abc"))

    def test_kisa_attach(self):
        h = self.ledger.append(AuditEntry("v1", "APPLY", "a"))
        self.ledger.attach_kisa_timestamp(h, "2026-09-17T00:00:00Z")
        self.assertEqual(
            self.ledger.get(h)["kisa_timestamp"], "2026-09-17T00:00:00Z"
        )

    def test_evidence_service(self):
        svc = EvidenceService(self.ledger, KISATimestampClient(enabled=False))
        rec = svc.record("v1", "VISA_APPLICATION", "officer.kim",
                         payload={"visa": "D-8-4"}, pii_detected=True)
        self.assertFalse(rec["timestampped"])  # TSA disabled
        self.assertTrue(self.ledger.verify_chain())


if __name__ == "__main__":
    unittest.main()