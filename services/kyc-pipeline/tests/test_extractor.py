import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/kyc-pipeline'))
from ingestion import KYCExtractor


class TestKYCExtractor(unittest.TestCase):
    def test_extract_with_consent(self):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        visa_rules = {"id": True}
        policy_rules = {"id": 1}
        extractor = KYCExtractor(key, visa_rules, policy_rules)
        data = {"id": "K12345", "name": "Talent", "doc_type": "passport",
                "consent": True}
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        result = extractor.extract_pii(encrypted)
        self.assertEqual(data["id"], result["id"])
        self.assertTrue(result["validation"]["valid"])
        self.assertIn("policy_match", result)
        self.assertEqual(len(result["pipa"]), 3)  # Art.21, 39, 22

    def test_extract_blocked_without_consent(self):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        extractor = KYCExtractor(key, {"id": True}, {"id": 1})
        data = {"id": "K54321", "name": "Talent"}  # no consent
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        result = extractor.extract_pii(encrypted)
        self.assertFalse(result["validation"]["valid"])
        self.assertEqual(result["validation"]["article"], "Art.21")


if __name__ == '__main__':
    unittest.main()