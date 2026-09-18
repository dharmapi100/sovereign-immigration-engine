import unittest
import os
import sys
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/compliance-dashboard'))
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