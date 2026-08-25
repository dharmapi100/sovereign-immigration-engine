from cryptography.fernet import Fernet
import json
import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline/ocr')
from processor import OCRProcessor

from preprocessor.image_cleaner import ImageCleaner
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/compliance-dashboard')
from logger import AuditLogger

class KYCExtractor:
    def __init__(self, key: bytes):
        self.cipher = Fernet(key)
        self.ocr = OCRProcessor()
        self.cleaner = ImageCleaner()
        self.logger = AuditLogger()

    def extract_pii(self, encrypted_doc: bytes, image_path: str = None) -> dict:
        # PIPA compliant local PII extraction
        decrypted = self.cipher.decrypt(encrypted_doc)
        data = json.loads(decrypted.decode('utf-8'))
        if image_path:
            cleaned_path = self.cleaner.preprocess(image_path)
            data['ocr_text'] = self.ocr.extract_text(cleaned_path)
        self.logger.log_access(data.get("id"), "PII_EXTRACT")
        return data
