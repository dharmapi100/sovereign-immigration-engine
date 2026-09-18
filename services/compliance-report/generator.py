"""
Compliance Report Generator
===========================
Produces the evidence artifact you hand to a regulator or acquirer: a
self-hashing document that ties together

    * the visa decision (with statutory citations),
    * the PIPA Article-as-Code decisions, and
    * a proof over the audit chain segment (hashes + integrity status).

The report itself carries a SHA-256 over its canonical body, so any later
edit invalidates it — the artifact is tamper-evident, not just the ledger.

Output: JSON (machine) and Markdown (human/PDF-ready).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, "services")) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
for _p in ["services/audit-ledger", "services/visa-policy", "services/pipa-dsl"]:
    _full = os.path.join(_ROOT, _p)
    if _full not in sys.path:
        sys.path.insert(0, _full)

from ledger import AuditLedger  # noqa: E402


@dataclass
class ComplianceReport:
    applicant_id: str
    generated_at: str
    visa_decisions: list[dict]
    pipa_decisions: list[dict]
    audit_proof: dict
    report_hash: str = ""

    def _canonical(self) -> bytes:
        body = {
            "applicant_id": self.applicant_id,
            "generated_at": self.generated_at,
            "visa_decisions": self.visa_decisions,
            "pipa_decisions": self.pipa_decisions,
            "audit_proof": self.audit_proof,
        }
        return json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")

    def seal(self) -> "ComplianceReport":
        self.report_hash = hashlib.sha256(self._canonical()).hexdigest()
        return self

    def verify(self) -> bool:
        return self.report_hash == hashlib.sha256(self._canonical()).hexdigest()

    def to_dict(self) -> dict:
        return asdict(self)

    def to_markdown(self) -> str:
        lines = [
            "# Compliance Report",
            "",
            f"- **Applicant:** `{self.applicant_id}`",
            f"- **Generated:** {self.generated_at}",
            f"- **Report SHA-256:** `{self.report_hash}`",
            f"- **Report integrity:** {'VALID' if self.verify() else 'INVALID'}",
            "",
            "## Visa decisions",
            "",
            "| Visa | Eligible | Score | Missing |",
            "|------|----------|-------|---------|",
        ]
        for v in self.visa_decisions:
            lines.append(
                f"| {v['visa']} | {v['eligible']} | {v['score']}/{v['max_score']} "
                f"| {', '.join(v['missing']) or '—'} |"
            )
        lines += ["", "### Rule citations", ""]
        for v in self.visa_decisions:
            for r in v["rules"]:
                mark = "✅" if r["passed"] else "❌"
                lines.append(f"- {mark} `{r['rule_id']}` — {r['reason']}  \n"
                             f"  <sub>{r['citation']}</sub>")

        lines += ["", "## PIPA Article-as-Code", "",
                  "| Article | Outcome | Reason |", "|---------|---------|--------|"]
        for p in self.pipa_decisions:
            lines.append(f"| {p['article']} | {p['outcome']} | {p['reason']} |")

        ap = self.audit_proof
        lines += [
            "", "## Audit-chain proof", "",
            f"- **Entries covered:** {ap['entries']}",
            f"- **Chain intact:** {ap['intact']}",
            f"- **Head hash:** `{ap.get('head_hash', '')}`",
            f"- **KISA-timestamped entries:** {ap.get('kisa_timestamped', 0)}",
            "", "Chain segment:",
            "",
        ]
        for h in ap.get("segment", []):
            lines.append(f"  - `{h}`")

        lines += ["", "---",
                  "_This report is self-hashing: any modification invalidates the "
                  "SHA-256 above. Verify with `report.verify()`._"]
        return "\n".join(lines)


class ReportGenerator:
    def __init__(self, ledger: AuditLedger):
        self.ledger = ledger

    def _audit_proof(self, limit: int = 100) -> dict:
        rows = self.ledger._conn.execute(
            """SELECT hash, prev_hash, kisa_timestamp FROM audit_log
               ORDER BY id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        segment = [r[0] for r in rows][::-1]  # chronological
        kisa = sum(1 for r in rows if r[2])
        return {
            "entries": self.ledger.count(),
            "intact": self.ledger.verify_chain(),
            "head_hash": segment[-1] if segment else "",
            "kisa_timestamped": kisa,
            "segment": segment,
        }

    def generate(
        self,
        applicant_id: str,
        visa_decisions: list[dict],
        pipa_decisions: list[dict],
    ) -> ComplianceReport:
        report = ComplianceReport(
            applicant_id=applicant_id,
            generated_at=datetime.now(timezone.utc).isoformat(),
            visa_decisions=visa_decisions,
            pipa_decisions=pipa_decisions,
            audit_proof=self._audit_proof(),
        )
        return report.seal()


if __name__ == "__main__":
    import os
    import sys

    _ROOT = os.path.dirname(os.path.abspath(__file__))
    while not os.path.isdir(os.path.join(_ROOT, "services")) and os.path.dirname(_ROOT) != _ROOT:
        _ROOT = os.path.dirname(_ROOT)
    for _p in ["services/audit-ledger", "services/visa-policy", "services/pipa-dsl"]:
        sys.path.insert(0, os.path.join(_ROOT, _p))

    from engine import VisaPolicyEngine
    from compiler import PIPACompiler

    ledger = AuditLedger(":memory:")
    from ledger import AuditEntry
    ledger.append(AuditEntry("founder_kim", "VISA_EVALUATE", "api"))

    visa = VisaPolicyEngine()
    pipa = PIPACompiler()
    vd = [visa.evaluate("D-8-4", {
        "investment_capital_krw": 150_000_000, "business_plan": True,
        "incubator_letter": True, "ip_assets": ["patent"]}).to_dict()]
    pd = [d.to_dict() for d in pipa.enforce_plan(
        {"consent": True, "output": "900101-1234567"})]

    report = ReportGenerator(ledger).generate("founder_kim", vd, pd)
    print(report.to_markdown())
    print("\nJSON keys:", list(report.to_dict().keys()))