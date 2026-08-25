from cryptography.fernet import Fernet
import json
import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline/ocr')
from processor import OCRProcessor

class KYCExtractor:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
        self.ocr = OCRProcessor()

    def extract_pii(self, encrypted_doc: bytes, image_path: str = None) -> dict:
        # PIPA compliant local PII extraction
        decrypted = self.cipher.decrypt(encrypted_doc)
        data = json.loads(decrypted.decode('utf-8'))
        if image_path:
            data['ocr_text'] = self.ocr.extract_text(image_path)
        return data
