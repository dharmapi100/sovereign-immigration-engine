import unittest
import os
import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline/ocr/preprocessor')
from image_cleaner import ImageCleaner
from PIL import Image

class TestImageCleaner(unittest.TestCase):
    def test_preprocess(self):
        # Create dummy image
        img_path = 'dummy.png'
        Image.new('L', (100, 100), color=200).save(img_path)
        
        cleaner = ImageCleaner()
        cleaned_path = cleaner.preprocess(img_path)
        
        self.assertTrue(os.path.exists(cleaned_path))
        
        # Cleanup
        os.remove(img_path)
        os.remove(cleaned_path)

if __name__ == '__main__':
    unittest.main()
