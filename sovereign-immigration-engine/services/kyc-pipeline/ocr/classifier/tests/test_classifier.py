import unittest
import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline/ocr/classifier')
from doc_classifier import DocumentClassifier

class TestClassifier(unittest.TestCase):
    def test_classify(self):
        classifier = DocumentClassifier()
        category = classifier.classify("This is a passport document")
        self.assertEqual(category, "passport")

if __name__ == '__main__':
    unittest.main()
