import unittest
import sys
import os
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/notification-gateway'))
from gateway import NotificationGateway

class TestGateway(unittest.TestCase):
    def test_status(self):
        gateway = NotificationGateway()
        status = gateway.check_status("talent_1")
        self.assertEqual(status, "PROCESSING")

if __name__ == '__main__':
    unittest.main()