import unittest
import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/notification-gateway')
from gateway import NotificationGateway

class TestGateway(unittest.TestCase):
    def test_status(self):
        gateway = NotificationGateway()
        status = gateway.check_status("talent_1")
        self.assertEqual(status, "PROCESSING")

if __name__ == '__main__':
    unittest.main()
