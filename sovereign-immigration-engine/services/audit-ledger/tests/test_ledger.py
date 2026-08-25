import unittest
import os
import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/audit-ledger')
from ledger import AuditLedger

class TestLedger(unittest.TestCase):
    def test_ledger(self):
        log_file = "access_audit.log"
        with open(log_file, "w") as f:
            f.write('{"id": "t1"}\n')
        
        ledger = AuditLedger(log_file)
        ledger_hash = ledger.generate_ledger_hash()
        self.assertTrue(len(ledger_hash) > 0)
        os.remove(log_file)

if __name__ == '__main__':
    unittest.main()
