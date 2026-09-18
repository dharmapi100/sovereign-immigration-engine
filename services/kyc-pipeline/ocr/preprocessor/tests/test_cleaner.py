import unittest
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/kyc-pipeline/ocr/preprocessor'))
from image_cleaner import ImageCleaner  # noqa: E402

try:
    import cv2  # noqa: F401
    from PIL import Image  # noqa: F401
    HAS_CV = True
except ImportError:
    HAS_CV = False


@unittest.skipUnless(HAS_CV, "cv2/PIL not installed")
class TestImageCleaner(unittest.TestCase):
    def test_preprocess(self):
        from PIL import Image
        img_path = 'dummy.png'
        Image.new('L', (100, 100), color=200).save(img_path)
        cleaner = ImageCleaner()
        cleaned_path = cleaner.preprocess(img_path)
        self.assertTrue(os.path.exists(cleaned_path))
        os.remove(img_path)
        os.remove(cleaned_path)


if __name__ == '__main__':
    unittest.main()