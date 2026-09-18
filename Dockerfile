# =============================================================================
# Sovereign Immigration Engine — container image
# =============================================================================
# Minimal image: stdlib + cryptography only (no web framework, no ML stack).
# OCR/classification are optional and loaded lazily; install the `ocr` extra
# layer only where document scanning is required.
#
#   docker build -t sovereign-immigration:0.2 .
#   docker run -p 8787:8787 sovereign-immigration:0.2
# =============================================================================
FROM python:3.12-slim

LABEL org.opencontainers.image.title="Sovereign Immigration Engine" \
      org.opencontainers.image.description="PIPA-compliant visa + KYC API with evidence-grade audit" \
      org.opencontainers.image.version="0.2.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HOST=0.0.0.0 \
    PORT=8787 \
    AUDIT_DB=/data/sovereign_audit.db

WORKDIR /app

# Core dependency (audit/evidence only come from stdlib + cryptography)
RUN pip install --no-cache-dir "cryptography>=42"

COPY services/ /app/services/
COPY tests/ /app/tests/
COPY README.md /app/README.md

# Non-root, writable ledger volume
RUN useradd -r -u 10001 sie && mkdir -p /data && chown -R sie:sie /data /app
USER sie
VOLUME ["/data"]

EXPOSE 8787

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python3 -c "import urllib.request,sys; \
sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8787/health').status==200 else 1)"

CMD ["python3", "/app/services/api/server.py"]