import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline')
from ingestion import KYCExtractor

class TestKYCE2E(unittest.TestCase):
    def test_pii_ocr_extraction(self):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        visa_rules = {"id": True, "name": True}
        policy_rules = {"name_len": 5}
        extractor = KYCExtractor(key, visa_rules, policy_rules)
        data = {"id": "K12345", "name": "Talent", "name_len": 6}
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        
        # We don't have an image path handy, testing extraction logic only for now
        result = extractor.extract_pii(encrypted)
        self.assertEqual(data["id"], result["id"])
        self.assertTrue(result["validation"]["valid"])
        print("e2e kyc extraction test passed")

if __name__ == '__main__':
    unittest.main()
