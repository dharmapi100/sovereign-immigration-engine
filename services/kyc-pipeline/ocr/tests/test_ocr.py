import unittest
import sys
import os

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/kyc-pipeline/ocr'))
from processor import OCRProcessor  # noqa: E402

try:
    import easyocr  # noqa: F401
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False


class TestOCR(unittest.TestCase):
    def test_constructs_without_loading_model(self):
        # OCR model is lazy — constructing must not require easyocr at import time
        processor = OCRProcessor()
        self.assertIsNone(processor._reader)  # not loaded yet

    @unittest.skipUnless(HAS_EASYOCR, "easyocr not installed")
    def test_reader_loads(self):
        processor = OCRProcessor()
        self.assertIsNotNone(processor._ensure_reader())


if __name__ == '__main__':
    unittest.main()