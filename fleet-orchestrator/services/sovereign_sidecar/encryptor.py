from cryptography.fernet import Fernet
import os
import json

class SovereignEncryptor:
    def __init__(self, key_file="secret.key"):
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                self.key = f.read()
        else:
            self.key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self.key)
        self.cipher = Fernet(self.key)

    def secure_sensor_input(self, data: dict) -> bytes:
        # Serializes and encrypts sensor telemetry
        serialized = json.dumps(data).encode('utf-8')
        return self.cipher.encrypt(serialized)

    def decrypt_sensor_input(self, token: bytes) -> dict:
        decrypted = self.cipher.decrypt(token)
        return json.loads(decrypted.decode('utf-8'))
