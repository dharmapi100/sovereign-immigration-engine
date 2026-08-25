import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline')
from ingestion import KYCIngestor

class TestKYCIngestor(unittest.TestCase):
    def test_ingestion(self):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        ingestor = KYCIngestor(key)
        data = {"id": "123", "name": "user"}
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        result = ingestor.process_document(encrypted)
        self.assertEqual(data, result)

if __name__ == '__main__':
    unittest.main()
