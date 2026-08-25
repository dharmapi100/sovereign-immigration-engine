import unittest
import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/policy-matching')
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
EOF
python3 /Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/policy-matching/tests/test_matcher.py