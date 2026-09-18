import unittest
import os
import sys

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/kyc-pipeline/ocr/preprocessor/anonymizer'))
from pii_scrubber import PIIScrubber  # noqa: E402

try:
    import cv2  # noqa: F401
    from PIL import Image  # noqa: F401
    HAS_CV = True
except ImportError:
    HAS_CV = False


@unittest.skipUnless(HAS_CV, "cv2/PIL not installed")
class TestPIIScrubber(unittest.TestCase):
    def test_mask(self):
        from PIL import Image
        img_path = 'test_mask.png'
        Image.new('RGB', (100, 100), color='white').save(img_path)
        scrubber = PIIScrubber()
        scrubbed_path = scrubber.mask_pii(img_path)
        self.assertTrue(os.path.exists(scrubbed_path))
        os.remove(img_path)
        os.remove(scrubbed_path)


if __name__ == '__main__':
    unittest.main()