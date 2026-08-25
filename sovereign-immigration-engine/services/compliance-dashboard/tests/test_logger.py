import unittest
import os
import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/compliance-dashboard')
from logger import AuditLogger

class TestAuditLogger(unittest.TestCase):
    def test_log(self):
        log_file = "test_audit.log"
        logger = AuditLogger(log_file=log_file)
        logger.log_access("talent_1", "PII_EXTRACT")
        self.assertTrue(os.path.exists(log_file))
        os.remove(log_file)

if __name__ == '__main__':
    unittest.main()
