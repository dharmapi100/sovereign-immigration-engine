import unittest
import sys
import os
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/visa-validation'))
from validator import VisaValidator

class TestVisaValidator(unittest.TestCase):
    def test_validate(self):
        rules = {"id": True, "visa": True}
        validator = VisaValidator(rules)
        applicant = {"id": "talent_1"}
        result = validator.validate_application(applicant)
        self.assertFalse(result["valid"])
        self.assertIn("visa", result["missing"])

if __name__ == '__main__':
    unittest.main()