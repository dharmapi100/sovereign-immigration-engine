import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from manager import RobotManager

class TestRobotManager(unittest.TestCase):
    def test_manager_dispatch(self):
        manager = RobotManager()
        status = manager.get_all_status()
        self.assertIn("hyundai", status)
        self.assertTrue(manager.dispatch("hyundai", {"task": "test"}))

if __name__ == '__main__':
    unittest.main()
