import unittest
import sys
import os
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/policy-matching'))
from matcher import PolicyMatcher

class TestPolicyMatcher(unittest.TestCase):
    def test_match(self):
        rules = {"degree_level": 1, "experience_years": 2}
        matcher = PolicyMatcher(rules)
        applicant = {"degree_level": 2, "experience_years": 3}
        result = matcher.match_visa(applicant)
        self.assertTrue(result["eligible"])

if __name__ == '__main__':
    unittest.main()