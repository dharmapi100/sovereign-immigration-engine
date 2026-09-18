# Deployment

Two supported paths: **air-gap bundle** (offline, sovereign) and
**container** (standard). Both run the same API on port 8787.

---

## 1. Air-gap (offline) deployment

For environments with no outbound network: government, finance, defense.

### On the build host

```bash
cd deployment
./build_bundle.sh 0.2.0
```

Produces in `../dist/`:

| File | Purpose |
|------|---------|
| `sovereign-immigration-0.2.0.tar.gz` | self-contained bundle |
| `sovereign-immigration-0.2.0.tar.gz.sha256` | archive checksum |

### Transfer across the air-gap

Copy both files by removable media (hardware token, approved USB). Verify
the archive checksum **before** extracting:

```bash
shasum -a 256 -c sovereign-immigration-0.2.0.tar.gz.sha256
tar -xzf sovereign-immigration-0.2.0.tar.gz
cd sovereign-immigration-0.2.0
```

### On the target (offline)

```bash
./install.sh                    # -> /opt/sovereign-immigration
./install.sh --with-service     # + systemd unit (as root)
```

`install.sh` verifies `MANIFEST.sha256` (every file) and **aborts on any
mismatch** before touching the system. It then checks the Python runtime
and `cryptography`, installs, writes a `chmod 600` `.env`, and optionally
enables the hardened systemd unit.

### Run

```bash
set -a; . /opt/sovereign-immigration/.env; set +a
python3 /opt/sovereign-immigration/services/api/server.py
curl http://127.0.0.1:8787/health
```

---

## 2. Container deployment

```bash
docker build -t sovereign-immigration:0.2 .
docker run -d -p 8787:8787 \
    -v /var/lib/sie:/data \
    -e API_TOKEN=change-me \
    sovereign-immigration:0.2
```

The image is stdlib + `cryptography` only (~no ML stack). OCR is optional.

---

## Security posture

| Control | Setting |
|---------|---------|
| Process user | non-root (`sie`) |
| systemd hardening | `ProtectSystem=strict`, `ProtectHome`, `NoNewPrivileges` |
| Secrets | `.env` chmod 600, never committed |
| Bundle integrity | per-file SHA-256 manifest + archive checksum |
| API auth | bearer token via `API_TOKEN` (open only if unset) |
| Audit | append-only hash chain, optional KISA RFC-3161 timestamp |

---

## Configuration

All via environment (see `.env`):

| Var | Default | Notes |
|-----|---------|-------|
| `HOST` | `127.0.0.1` | bind address |
| `PORT` | `8787` | listen port |
| `API_TOKEN` | *(empty)* | if set, `/v1/*` requires `Authorization: Bearer` |
| `AUDIT_DB` | `./sovereign_audit.db` | ledger location |
| `KISA_ENABLED` | `false` | enable RFC-3161 timestamps |
| `KISA_ENDPOINT` | KISA TSA | timestamp authority URL |
| `KISA_API_KEY` | *(empty)* | TSA bearer token |

---

## Optional: OCR / document scanning

The API runs without it. To enable image ingestion on a target that has
the ML stack installed:

```bash
pip install cryptography easyocr opencv-python pillow numpy torch torchvision
```

These load lazily — the core compliance engine never imports them.