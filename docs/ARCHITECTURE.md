# Architecture

## Principles

1. **Zero runtime dependencies for the core.** The compliance engine and
   API use Python stdlib + `cryptography` only. No web framework, no ORM,
   no message broker. This is what makes air-gap deployment trivial.
2. **Evidence before convenience.** Raw personal data is never persisted;
   only hashes and decisions are. Every action is chained.
3. **Optional heavy layers.** OCR and document classification are the only
   heavy dependencies and load lazily — the core runs without them.
4. **Law maps to code 1:1.** PIPA articles and visa rules compile to
   callables that return a decision *with a citation*.

---

## Components

```
                          ┌───────────────────────────┐
   client ──HTTP──▶       │  services/api/server.py    │  stdlib http.server
                          │  (ThreadingHTTPServer)     │  zero frameworks
                          └─────────────┬─────────────┘
                                        │
            ┌───────────────────────────┼──────────────────────────┐
            ▼                           ▼                          ▼
  ┌──────────────────┐      ┌──────────────────┐       ┌──────────────────┐
  │ visa-policy      │      │ pipa-dsl         │       │ kyc-pipeline     │
  │ D-8-4/E-7/E-9/   │      │ Art.21/22/39     │       │ ingest → enforce │
  │ D-10 rules-as-   │      │ consent/redact/  │       │ → validate       │
  │ code + citations │      │ retention        │       │ (+ optional OCR) │
  └────────┬─────────┘      └────────┬─────────┘       └────────┬─────────┘
           │                         │                          │
           └─────────────┬───────────┴──────────────┬───────────┘
                         ▼                          ▼
              ┌────────────────────┐     ┌────────────────────────┐
              │ audit-ledger       │     │ compliance-report      │
              │ hash-chained log   │────▶│ self-hashing evidence  │
              │ + kisa_client      │     │ artifact               │
              └────────────────────┘     └────────────────────────┘
```

### `services/audit-ledger/`
- `ledger.py` — `AuditLedger`: append-only, SHA-256 chained, SQLite,
  thread-safe, `verify_chain()` for tamper detection.
- `kisa_client.py` — RFC 3161 timestamp client (fail-soft).
- `evidence.py` — `EvidenceService`: the single entry point that every
  stage calls so the evidence format is uniform.

### `services/pipa-dsl/`
- `compiler.py` — `PIPACompiler` compiles Art. 21/22/39 into callables.
  `enforce_plan()` runs them in dependency order and stops at the first
  block.

### `services/visa-policy/`
- `engine.py` — `VisaPolicyEngine` with real rule sets per visa class.
  `PolicyConfig` holds tunable thresholds. Each `Rule` carries a citation.

### `services/compliance-report/`
- `generator.py` — `ReportGenerator` produces a self-hashing report
  combining visa decisions, PIPA decisions, and an audit-chain proof.

### `services/kyc-pipeline/`
- `ingestion.py` — orchestrates: decrypt → classify → OCR → **PIPA
  enforce** → validate → match → record.

### `services/api/`
- `server.py` — stdlib REST surface. All routing, auth (optional bearer
  token), JSON I/O.

---

## Request lifecycle (`POST /v1/pipeline/ingest`)

```
1. base64 decode encrypted doc + Fernet key
2. decrypt → JSON applicant data
3. optional: classify image, OCR extract text
4. PIPA enforce_plan(consent, output, retention)
     - Art.21 block  → record PIPA_BLOCK, return invalid
     - Art.22 redact → scrub PII from output text
     - Art.39 block  → retention expired
5. visa validate + policy match
6. EvidenceService.record(...)  → ledger append (+ KISA timestamp)
7. return result
```

Every step that touches data produces an auditable entry.

---

## Why stdlib for the API

An acquirer or government client must be able to run this in an air-gapped
network with **no package registry**. A stdlib HTTP server means the
install is: copy files, run `python3 services/api/server.py`. Nothing to
`pip install` for the compliance core.

OCR is the exception — it needs `easyocr`/`torch`, and is therefore a
separate, optional layer (`pip install .[ocr]`).

---

## Deployment shapes

| Shape | Path | Use |
|-------|------|-----|
| Direct | `python3 services/api/server.py` | dev, demo |
| Air-gap bundle | `deployment/build_bundle.sh` → `install.sh` | government/finance/defense |
| Container | `Dockerfile` | standard cloud/on-prem |
| systemd | `deployment/sovereign-immigration.service` | hardened host service |
