"""
High-volume onboarding simulation
=================================
Exercises the pipeline across many applicants in one run and proves the
audit chain stays intact end-to-end. Also asserts that appends stay
strictly ordered (no forked chain) under sequential load.
"""

import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, "services")) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, "services/kyc-pipeline"))
from ingestion import KYCExtractor  # noqa: E402


class TestKYCSimulation(unittest.TestCase):
    def setUp(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.extractor = KYCExtractor(self.key, {"id": True}, {"id": 1})

    def _submit(self, data):
        enc = self.cipher.encrypt(json.dumps(data).encode("utf-8"))
        return self.extractor.extract_pii(enc)

    def test_high_volume_onboarding(self):
        for i in range(50):
            data = {"id": f"talent_{i}", "name": "Talent", "consent": True}
            result = self._submit(data)
            self.assertEqual(result["id"], f"talent_{i}")
            self.assertTrue(result["validation"]["valid"])
        # every submission is recorded; chain remains valid
        self.assertGreaterEqual(self.extractor.ledger.count(), 50)
        self.assertTrue(self.extractor.ledger.verify_chain())

    def test_chain_ordering_is_sequential(self):
        prev = None
        for i in range(10):
            self._submit({"id": f"seq_{i}", "consent": True})
        rows = self.extractor.ledger._conn.execute(
            "SELECT prev_hash, hash FROM audit_log ORDER BY id ASC"
        ).fetchall()
        for prev_hash, h in rows:
            if prev is not None:
                self.assertEqual(prev_hash, prev)
            prev = h
        self.assertTrue(self.extractor.ledger.verify_chain())

    def test_blocked_applicants_also_audited(self):
        before = self.extractor.ledger.count()
        self._submit({"id": "no_consent", "name": "X"})  # blocked by Art.21
        self.assertGreater(self.extractor.ledger.count(), before)
        self.assertTrue(self.extractor.ledger.verify_chain())


if __name__ == "__main__":
    unittest.main()