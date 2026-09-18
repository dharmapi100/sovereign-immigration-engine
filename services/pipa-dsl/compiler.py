"""
PIPA Article-as-Code Compiler
=============================
Turns Korean Personal Information Protection Act (PIPA) articles into
executable policy. This is the wedge no competitor owns: a DSL where the
legal article *is* the enforcement rule, so auditors can map code→law 1:1.

Articles implemented (KSGC / MSS scope):
    Art. 21 (동의 / Consent)          -> consent gate on input
    Art. 22 (최소수집 / Minimization) -> field-level redaction on output
    Art. 39 (파기 / Retention)        -> time-based retention policy

Each policy compiles to a callable `Decision` so the pipeline can run
`policy.evaluate(context)` and get allow / block / redact with a citation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Callable, Optional


class Outcome(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    REDACT = "redact"


@dataclass
class Decision:
    outcome: Outcome
    article: str
    reason: str
    redactions: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "outcome": self.outcome.value,
            "article": self.article,
            "reason": self.reason,
            "redactions": self.redactions,
        }


# --------------------------------------------------------------------------- #
# Field patterns — the personal data a mandated minimization must catch
# --------------------------------------------------------------------------- #
FIELD_PATTERNS = {
    "rrn": re.compile(r"\d{6}-\d{7}"),          # 주민등록번호
    "passport": re.compile(r"\b[A-Z]{1,2}\d{7}\b"),  # 여권번호
    "phone": re.compile(r"01\d-\d{3,4}-\d{4}"),      # 휴대전화
    "bank_acct": re.compile(r"\b\d{3,6}-\d{2,6}-\d{4,7}\b"),  # 계좌번호
}


@dataclass
class Article:
    """A compiled PIPA article."""
    number: str
    title: str
    evaluate: Callable[[dict], Decision]


class PIPACompiler:
    """
    Compiles article definitions into an Article set.

    `compile()` returns a dict {article_number: Article}; the pipeline calls
    `enforce_plan()` to get the ordered decisions for a context.
    """

    def __init__(self):
        self._articles: dict[str, Article] = {}
        self._build()

    # ---- Art. 21: Consent gate ------------------------------------------- #
    def _art21(self, ctx: dict) -> Decision:
        if ctx.get("consent") is True:
            return Decision(Outcome.ALLOW, "Art.21", "valid consent on record")
        return Decision(
            Outcome.BLOCK,
            "Art.21",
            "처리 동의 없음 — processing blocked (no consent metadata)",
        )

    # ---- Art. 22: Minimization / redaction ------------------------------- #
    def _art22(self, ctx: dict) -> Decision:
        text = str(ctx.get("output", ""))
        redactions = {}
        for name, pat in FIELD_PATTERNS.items():
            matches = pat.findall(text)
            if matches:
                redactions[name] = len(matches)
                text = pat.sub(f"[{name.upper()}_REDACTED]", text)
        if redactions:
            return Decision(
                Outcome.REDACT,
                "Art.22",
                f"최소수집 위반 — redacted {sum(redactions.values())} field(s)",
                redactions={"counts": redactions, "clean": text},
            )
        return Decision(Outcome.ALLOW, "Art.22", "no excess personal data")

    # ---- Art. 39: Retention / destruction -------------------------------- #
    def _art39(self, ctx: dict) -> Decision:
        stored_at = ctx.get("stored_at")
        retention_days = ctx.get("retention_days", 1825)  # default 5 years
        if stored_at is None:
            return Decision(Outcome.ALLOW, "Art.39", "no retention window set")
        if isinstance(stored_at, str):
            stored_at = datetime.fromisoformat(stored_at)
        if stored_at.tzinfo is None:
            stored_at = stored_at.replace(tzinfo=timezone.utc)
        expiry = stored_at + timedelta(days=retention_days)
        now = datetime.now(timezone.utc)
        if now >= expiry:
            return Decision(
                Outcome.BLOCK,
                "Art.39",
                f"보유기간 만료 — retention expired {expiry.date().isoformat()}",
            )
        return Decision(
            Outcome.ALLOW,
            "Art.39",
            f"within retention until {expiry.date().isoformat()}",
        )

    def _build(self):
        self._articles = {
            "Art.21": Article("Art.21", "동의 (Consent)", self._art21),
            "Art.22": Article("Art.22", "최소수집 (Minimization)", self._art22),
            "Art.39": Article("Art.39", "파기 (Retention)", self._art39),
        }

    @property
    def articles(self) -> dict[str, Article]:
        return dict(self._articles)

    def describe(self) -> dict:
        """Machine-readable policy manifest (auditor-facing)."""
        return {
            num: {"title": a.title, "rule": a.evaluate.__doc__ or ""}
            for num, a in self._articles.items()
        }

    def enforce_plan(self, ctx: dict, order=("Art.21", "Art.39", "Art.22")) -> list[Decision]:
        """
        Run articles in a fixed order:
          1. Consent gate must pass first (Art.21)
          2. Retention window checked (Art.39)
          3. Redaction applied last so nothing leaks on block (Art.22)

        Returns all decisions; the caller stops at the first BLOCK.
        """
        decisions = []
        for num in order:
            d = self._articles[num].evaluate(ctx)
            decisions.append(d)
            if d.outcome == Outcome.BLOCK:
                break
        return decisions


if __name__ == "__main__":
    compiler = PIPACompiler()
    ctx = {
        "consent": True,
        "output": "신청인 900101-1234567 여권 M1234567",
    }
    for d in compiler.enforce_plan(ctx):
        print(d.to_dict())
    print("--- manifest ---")
    print(compiler.describe())