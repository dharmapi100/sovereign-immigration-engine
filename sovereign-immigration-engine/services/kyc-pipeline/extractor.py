from PIL import Image
import pytesseract
import json
from sovereign_sidecar.encryptor import SovereignEncryptor

class KYCInjestor:
    def __init__(self):
        self.encryptor = SovereignEncryptor(key_file="secure.key")

    def process_document(self, image_path: str) -> dict:
        # local ocr
        text = pytesseract.image_to_string(Image.open(image_path))
        # secure data immediately
        return self.encryptor.secure_sensor_input({"raw_text": text})
