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