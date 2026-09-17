import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline')
from ingestion import KYCExtractor

class TestKYCSimulation(unittest.TestCase):
    def test_high_volume_onboarding(self):
        key = Fernet.generate_key()
        cipher = Fernet(key)
        extractor = KYCExtractor(key)
        
        # Simulate 20 applicants
        for i in range(20):
            data = {"id": f"talent_{i}", "visa": "D-10-2"}
            encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
            result = extractor.extract_pii(encrypted)
            self.assertEqual(data, result)
        print("simulation passed")

if __name__ == '__main__':
    unittest.main()
