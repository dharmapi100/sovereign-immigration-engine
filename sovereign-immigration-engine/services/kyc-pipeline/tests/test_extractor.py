import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline')
from ingestion import KYCExtractor

class TestKYCExtractor(unittest.TestCase):
    def test_extract_pii(self):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        extractor = KYCExtractor(key)
        data = {"id": "K12345", "name": "Talent", "doc_type": "passport"}
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        result = extractor.extract_pii(encrypted)
        self.assertEqual(data, result)

if __name__ == '__main__':
    unittest.main()
