import unittest
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from graph import app, FleetState

class TestFleetGraph(unittest.TestCase):
    def test_orchestrator_execution(self):
        initial_state = {"robot_ids": ["hyundai_01", "sme_01"], "tasks": [], "assignments": {}, "error_report": {}}
        result = app.invoke(initial_state)
        self.assertTrue("assignments" in result)
        self.assertEqual(len(result["assignments"]), 2)

if __name__ == '__main__':
    unittest.main()
