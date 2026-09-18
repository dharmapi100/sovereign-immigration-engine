import os
import sys
import unittest

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, "services")) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, "services/compliance-report"))
sys.path.insert(0, os.path.join(_ROOT, "services/audit-ledger"))
sys.path.insert(0, os.path.join(_ROOT, "services/visa-policy"))
sys.path.insert(0, os.path.join(_ROOT, "services/pipa-dsl"))

from generator import ReportGenerator  # noqa: E402
from ledger import AuditEntry, AuditLedger  # noqa: E402
from engine import VisaPolicyEngine  # noqa: E402
from compiler import PIPACompiler  # noqa: E402


class TestComplianceReport(unittest.TestCase):
    def setUp(self):
        self.ledger = AuditLedger(":memory:")
        self.ledger.append(AuditEntry("f1", "VISA_EVALUATE", "api"))
        self.gen = ReportGenerator(self.ledger)
        self.visa = VisaPolicyEngine()
        self.pipa = PIPACompiler()

    def _make(self):
        vd = [self.visa.evaluate("D-8-4", {
            "investment_capital_krw": 150_000_000, "business_plan": True,
            "incubator_letter": True, "ip_assets": ["patent"]}).to_dict()]
        pd = [d.to_dict() for d in self.pipa.enforce_plan(
            {"consent": True, "output": "900101-1234567"})]
        return self.gen.generate("f1", vd, pd)

    def test_sealed_and_verifies(self):
        r = self._make()
        self.assertTrue(r.report_hash)
        self.assertTrue(r.verify())

    def test_tamper_invalidates_report(self):
        r = self._make()
        r.applicant_id = "someone_else"
        self.assertFalse(r.verify())

    def test_includes_audit_proof(self):
        r = self._make()
        self.assertTrue(r.audit_proof["intact"])
        self.assertGreaterEqual(r.audit_proof["entries"], 1)
        self.assertTrue(r.audit_proof["head_hash"])

    def test_markdown_contains_citations(self):
        md = self._make().to_markdown()
        self.assertIn("출입국관리법", md)
        self.assertIn("Art.22", md)
        self.assertIn("Report integrity", md)

    def test_json_roundtrip(self):
        r = self._make()
        d = r.to_dict()
        self.assertIn("report_hash", d)
        self.assertIn("visa_decisions", d)
        self.assertIn("pipa_decisions", d)


if __name__ == "__main__":
    unittest.main()