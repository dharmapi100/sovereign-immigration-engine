import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline')
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
