import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/fleet-orchestrator')
import unittest
from orchestrator import FleetOrchestrator

class TestFleetOrchestrator(unittest.TestCase):
    def test_distribute_task(self):
        orchestrator = FleetOrchestrator()
        orchestrator.register_node("node-1")
        result = orchestrator.distribute_task({"id": "T1"})
        self.assertEqual(result["status"], "dispatched")

if __name__ == '__main__':
    unittest.main()
