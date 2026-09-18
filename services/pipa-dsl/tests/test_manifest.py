import json
import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, "services")) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, "services/pipa-dsl"))

from manifest import build_manifest  # noqa: E402


class TestManifest(unittest.TestCase):
    def setUp(self):
        self.m = build_manifest()
        self.by_article = {r["article"]: r for r in self.m["rules"]}

    def test_three_articles(self):
        self.assertEqual(set(self.by_article), {"Art.21", "Art.22", "Art.39"})

    def test_enforcement_order(self):
        self.assertEqual(self.m["enforcement_order"], ["Art.21", "Art.39", "Art.22"])

    def test_art22_patterns_and_actions(self):
        pats = {p["name"]: p["action"] for p in self.by_article["Art.22"]["patterns"]}
        self.assertEqual(pats["rrn"], "block")           # hard-block class
        self.assertEqual(pats["passport"], "redact")
        self.assertEqual(pats["phone"], "redact")
        self.assertEqual(pats["bank_acct"], "redact")

    def test_every_rule_cites_statute(self):
        for r in self.m["rules"]:
            self.assertIn("개인정보 보호법", r["citation"])
            self.assertTrue(r["citation"])

    def test_header_rules_disabled_by_default(self):
        self.assertFalse(self.by_article["Art.21"]["enabled"])
        self.assertFalse(self.by_article["Art.39"]["enabled"])
        self.assertEqual(self.by_article["Art.21"]["header"], "X-PIPA-Consent")

    def test_json_roundtrip(self):
        blob = json.dumps(self.m, ensure_ascii=False)
        self.assertEqual(json.loads(blob)["version"], "1.0")


if __name__ == "__main__":
    unittest.main()
