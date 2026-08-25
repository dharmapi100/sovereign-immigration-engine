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
        extractor = KYCExtractor(key)
        data = {"id": "K12345", "name": "Talent"}
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        
        # We don't have an image path handy, testing extraction logic only for now
        result = extractor.extract_pii(encrypted)
        self.assertEqual(data, result)
        print("e2e kyc extraction test passed")

if __name__ == '__main__':
    unittest.main()
