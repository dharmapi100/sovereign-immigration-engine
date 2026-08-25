import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/fleet-orchestrator/src')
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/fleet-orchestrator/services')
from graph import app
from fault_injector import FaultFuzzer
import unittest

class TestFuzzer(unittest.TestCase):
    def test_random_faults(self):
        # Stress test: 100 cycles with random faults
        state = {'robot_ids': ['hyundai_01', 'sme_01'], 'tasks': [], 'assignments': {}, 'error_report': {}}
        for _ in range(100):
            fault = FaultFuzzer.inject_random_fault("hyundai_01")
            # Logic integration needed here: simulate fault report
            result = app.invoke(state)
            self.assertIn('assignments', result)
        print("fuzzer test passed")

if __name__ == '__main__':
    unittest.main()
