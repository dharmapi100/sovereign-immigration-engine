# Compliance Mapping

Every legal requirement in this system maps to *identified code* and a
*test that proves it*. This document is the audit trail for auditors and
acquirers: nothing here is aspirational.

---

## PIPA (개인정보 보호법)

| Article | Requirement | Implementation | Test |
|---------|-------------|----------------|------|
| **Art. 21** | 동의 (Consent) — process only with lawful consent | `services/pipa-dsl/compiler.py` → `_art21` | `services/pipa-dsl/tests/test_compiler.py::test_art21_blocks_without_consent` |
| **Art. 22** | 최소수집 (Minimization) — collect only what's needed | `compiler.py` → `_art22`, `FIELD_PATTERNS` (RRN/여권/휴대전화/계좌) | `test_compiler.py::test_art22_redacts_rrn`, `..._redacts_multiple` |
| **Art. 39** | 파기 (Retention) — destroy after retention window | `compiler.py` → `_art39` (default 1825d / 5yr) | `test_compiler.py::test_art39_expired_blocks`, `..._fresh_allows` |

**Enforcement order** (`enforce_plan`): Art. 21 (consent) → Art. 39
(retention) → Art. 22 (redact last, so nothing leaks even on block).

**Manifest** exposed at `GET /v1/pipa/manifest` so a reviewer can map
code → statute at runtime.

---

## Visa classes (출입국관리법)

| Visa | Class | Rules | Implementation | Test |
|------|-------|-------|----------------|------|
| **D-8-4** | 기업투자 (startup/investment) | capital, business plan, entity, tech/ip | `services/visa-policy/engine.py` → `_d84_rules` | `test_engine.py::test_d84_full_founder_eligible`, `..._underfunded_blocked` |
| **E-7** | 특정활동 (professional) | degree/experience, offer, salary, occupation list | `engine.py` → `_e7_rules` | `..._degree_or_experience` |
| **E-9** | 비전문취업 (EPS) | age bounds, EPS-TOPIK, employer sponsor | `engine.py` → `_e9_rules` | `..._age_bounds` |
| **D-10** | 구직 (job-seeking) | points score, degree | `engine.py` → `_d10_rules` | `..._points` |

Every decision returns a `citation` (e.g. `출입국관리법 시행령 별표1`) — tested
by `test_engine.py::test_every_decision_has_citation`.

Thresholds are in `PolicyConfig` (`engine.py`) and tunable per scheme
(tested by `..._config_tunable`).

---

## Evidence integrity

| Control | Implementation | Test |
|---------|----------------|------|
| Hash-chained audit log | `services/audit-ledger/ledger.py` — `hash_n = SHA256(payload_hash ‖ hash_{n-1})` | `test_ledger.py::test_append_chains` |
| Payloads never stored | `ledger.py` — only `payload_hash` persisted | `test_ledger.py::test_payload_never_stored` |
| Tamper detection | `ledger.py::verify_chain()` | `test_ledger.py::test_tamper_detected` |
| Trusted timestamp (RFC 3161) | `kisa_client.py` | `test_kisa_integration.py::test_client_round_trip` |
| Timestamp fail-soft | `evidence.py` — TSA failure never blocks the ledger | `test_kisa_integration.py::test_tsa_failure_is_failsafe` |
| Self-hashing report | `services/compliance-report/generator.py` | `test_report.py::test_tamper_invalidates_report` |

---

## Data handling summary

```
applicant doc  ──▶  PIPA enforce (Art.21/39/22)  ──▶  visa evaluate
                        │                                  │
                        └──────────► audit ledger ◄─────────┘
                                   (hash chain, optional KISA TS)
                                          │
                                          ▼
                              self-hashing compliance report
```

- **Raw personal data is never written to the ledger** — only hashes.
- **Redaction happens before persistence** (Art. 22).
- **Every action is chained and, when enabled, KISA-timestamped.**

---

## What is NOT yet verified

Honest gaps, so nothing is overstated:

- **Live KISA TSA** — the client is proven against a mock TSA; a real
  endpoint + API key is required to close this.
- **OCR / Korean document model** — not trained/bundled; OCR is optional
  and loaded lazily.
- **MOJ quota tracking** and per-scheme numeric thresholds should be
  confirmed with counsel before production use.
