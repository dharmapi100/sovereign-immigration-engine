"""
PIPA Article-as-Code → Policy Manifest Exporter
================================================
Compiles the PIPA article set into a **wire-enforceable policy manifest** that
the Go guardrail gateway loads and executes at the request boundary.

This is the "compile" half of the two-stage design:

    statute (PIPA articles)
          │  this module (Python)
          ▼
    policy.manifest.json
          │  loaded by
          ▼
    guardrail gateway (Go) — enforces at the wire, writes the audit chain

Why a manifest rather than shared code: the gateway must stay a single static
binary (air-gap story); the compiler stays in Python where the article logic
lives. The manifest is the stable interface between them.

Wire-binding note (honest): a transparent proxy can only enforce what it can
observe on the wire.
    * Art. 22 (minimization) — body patterns → FULLY enforceable (block/redact)
    * Art. 21 (consent)      — header-gated; enforced only when the client
                               declares consent state (proxy can't infer it)
    * Art. 39 (retention)    — header-gated; enforced only when a stored-at
                               timestamp is supplied
Full Art. 21/39 enforcement happens in the application pipeline; the gateway
enforces the wire-observable subset.

Usage:
    python3 manifest.py > policy.manifest.json
    python3 manifest.py --out policy.manifest.json
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

# Reuse the compiler's patterns so the two never drift.
try:
    from compiler import FIELD_PATTERNS
except ImportError:  # allow running from repo root
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from compiler import FIELD_PATTERNS

# Which minimization patterns block outright vs. redact in place.
# 주민등록번호 (RRN) is the hard-block class the guardrail is known for.
PATTERN_ACTIONS = {
    "rrn": "block",
    "passport": "redact",
    "phone": "redact",
    "bank_acct": "redact",
}

CITATIONS = {
    "Art.21": "개인정보 보호법 제21조 (개인정보의 수집·이용 동의)",
    "Art.22": "개인정보 보호법 제22조 (개인정보의 최소 수집)",
    "Art.39": "개인정보 보호법 제39조 (개인정보의 파기)",
}


def build_manifest() -> dict:
    patterns = []
    for name, pat in FIELD_PATTERNS.items():
        patterns.append({
            "name": name,
            "regex": pat.pattern,
            "action": PATTERN_ACTIONS.get(name, "redact"),
        })

    rules = [
        {
            "article": "Art.22",
            "title": "최소수집 (Minimization)",
            "io": "body",
            "citation": CITATIONS["Art.22"],
            "patterns": patterns,
        },
        {
            "article": "Art.21",
            "title": "동의 (Consent)",
            "io": "header",
            "citation": CITATIONS["Art.21"],
            "header": "X-PIPA-Consent",
            "required_value": "true",
            "enabled": False,  # turn on to make the gateway consent-required
        },
        {
            "article": "Art.39",
            "title": "파기 (Retention)",
            "io": "header",
            "citation": CITATIONS["Art.39"],
            "header": "X-PIPA-Stored-At",
            "max_age_days": 1825,
            "enabled": False,  # turn on to enforce a retention window at the wire
        },
    ]

    return {
        "version": "1.0",
        "source": "PIPA",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "enforcement_order": ["Art.21", "Art.39", "Art.22"],
        "rules": rules,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="Export the PIPA policy manifest")
    ap.add_argument("--out", help="write to file instead of stdout")
    args = ap.parse_args()

    manifest = build_manifest()
    blob = json.dumps(manifest, ensure_ascii=False, indent=2)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(blob + "\n")
        print(f"wrote {args.out} ({len(manifest['rules'])} rules)", file=sys.stderr)
    else:
        print(blob)


if __name__ == "__main__":
    main()
