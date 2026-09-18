#!/usr/bin/env bash
# =============================================================================
# install.sh — Offline (air-gap) installer for Sovereign Immigration Engine
# =============================================================================
# Runs entirely offline. Steps:
#   1. Verify the bundle MANIFEST.sha256 (abort on any mismatch)
#   2. Verify Python + cryptography availability
#   3. Install to $PREFIX, write env config
#   4. Optionally install + start the systemd service (needs root)
#
# Usage:
#   ./install.sh                 # install to /opt/sovereign-immigration
#   PREFIX=~/sie ./install.sh    # custom prefix
#   ./install.sh --with-service  # also install systemd unit (root)
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PREFIX="${PREFIX:-/opt/sovereign-immigration}"
WITH_SERVICE=0
[[ "${1:-}" == "--with-service" ]] && WITH_SERVICE=1

echo "=== Sovereign Immigration Engine — offline install ==="
echo "[1/5] verifying bundle integrity"

if [ ! -f "$HERE/MANIFEST.sha256" ]; then
    echo "FATAL: MANIFEST.sha256 missing — refusing to install" >&2
    exit 1
fi

if command -v shasum >/dev/null 2>&1; then
    ( cd "$HERE" && shasum -a 256 -c MANIFEST.sha256 --quiet ) \
        || { echo "FATAL: checksum mismatch — bundle tampered or corrupt" >&2; exit 2; }
else
    ( cd "$HERE" && sha256sum -c MANIFEST.sha256 --quiet ) \
        || { echo "FATAL: checksum mismatch — bundle tampered or corrupt" >&2; exit 2; }
fi
echo "      integrity OK ($(wc -l < "$HERE/MANIFEST.sha256") files verified)"

echo "[2/5] checking runtime"
PY="$(command -v python3 || true)"
[ -z "$PY" ] && { echo "FATAL: python3 not found" >&2; exit 3; }
"$PY" - <<'PYEOF' || { echo "FATAL: python3 >=3.10 and 'cryptography' required" >&2; exit 3; }
import sys
assert sys.version_info >= (3, 10), sys.version
try:
    import cryptography  # noqa
except ImportError:
    raise SystemExit("cryptography not installed")
PYEOF
echo "      runtime OK ($("$PY" --version 2>&1))"

echo "[3/5] installing to $PREFIX"
mkdir -p "$PREFIX"
cp -R "$HERE/services" "$HERE/tests" "$PREFIX/" 2>/dev/null || true
cp "$HERE/README.md" "$PREFIX/" 2>/dev/null || true

echo "[4/5] writing default environment"
ENV_FILE="$PREFIX/.env"
if [ ! -f "$ENV_FILE" ]; then
    cat > "$ENV_FILE" <<'ENVEOF'
# Sovereign Immigration Engine configuration
HOST=127.0.0.1
PORT=8787
# Set a bearer token to require auth on /v1/* endpoints
API_TOKEN=
# Audit ledger location
AUDIT_DB=/opt/sovereign-immigration/sovereign_audit.db
# KISA timestamp authority (RFC 3161)
KISA_ENABLED=false
KISA_ENDPOINT=https://timestamp.kisa.or.kr
KISA_API_KEY=
ENVEOF
    chmod 600 "$ENV_FILE"
    echo "      wrote $ENV_FILE (chmod 600)"
else
    echo "      kept existing $ENV_FILE"
fi

echo "[5/5] service install"
if [ "$WITH_SERVICE" -eq 1 ]; then
    if [ "$(id -u)" -ne 0 ]; then
        echo "      --with-service needs root; skipping" >&2
    else
        sed "s#__PREFIX__#$PREFIX#g" "$HERE/sovereign-immigration.service" \
            > /etc/systemd/system/sovereign-immigration.service
        systemctl daemon-reload
        systemctl enable --now sovereign-immigration.service
        echo "      systemd service installed + started"
    fi
else
    echo "      skipped (pass --with-service as root to enable)"
fi

echo
echo "=== install complete ==="
echo "Run the API:"
echo "  set -a; . $PREFIX/.env; set +a"
echo "  python3 $PREFIX/services/api/server.py"
echo "Health check:"
echo "  curl http://127.0.0.1:8787/health"