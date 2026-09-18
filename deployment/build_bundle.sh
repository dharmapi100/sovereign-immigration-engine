#!/usr/bin/env bash
# =============================================================================
# build_bundle.sh — Build an offline (air-gap) deployment bundle
# =============================================================================
# Produces: dist/sovereign-immigration-<version>.tar.gz
#           dist/sovereign-immigration-<version>.sha256
#
# The bundle is self-contained: source + manifest + install script + systemd
# unit, with a SHA-256 manifest of every file so the target can verify
# integrity before installing. No network access is required at build time
# beyond what is already on the build host.
# =============================================================================
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION="${1:-0.2.0}"
DIST="$REPO_ROOT/dist"
STAGE="$DIST/sovereign-immigration-$VERSION"

rm -rf "$STAGE"
mkdir -p "$STAGE"

echo "[bundle] staging v$VERSION -> $STAGE"

# Copy source (exclude dev artefacts)
for item in services tests deployment README.md LICENSE .gitignore; do
    if [ -e "$REPO_ROOT/$item" ]; then
        cp -R "$REPO_ROOT/$item" "$STAGE/"
    fi
done

# Deployment scripts live at the bundle root for the operator
cp "$REPO_ROOT/deployment/install.sh" "$STAGE/install.sh" 2>/dev/null || true
cp "$REPO_ROOT/deployment/sovereign-immigration.service" "$STAGE/" 2>/dev/null || true

# Drop caches the copy may have carried
find "$STAGE" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -name "*.pyc" -delete 2>/dev/null || true

# ---------------------------------------------------------------------------
# Integrity manifest — SHA-256 of every file, sorted, deterministic
# ---------------------------------------------------------------------------
MANIFEST="$STAGE/MANIFEST.sha256"
( cd "$STAGE" && find . -type f ! -name MANIFEST.sha256 -print0 \
    | sort -z \
    | xargs -0 shasum -a 256 > "$MANIFEST" )
echo "[bundle] wrote manifest ($(wc -l < "$MANIFEST") files)"

# ---------------------------------------------------------------------------
# Archive + top-level checksum
# ---------------------------------------------------------------------------
ARCHIVE="$DIST/sovereign-immigration-$VERSION.tar.gz"
( cd "$DIST" && tar -czf "$(basename "$ARCHIVE")" "$(basename "$STAGE")" )
shasum -a 256 "$ARCHIVE" > "$ARCHIVE.sha256"

echo "[bundle] archive:    $ARCHIVE"
echo "[bundle] checksum:   $ARCHIVE.sha256"
echo "[bundle] sha256:     $(cut -d' ' -f1 < "$ARCHIVE.sha256")"
echo
echo "Transfer these two files across the air-gap, then run:"
echo "  tar -xzf $(basename "$ARCHIVE")"
echo "  cd $(basename "$STAGE") && ./install.sh"