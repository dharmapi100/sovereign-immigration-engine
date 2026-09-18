import unittest
from cryptography.fernet import Fernet
import json
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/kyc-pipeline'))
from ingestion import KYCExtractor


class TestAuditE2E(unittest.TestCase):
    def test_access_log_written(self):
        log_file = "access_audit.log"
        if os.path.exists(log_file):
            os.remove(log_file)

        key = Fernet.generate_key()
        cipher = Fernet(key)
        extractor = KYCExtractor(key, {"id": True}, {"id": 1})

        data = {"id": "talent_99", "visa": "D-10-2", "consent": True}
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        extractor.extract_pii(encrypted)

        self.assertTrue(os.path.exists(log_file))
        with open(log_file, "r") as f:
            self.assertIn("talent_99", f.read())

        # evidence ledger chain must be intact
        self.assertTrue(extractor.ledger.verify_chain())

        os.remove(log_file)


if __name__ == '__main__':
    unittest.main()