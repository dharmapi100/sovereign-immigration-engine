"""
Visa Policy Engine (Rules-as-Code)
==================================
Evaluates foreign-talent visa eligibility for the Korean market with the
actual rule sets, not a stub. Every decision carries a citation so an
auditor can map result -> statute.

Covered visa classes:
    D-8-4  기업투자 (startup / investment track)  — KSGC / OASIS founders
    E-7    특정활동 (professional / specialised occupation)
    E-9    비전문취업 (non-professional employment, EPS)
    D-10   구직 (job-seeking, points-based)

Design:
    Each visa is a Policy with a list of Rule objects. A Rule returns a
    RuleResult (pass/fail + reason + citation). The engine aggregates.
    Thresholds live in a PolicyConfig so they can be tuned per-scheme
    (e.g. KSGC vs OASIS) without touching logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class VisaClass(str, Enum):
    D84 = "D-8-4"
    E7 = "E-7"
    E9 = "E-9"
    D10 = "D-10"


@dataclass
class RuleResult:
    passed: bool
    rule_id: str
    reason: str
    citation: str

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "rule_id": self.rule_id,
            "reason": self.reason,
            "citation": self.citation,
        }


@dataclass
class PolicyConfig:
    """Tunable thresholds (KRW amounts in won)."""
    d84_min_capital_krw: int = 100_000_000      # 100M KRW base investment
    e7_min_degree: str = "bachelor"
    e7_min_salary_krw: int = 30_000_000         # ~30M KRW/yr
    e7_min_experience_years: int = 5
    e9_min_age: int = 18
    e9_max_age: int = 39
    d10_min_points: int = 60
    degree_rank: dict = field(default_factory=lambda: {
        "high_school": 1, "associate": 2, "bachelor": 3, "master": 4, "doctorate": 5,
    })

    def degree_at_least(self, have: str, need: str) -> bool:
        return self.degree_rank.get(have, 0) >= self.degree_rank.get(need, 99)


@dataclass
class Rule:
    rule_id: str
    citation: str
    check: Callable[[dict, "PolicyConfig"], "tuple[bool, str]"]

    def evaluate(self, applicant: dict, cfg: PolicyConfig) -> RuleResult:
        passed, reason = self.check(applicant, cfg)
        return RuleResult(passed, self.rule_id, reason, self.citation)


# --------------------------------------------------------------------------- #
# Rule definitions per visa class
# --------------------------------------------------------------------------- #

def _d84_rules() -> list[Rule]:
    return [
        Rule("D84-CAP", "출입국관리법 시행령 별표1 (D-8-4 기업투자)",
             lambda a, c: (
                 a.get("investment_capital_krw", 0) >= c.d84_min_capital_krw,
                 f"투자금 {a.get('investment_capital_krw', 0):,} KRW "
                 f"(최소 {c.d84_min_capital_krw:,})")),
        Rule("D84-BIZPLAN", "D-8-4 사업계획 요건",
             lambda a, c: (
                 bool(a.get("business_plan")),
                 "사업계획서 제출됨" if a.get("business_plan") else "사업계획서 없음")),
        Rule("D84-ENTITY", "D-8-4 법인 설립 요건",
             lambda a, c: (
                 bool(a.get("korean_entity_registered") or a.get("incubator_letter")),
                 "법인등기 또는 인큐베이터 확인서 보유"
                 if (a.get("korean_entity_registered") or a.get("incubator_letter"))
                 else "법인등기/인큐베이터 확인서 필요")),
        Rule("D84-TECH", "D-8-4 기술력 요건 (KISED 평가)",
             lambda a, c: (
                 bool(a.get("ip_assets") or a.get("tech_evaluation_passed")),
                 "특허/기술평가 보유"
                 if (a.get("ip_assets") or a.get("tech_evaluation_passed"))
                 else "특허 또는 기술평가 필요")),
    ]


def _e7_rules() -> list[Rule]:
    return [
        Rule("E7-DEGREE", "출입국관리법 시행령 별표1 (E-7 특정활동)",
             lambda a, c: (
                 c.degree_at_least(a.get("degree", ""), c.e7_min_degree)
                 or a.get("experience_years", 0) >= c.e7_min_experience_years,
                 f"학위 {a.get('degree', 'none')} / 경력 "
                 f"{a.get('experience_years', 0)}년")),
        Rule("E7-OFFER", "E-7 고용계약 요건",
             lambda a, c: (
                 bool(a.get("job_offer")),
                 "고용계약서 있음" if a.get("job_offer") else "고용계약서 필요")),
        Rule("E7-SALARY", "E-7 소득 요건",
             lambda a, c: (
                 a.get("salary_krw", 0) >= c.e7_min_salary_krw,
                 f"연봉 {a.get('salary_krw', 0):,} KRW "
                 f"(최소 {c.e7_min_salary_krw:,})")),
        Rule("E7-OCCUPATION", "E-7 직종 요건 (고시 직종)",
             lambda a, c: (
                 bool(a.get("occupation_in_list")),
                 "허용 직종" if a.get("occupation_in_list") else "허용 직종 아님")),
    ]


def _e9_rules() -> list[Rule]:
    return [
        Rule("E9-AGE", "E-9 연령 요건 (EPS)",
             lambda a, c: (
                 c.e9_min_age <= a.get("age", 0) <= c.e9_max_age,
                 f"만 {a.get('age', 0)}세 (허용 {c.e9_min_age}-{c.e9_max_age})")),
        Rule("E9-TOPIK", "E-9 한국어시험 요건 (EPS-TOPIK)",
             lambda a, c: (
                 bool(a.get("eps_topik_passed")),
                 "EPS-TOPIK 합격" if a.get("eps_topik_passed") else "EPS-TOPIK 미합격")),
        Rule("E9-SPONSOR", "E-9 송출/고용주 요건",
             lambda a, c: (
                 bool(a.get("employer_sponsorship")),
                 "고용주 스폰서 있음" if a.get("employer_sponsorship")
                 else "고용주 스폰서 필요")),
    ]


def _d10_rules() -> list[Rule]:
    def _points(a, c):
        pts = 0
        pts += {"high_school": 10, "associate": 15, "bachelor": 20,
                "master": 25, "doctorate": 30}.get(a.get("degree", ""), 0)
        age = a.get("age", 0)
        pts += 20 if 20 <= age <= 29 else 15 if 30 <= age <= 34 else 10 if age >= 35 else 0
        pts += {"topik_6": 20, "topik_5": 18, "topik_4": 15,
                "topik_3": 10}.get(a.get("topik_level", ""), 0)
        pts += 10 if a.get("income_krw", 0) >= 30_000_000 else 0
        pts += 10 if a.get("korean_university_grad") else 0
        return pts
    return [
        Rule("D10-POINTS", "출입국관리법 시행령 (D-10 점수제)",
             lambda a, c: (
                 _points(a, c) >= c.d10_min_points,
                 f"점수 {_points(a, c)} / {c.d10_min_points}")),
        Rule("D10-DEGREE", "D-10 학위 요건",
             lambda a, c: (
                 c.degree_at_least(a.get("degree", ""), "bachelor"),
                 f"학위 {a.get('degree', 'none')}")),
    ]


POLICIES = {
    VisaClass.D84: _d84_rules,
    VisaClass.E7: _e7_rules,
    VisaClass.E9: _e9_rules,
    VisaClass.D10: _d10_rules,
}


@dataclass
class EligibilityResult:
    visa: str
    eligible: bool
    score: int
    max_score: int
    results: list[RuleResult]
    missing: list[str]

    def to_dict(self) -> dict:
        return {
            "visa": self.visa,
            "eligible": self.eligible,
            "score": self.score,
            "max_score": self.max_score,
            "missing": self.missing,
            "rules": [r.to_dict() for r in self.results],
        }


class VisaPolicyEngine:
    def __init__(self, config: Optional[PolicyConfig] = None):
        self.cfg = config or PolicyConfig()

    def evaluate(self, visa: str, applicant: dict) -> EligibilityResult:
        vc = VisaClass(visa)
        rules = POLICIES[vc]()
        results = [r.evaluate(applicant, self.cfg) for r in rules]
        passed = [r for r in results if r.passed]
        missing = [r.rule_id for r in results if not r.passed]
        return EligibilityResult(
            visa=vc.value,
            eligible=len(missing) == 0,
            score=len(passed),
            max_score=len(results),
            results=results,
            missing=missing,
        )

    def evaluate_all(self, applicant: dict) -> list[EligibilityResult]:
        return [self.evaluate(v.value, applicant) for v in VisaClass]


if __name__ == "__main__":
    import json

    engine = VisaPolicyEngine()
    founder = {
        "investment_capital_krw": 150_000_000,
        "business_plan": True,
        "incubator_letter": True,
        "ip_assets": ["PIPA-Article-Compiler"],
    }
    print("=== D-8-4 founder ===")
    print(json.dumps(engine.evaluate("D-8-4", founder).to_dict(), ensure_ascii=False, indent=2))

    pro = {
        "degree": "master", "job_offer": True,
        "salary_krw": 50_000_000, "occupation_in_list": True,
    }
    print("=== E-7 professional ===")
    print(json.dumps(engine.evaluate("E-7", pro).to_dict(), ensure_ascii=False, indent=2))