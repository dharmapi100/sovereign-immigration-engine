import unittest
import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline/ocr')
from processor import OCRProcessor

class TestOCR(unittest.TestCase):
    def test_init(self):
        # verifies easyocr reader loads
        processor = OCRProcessor()
        self.assertIsNotNone(processor.reader)

if __name__ == '__main__':
    unittest.main()
