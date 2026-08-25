import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/fleet-orchestrator/src')
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/fleet-orchestrator/services')
from graph import app
import unittest

class TestStress(unittest.TestCase):
    def test_high_volume_dispatch(self):
        # Stress test: 50 cycles
        state = {'robot_ids': ['hyundai_01', 'sme_01'], 'tasks': [], 'assignments': {}, 'error_report': {}}
        for _ in range(50):
            result = app.invoke(state)
            self.assertIn('assignments', result)
        print("stress test passed")

if __name__ == '__main__':
    unittest.main()
