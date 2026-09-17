import unittest
import sys
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/visa-validation')
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
