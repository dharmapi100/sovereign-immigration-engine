import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # services/kyc-pipeline

from ingestion import KYCExtractor  # noqa: E402


def _encrypt(key, data):
    return Fernet(key).encrypt(json.dumps(data).encode("utf-8"))


class TestKYCE2E(unittest.TestCase):
    def setUp(self):
        self.key = Fernet.generate_key()
        self.visa_rules = {"id": True, "name": True}
        self.policy_rules = {"name_len": 5}
        self.extractor = KYCExtractor(self.key, self.visa_rules, self.policy_rules)

    def test_extraction_with_consent(self):
        data = {"id": "K12345", "name": "Talent", "consent": True}
        result = self.extractor.extract_pii(_encrypt(self.key, data))
        self.assertEqual(result["id"], "K12345")
        self.assertTrue(result["validation"]["valid"])
        self.assertEqual(len(result["pipa"]), 3)  # Art.21, 39, 22 all evaluated

    def test_pipeline_blocks_without_consent(self):
        data = {"id": "K99999", "name": "Talent"}  # no consent
        result = self.extractor.extract_pii(_encrypt(self.key, data))
        self.assertFalse(result["validation"]["valid"])
        self.assertEqual(result["validation"]["article"], "Art.21")

    def test_pipeline_redacts_pii_in_output(self):
        data = {
            "id": "K77777",
            "name": "Talent",
            "consent": True,
            "ocr_text":  "신청인 900101-1234567",
        }
        result = self.extractor.extract_pii(_encrypt(self.key, data))
        self.assertIn("RRN_REDACTED", result["ocr_text"])
        self.assertNotIn("900101-1234567", result["ocr_text"])

    def test_audit_chain_intact_after_run(self):
        self.extractor.extract_pii(
            _encrypt(self.key, {"id": "K1", "name": "T", "consent": True})
        )
        self.assertTrue(self.extractor.ledger.verify_chain())


if __name__ == "__main__":
    unittest.main()