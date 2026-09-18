import unittest
import os
import json
import sys
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/compliance-dashboard'))
sys.path.insert(0, os.path.join(_ROOT, 'services/monitor'))
from audit_monitor import AuditMonitor

class TestAuditMonitor(unittest.TestCase):
    def test_alert(self):
        log_file = "access_audit.log"
        with open(log_file, "w") as f:
            f.write(json.dumps({"action": "PII_EXTRACT_UNAUTHORIZED", "talent_id": "bad_actor"}) + "\n")
        
        monitor = AuditMonitor(log_file)
        self.assertTrue(monitor.scan_for_unauthorized_access())
        os.remove(log_file)

if __name__ == '__main__':
    unittest.main()