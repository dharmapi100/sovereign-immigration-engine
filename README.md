# Sovereign Immigration Engine

**PIPA-compliant visa + KYC platform for Korean regulated environments** — evidence-grade audit trail, rules-as-code visa policy, and air-gap deployment.

Built for the Korean market (KSGC / OASIS / D-8-4 pathway): a foreign-talent immigration and compliance engine that runs entirely on-premise, enforces PIPA by code, and produces a tamper-evident audit chain.

---

## What this actually does

A single HTTP API (Python stdlib, no web framework) that:

1. **Evaluates visa eligibility** for D-8-4 (startup), E-7 (professional), E-9 (non-professional), D-10 (job-seeking) — real rule sets, each decision carrying a statutory citation.
2. **Enforces PIPA as code** — Art. 21 (consent gate), Art. 22 (minimization/redaction), Art. 39 (retention).
3. **Runs a KYC pipeline** on submitted documents — PIPA enforcement, optional OCR/classification, validation.
4. **Writes an append-only hash-chained audit ledger** for every action, with optional KISA RFC-3161 timestamps.

---

## Status (honest)

| Component | State |
|-----------|-------|
| Visa policy engine (D-8-4/E-7/E-9/D-10) | ✅ Working, cited rules |
| PIPA Article-as-Code DSL (Art. 21/22/39) | ✅ Working |
| Hash-chained audit ledger + tamper detection | ✅ Working |
| KISA RFC-3161 timestamp client | ✅ Working (verified against mock TSA; live KISA endpoint needs a key) |
| REST API (stdlib, zero deps) | ✅ Working |
| Compliance report generator (self-hashing evidence artifact) | ✅ Working |
| Air-gap bundle + systemd + install | ✅ Working |
| Docker image | ✅ Provided |
| OCR / document classification | ⚠️ Optional — needs `easyocr`/`torch` + Korean-trained models (not bundled) |
| Compliance dashboard / notifications / monitor | ⚠️ Basic scaffolds |

**Not yet built:** live KISA integration test, trained Korean OCR/classifier models, compliance dashboard UI, multi-tenant isolation. The README previously claimed these — it no longer does.

---

## Quick start

### Run the API locally

```bash
# no pip install needed for the core — stdlib + cryptography
python3 services/api/server.py
curl http://127.0.0.1:8787/health
```

### Full end-to-end demo

```bash
python3 demo.py
```

Walks through: PIPA manifest → D-8-4/E-7 eligibility (with citations) →
document ingest + PII redaction → audit chain verification → tamper detection.

### Evaluate a visa

```bash
curl -X POST http://127.0.0.1:8787/v1/visa/evaluate \
  -H "Content-Type: application/json" \
  -d '{"visa":"D-8-4","applicant":{
        "investment_capital_krw":150000000,
        "business_plan":true,
        "incubator_letter":true,
        "ip_assets":["patent"]}}'
```

Response carries per-rule pass/fail with a citation (`출입국관리법 시행령 별표1` etc.).

---

## API

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/health` | liveness |
| GET | `/ready` | readiness + ledger integrity |
| GET | `/v1/pipa/manifest` | PIPA Article-as-Code manifest |
| POST | `/v1/visa/evaluate` | `{visa, applicant}` → eligibility |
| POST | `/v1/visa/evaluate-all` | `{applicant}` → all visa classes |
| POST | `/v1/pipeline/ingest` | `{doc_b64, key_b64}` → run KYC pipeline |
| POST | `/v1/report` | `{applicant_id, applicant, visa?}` → self-hashing compliance report |
| GET | `/v1/audit` | recent audit entries |
| GET | `/v1/audit/verify` | chain integrity |
| GET | `/v1/audit/{hash}` | single audit record |

Auth: set `API_TOKEN` to require `Authorization: Bearer <token>` on `/v1/*`.

---

## PIPA mapping

| Article | Enforcement |
|---------|-------------|
| **Art. 21** 동의 (Consent) | blocks processing when consent metadata is absent |
| **Art. 22** 최소수집 (Minimization) | redacts RRN / passport / phone / account on output |
| **Art. 39** 파기 (Retention) | blocks access past the retention window |

The manifest is exposed at `/v1/pipa/manifest` so an auditor can map code → statute.

---

## Audit ledger

Every pipeline action appends `hash_n = SHA256(payload_hash || hash_{n-1})`.
Raw payloads are never stored — only hashes. Integrity is checkable:

```python
ledger.verify_chain()   # recomputes the full chain
ledger.get(chain_hash)  # retrieve a single record
```

When `KISA_ENABLED=true`, each new hash requests an RFC-3161 timestamp from
the TSA and attaches it (fail-soft: a slow TSA never blocks the ledger).

---

## Deployment

### Air-gap (offline, recommended for government/finance/defense)

```bash
cd deployment
./build_bundle.sh 0.2.0        # -> dist/sovereign-immigration-0.2.0.tar.gz (+ .sha256)
```

Transfer both files across the gap, verify the archive checksum, extract, then:

```bash
./install.sh                    # installs to /opt/sovereign-immigration (verifies every file)
./install.sh --with-service     # + hardened systemd unit (as root)
```

### Container

```bash
docker build -t sovereign-immigration:0.2 .
docker run -p 8787:8787 -v /var/lib/sie:/data sovereign-immigration:0.2
```

See [deployment/README.md](deployment/README.md) for the full runbook.

---

## Testing

```bash
# run the whole suite (stdlib unittest — no pytest needed)
for f in $(find . -name "test_*.py"); do python3 "$f"; done
```

Coverage: ledger (incl. tamper detection), PIPA DSL, visa engine, API
integration, pipeline end-to-end.

---

## Project structure

```
sovereign-immigration-engine/
├── Dockerfile
├── deployment/                 # air-gap bundle, installer, systemd, runbook
│   ├── build_bundle.sh
│   ├── install.sh
│   ├── sovereign-immigration.service
│   └── README.md
├── services/
│   ├── api/                    # stdlib HTTP API
│   ├── audit-ledger/           # hash-chained ledger, KISA client, evidence service
│   ├── pipa-dsl/               # PIPA Article-as-Code compiler
│   ├── visa-policy/            # D-8-4/E-7/E-9/D-10 rules-as-code engine
│   ├── compliance-report/      # self-hashing evidence-artifact generator
│   ├── kyc-pipeline/           # ingestion + optional OCR/preprocess
│   ├── doc-classifier/         # optional (torch) document classifier
│   ├── policy-matching/        # rule scoring
│   ├── visa-validation/        # field validation
│   ├── monitor/                # audit monitoring
│   ├── notification-gateway/   # notifications
│   ├── compliance-dashboard/   # audit logging helper
│   └── fleet-orchestrator/     # shared robot-fleet adapter
└── tests/
```

---

## License

MIT — see [LICENSE](LICENSE).

---

**Built for sovereign data environments where auditability and PIPA compliance are non-negotiable.**
