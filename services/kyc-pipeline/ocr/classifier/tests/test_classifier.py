import unittest
import sys
import os
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/kyc-pipeline/ocr/classifier'))
from doc_classifier import DocumentClassifier

class TestClassifier(unittest.TestCase):
    def test_classify(self):
        classifier = DocumentClassifier()
        category = classifier.classify("This is a passport document")
        self.assertEqual(category, "passport")

if __name__ == '__main__':
    unittest.main()