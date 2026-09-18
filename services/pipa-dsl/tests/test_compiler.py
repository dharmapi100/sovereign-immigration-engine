import os
import sys
import unittest
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # services/pipa-dsl

from compiler import Outcome, PIPACompiler  # noqa: E402


class TestPIPADSL(unittest.TestCase):
    def setUp(self):
        self.c = PIPACompiler()

    def test_art21_blocks_without_consent(self):
        d = self.c.articles["Art.21"].evaluate({"consent": False})
        self.assertEqual(d.outcome, Outcome.BLOCK)
        self.assertEqual(d.article, "Art.21")

    def test_art21_allows_with_consent(self):
        d = self.c.articles["Art.21"].evaluate({"consent": True})
        self.assertEqual(d.outcome, Outcome.ALLOW)

    def test_art22_redacts_rrn(self):
        d = self.c.articles["Art.22"].evaluate({"output": "900101-1234567"})
        self.assertEqual(d.outcome, Outcome.REDACT)
        self.assertIn("RRN_REDACTED", d.redactions["clean"])
        self.assertNotIn("900101-1234567", d.redactions["clean"])

    def test_art22_redacts_multiple(self):
        d = self.c.articles["Art.22"].evaluate(
            {"output": "900101-1234567 / M1234567"}
        )
        self.assertIn("rrn", d.redactions["counts"])
        self.assertIn("passport", d.redactions["counts"])

    def test_art22_clean_passes(self):
        d = self.c.articles["Art.22"].evaluate({"output": "hello world"})
        self.assertEqual(d.outcome, Outcome.ALLOW)

    def test_art39_expired_blocks(self):
        old = (datetime.now(timezone.utc) - timedelta(days=2000)).isoformat()
        d = self.c.articles["Art.39"].evaluate(
            {"stored_at": old, "retention_days": 1825}
        )
        self.assertEqual(d.outcome, Outcome.BLOCK)

    def test_art39_fresh_allows(self):
        fresh = datetime.now(timezone.utc).isoformat()
        d = self.c.articles["Art.39"].evaluate({"stored_at": fresh})
        self.assertEqual(d.outcome, Outcome.ALLOW)

    def test_enforce_plan_stops_at_block(self):
        decisions = self.c.enforce_plan({"consent": False, "output": "x"})
        self.assertEqual(len(decisions), 1)
        self.assertEqual(decisions[0].outcome, Outcome.BLOCK)

    def test_enforce_plan_full_pass(self):
        decisions = self.c.enforce_plan(
            {"consent": True, "output": "clean", "stored_at": None}
        )
        self.assertEqual(len(decisions), 3)
        self.assertTrue(all(d.outcome == Outcome.ALLOW for d in decisions))

    def test_manifest_has_three_articles(self):
        self.assertEqual(set(self.c.describe()), {"Art.21", "Art.22", "Art.39"})


if __name__ == "__main__":
    unittest.main()