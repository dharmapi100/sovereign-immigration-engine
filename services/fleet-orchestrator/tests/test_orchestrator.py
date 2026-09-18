import sys
import os
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/fleet-orchestrator'))
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