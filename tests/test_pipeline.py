import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services'))
from pipeline_orchestrator import PipelineOrchestrator


class TestPipeline(unittest.TestCase):
    def test_run(self):
        key = Fernet.generate_key()
        visa_rules = {"degree_level": 1}
        policy_rules = {"degree_level": 1}
        orchestrator = PipelineOrchestrator(key, visa_rules, policy_rules)
        data = {"id": "talent_1", "degree_level": 2, "consent": True}
        encrypted = Fernet(key).encrypt(json.dumps(data).encode('utf-8'))
        result = orchestrator.run_pipeline(encrypted, None)
        self.assertTrue(result["validation"]["valid"])
        self.assertEqual(len(result["pipa"]), 3)


if __name__ == '__main__':
    unittest.main()