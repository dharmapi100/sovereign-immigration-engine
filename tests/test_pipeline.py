import unittest
from cryptography.fernet import Fernet
import json
import sys
import os

sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services')
from pipeline_orchestrator import PipelineOrchestrator

class TestPipeline(unittest.TestCase):
    def test_run(self):
        key = Fernet.generate_key()
        rules = {"degree_level": 1}
        orchestrator = PipelineOrchestrator(key, rules)
        data = {"id": "talent_1", "degree_level": 2}
        encrypted = Fernet(key).encrypt(json.dumps(data).encode('utf-8'))
        result = orchestrator.run_pipeline(encrypted, None)
        self.assertTrue(result["eligible"])

if __name__ == '__main__':
    unittest.main()
