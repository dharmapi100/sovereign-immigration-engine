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

class TestKYCIngestor(unittest.TestCase):
    def test_ingestion(self):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        visa_rules = {"id": True}
        policy_rules = {"id": 1}
        extractor = KYCExtractor(key, visa_rules, policy_rules)
        data = {"id": "123", "name": "user"}
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        result = extractor.extract_pii(encrypted)
        self.assertEqual(data["id"], result["id"])

if __name__ == '__main__':
    unittest.main()