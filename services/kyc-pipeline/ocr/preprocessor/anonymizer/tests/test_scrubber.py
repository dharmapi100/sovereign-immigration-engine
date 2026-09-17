import unittest
import os
import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline/ocr/preprocessor/anonymizer')
from pii_scrubber import PIIScrubber
from PIL import Image

class TestPIIScrubber(unittest.TestCase):
    def test_mask(self):
        img_path = 'test_mask.png'
        Image.new('RGB', (100, 100), color='white').save(img_path)
        scrubber = PIIScrubber()
        scrubbed_path = scrubber.mask_pii(img_path)
        self.assertTrue(os.path.exists(scrubbed_path))
        os.remove(img_path)
        os.remove(scrubbed_path)

if __name__ == '__main__':
    unittest.main()
