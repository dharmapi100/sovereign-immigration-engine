import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, "services")) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, "services/visa-policy"))

from engine import PolicyConfig, VisaPolicyEngine  # noqa: E402


class TestVisaPolicyEngine(unittest.TestCase):
    def setUp(self):
        self.e = VisaPolicyEngine()

    def test_d84_full_founder_eligible(self):
        a = {
            "investment_capital_krw": 150_000_000,
            "business_plan": True,
            "incubator_letter": True,
            "ip_assets": ["patent"],
        }
        r = self.e.evaluate("D-8-4", a)
        self.assertTrue(r.eligible)
        self.assertEqual(r.score, r.max_score)
        self.assertEqual(r.missing, [])

    def test_d84_underfunded_blocked(self):
        a = {"investment_capital_krw": 50_000_000, "business_plan": True,
             "incubator_letter": True, "ip_assets": ["patent"]}
        r = self.e.evaluate("D-8-4", a)
        self.assertFalse(r.eligible)
        self.assertIn("D84-CAP", r.missing)

    def test_e7_degree_or_experience(self):
        a = {"degree": "bachelor", "job_offer": True,
             "salary_krw": 40_000_000, "occupation_in_list": True}
        self.assertTrue(self.e.evaluate("E-7", a).eligible)
        # no degree but 6 years experience still passes the degree rule
        b = {"degree": "", "experience_years": 6, "job_offer": True,
             "salary_krw": 40_000_000, "occupation_in_list": True}
        self.assertNotIn("E7-DEGREE", self.e.evaluate("E-7", b).missing)

    def test_e9_age_bounds(self):
        ok = {"age": 25, "eps_topik_passed": True, "employer_sponsorship": True}
        self.assertTrue(self.e.evaluate("E-9", ok).eligible)
        old = {"age": 45, "eps_topik_passed": True, "employer_sponsorship": True}
        self.assertIn("E9-AGE", self.e.evaluate("E-9", old).missing)

    def test_d10_points(self):
        a = {"degree": "master", "age": 27, "topik_level": "topik_5",
             "income_krw": 35_000_000, "korean_university_grad": True}
        r = self.e.evaluate("D-10", a)
        self.assertTrue(r.eligible)

    def test_every_decision_has_citation(self):
        r = self.e.evaluate("D-8-4", {})
        for rule in r.results:
            self.assertTrue(rule.citation)
            self.assertTrue(rule.rule_id)

    def test_evaluate_all_returns_four(self):
        results = self.e.evaluate_all({})
        self.assertEqual(len(results), 4)
        self.assertEqual({r.visa for r in results}, {"D-8-4", "E-7", "E-9", "D-10"})

    def test_config_tunable(self):
        strict = VisaPolicyEngine(PolicyConfig(d84_min_capital_krw=500_000_000))
        a = {"investment_capital_krw": 150_000_000, "business_plan": True,
             "incubator_letter": True, "ip_assets": ["patent"]}
        self.assertFalse(strict.evaluate("D-8-4", a).eligible)


if __name__ == "__main__":
    unittest.main()