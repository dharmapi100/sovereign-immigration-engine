import unittest
import os
import json
import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/compliance-dashboard')
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/monitor')
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
EOF
python3 /Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/monitor/tests/test_monitor.py
