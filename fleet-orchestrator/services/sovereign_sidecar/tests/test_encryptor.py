import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from encryptor import SovereignEncryptor

class TestSovereignEncryptor(unittest.TestCase):
    def test_encryption_decryption(self):
        encryptor = SovereignEncryptor(key_file="test.key")
        data = {"sensor_id": "robot_01", "reading": 42.5}
        encrypted = encryptor.secure_sensor_input(data)
        decrypted = encryptor.decrypt_sensor_input(encrypted)
        self.assertEqual(data, decrypted)
        if os.path.exists("test.key"): os.remove("test.key")

if __name__ == '__main__':
    unittest.main()
