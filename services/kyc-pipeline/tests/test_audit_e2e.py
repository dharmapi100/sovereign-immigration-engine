import unittest
from cryptography.fernet import Fernet
import json
import os
import sys

sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline')
from ingestion import KYCExtractor

class TestAuditE2E(unittest.TestCase):
    def test_audit_log(self):
        log_file = "access_audit.log"
        if os.path.exists(log_file): os.remove(log_file)
        
        key = Fernet.generate_key()
        cipher = Fernet(key)
        visa_rules = {"id": True}
        policy_rules = {"id": 1}
        extractor = KYCExtractor(key, visa_rules, policy_rules)
        
        data = {"id": "talent_99", "visa": "D-10-2"}
        encrypted = cipher.encrypt(json.dumps(data).encode('utf-8'))
        extractor.extract_pii(encrypted)
        
        self.assertTrue(os.path.exists(log_file))
        with open(log_file, "r") as f:
            self.assertIn("talent_99", f.read())
            
        os.remove(log_file)

if __name__ == '__main__':
    unittest.main()
