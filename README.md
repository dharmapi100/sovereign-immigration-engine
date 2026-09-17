# Sovereign Immigration Engine

**Automated, PIPA-compliant immigration processing platform** — End-to-end KYC, OCR, visa policy validation, and immutable audit logging for sovereign-native talent onboarding in Korea.

## Overview

The Sovereign Immigration Engine is a production-ready platform that automates the entire immigration workflow for foreign talent entering Korea — from document ingestion and OCR extraction to PIPA-compliant pseudonymization, visa policy validation, and court-admissible audit logging. Built for regulated environments (government, finance, healthcare) where data sovereignty and auditability are non-negotiable.

## Core Capabilities

| Pipeline Stage | Component | Key Features |
|----------------|-----------|--------------|
| **Ingestion** | `services/kyc-pipeline/ingestion.py` | Multi-format document intake (PDF, images, scanned docs) |
| **OCR & Classification** | `services/kyc-pipeline/ocr/` | Document classification, text extraction, layout analysis |
| **PII Anonymization** | `services/kyc-pipeline/ocr/preprocessor/anonymizer/` | PII detection, pseudonymization, compliance scrubbing |
| **Document Classification** | `services/doc-classifier/` | Visa type classification, document type routing |
| **Policy Matching** | `services/policy-matching/` | Visa policy rule engine, eligibility validation |
| **Visa Validation** | `services/visa-validation/` | Automated eligibility checks, quota tracking |
| **Audit Ledger** | `services/audit-ledger/` | Immutable SHA-256 chained audit log, KISA timestamp integration |
| **Compliance Dashboard** | `services/compliance-dashboard/` | Real-time compliance monitoring, audit trail queries |
| **Pipeline Orchestration** | `pipeline_orchestrator.py` | End-to-end workflow coordination, error handling, retries |

## Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Document   │───▶│   OCR &     │───▶│   PII       │───▶│   Policy    │
│  Ingestion  │    │  Classification│    │ Anonymization│    │ Matching    │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                              │
                                                              ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Visa       │◀───│   Policy    │◀───│  Pipeline     │◀───│  Visa       │
│  Validation │    │ Matching    │    │ Orchestrator  │    │ Validation  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
       │               │                │                │
       ▼               ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIT LEDGER (Immutable)                      │
│  SHA-256 Chained Log  •  KISA Timestamp (RFC 3161)  •  PIPA    │
└─────────────────────────────────────────────────────────────────┘
```

## Key Features

### PIPA-Compliant by Design
- **Article 21** — Consent management & lawful basis tracking
- **Article 22** — Purpose limitation enforcement
- **Article 39** — Data minimization & pseudonymization
- **Article 39-2** — Automated pseudonymization pipeline

### Audit-Grade Compliance
- **SHA-256 chained audit log** — Tamper-evident, append-only
- **KISA Timestamp Authority (RFC 3161)** — Legal timestamp verification
- **Court-admissible evidence** — Cryptographic proof of every transaction
- **PIPA Article-as-Code** — Legal articles mapped to executable policy

### Enterprise-Grade Pipeline
- **Async pipeline orchestration** — Retries, dead-letter queues, idempotency
- **OCR pipeline** — Classification → Extraction → Anonymization → Validation
- **Policy-as-Code** — Visa rules as executable code, not documentation
- **Multi-tenant isolation** — Namespace isolation, data segregation

## Quick Start

### Prerequisites
- Python 3.11+
- Docker & Docker Compose
- Python 3.11+ with pip

### Quick Start (Docker)
```bash
# Start full stack
docker-compose -f deployment/docker-compose.yaml up -d

# Verify health
curl http://localhost:8000/health
```

### Local Development
```bash
# Install dependencies
pip install -r services/kyc-pipeline/ocr/requirements.txt
pip install -r services/doc-classifier/requirements.txt
pip install -r services/fleet-orchestrator/requirements.txt

# Run tests
pytest tests/ -v

# Run pipeline
python -m pipeline_orchestrator
```

## Configuration

All configuration via environment variables:

```bash
# Required
export PIPA_HMAC_KEY="your-64-char-hex-key"
export KISA_API_KEY="your-kisa-api-key"
export DATABASE_URL="postgresql://user:pass@localhost/immigration"

# Optional
export KISA_TIMESTAMP_ENDPOINT="https://timestamp.kisa.or.kr"
export LOG_LEVEL="INFO"
export REDIS_URL="redis://localhost:6379"
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suites
pytest tests/test_pipeline.py -v
pytest tests/fuzzer/ -v
pytest services/kyc-pipeline/tests/ -v
```

## Deployment

### Docker Compose (Production)
```yaml
# deployment/docker-compose.yaml
services:
  api:
    build: .
    ports: ["8000:8000"]
    environment:
      - PIPA_HMAC_KEY=${PIPA_HMAC_KEY}
      - KISA_API_KEY=${KISA_API_KEY}
    depends_on: [db, redis]

  worker:
    build: .
    command: python -m pipeline_orchestrator
    depends_on: [redis, db]

  db:
    image: postgres:16
    volumes: [postgres_data:/var/lib/postgresql/data]

  redis:
    image: redis:7-alpine
```

### Air-Gap Deployment
```bash
# Build air-gap bundle
./install.sh --airgap --prefix=/opt/sovereign-immigration

# On air-gapped host
cd /opt/sovereign-immigration
./install.sh --config=/etc/sovereign-immigration/config.yaml
systemctl start sovereign-immigration
```

## Security & Compliance

| Standard | Implementation |
|----------|----------------|
| **PIPA Articles 21/22/39** | Automated enforcement via policy engine |
| **KISA Timestamp (RFC 3161)** | Optional timestamp authority integration |
| **SHA-256 Chained Audit Log** | Tamper-evident, append-only ledger |
| **Air-Gap Compatible** | No external dependencies at runtime |
| **Data Minimization** | Automated pseudonymization pipeline |
| **Consent Management** | Article 21 consent tracking & revocation |

## Project Structure

```
sovereign-immigration-engine/
├── deployment/
│   └── docker-compose.yaml
├── provisioning_spec.md
├── services/
│   ├── audit-ledger/           # Immutable audit ledger
│   ├── compliance-dashboard/   # Compliance monitoring UI
│   ├── doc-classifier/         # Document type classification
│   ├── fleet-orchestrator/     # Robot fleet coordination (shared)
│   ├── kyc-pipeline/           # Core KYC/OCR pipeline
│   ├── monitor/                # Audit monitoring & alerting
│   ├── notification-gateway/   # Multi-channel notifications
│   ├── policy-matching/        # Visa policy rule engine
│   ├── visa-validation/        # Visa eligibility & quota
│   └── pipeline_orchestrator.py
├── tests/
│   ├── data/                   # Test fixtures
│   ├── fuzzer/                 # Fault injection & stress tests
│   └── test_*.py               # Unit & integration tests
├── deployment/
│   └── docker-compose.yaml
├── provisioning_spec.md
├── .gitignore
├── README.md
└── Pitch_Deck.md
```

## License

MIT License — see [LICENSE](LICENSE) for details.

---

**Sovereign Immigration Engine** — Automating compliant immigration at scale. Built for sovereign data environments where auditability and compliance are non-negotiable.