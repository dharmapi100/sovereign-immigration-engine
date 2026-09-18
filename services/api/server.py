"""
Sovereign Immigration Engine — HTTP API
=======================================
Zero-dependency REST surface (Python stdlib only) so the whole product
runs in an air-gapped environment with no `pip install`. This is the
integration surface every downstream system talks to.

Endpoints:
    GET  /health                      liveness
    GET  /ready                       readiness (ledger + policy loaded)
    GET  /v1/pipa/manifest            PIPA Article-as-Code manifest
    POST /v1/visa/evaluate            {visa, applicant} -> eligibility
    POST /v1/visa/evaluate-all        {applicant} -> all visa classes
    POST /v1/pipeline/ingest          {doc_b64, key_b64} -> run KYC pipeline
    GET  /v1/audit                     recent audit entries
    GET  /v1/audit/verify             chain integrity bool
    GET  /v1/audit/{hash}             single audit record

Auth: bearer token via API_TOKEN env var (if unset, no auth — dev mode).
"""

from __future__ import annotations

import base64
import json
import os
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, "services")) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)

for _p in ["services/audit-ledger", "services/visa-policy", "services/pipa-dsl",
           "services/kyc-pipeline", "services/kyc-pipeline/ocr",
           "services/kyc-pipeline/ocr/preprocessor", "services/doc-classifier",
           "services/visa-validation", "services/fleet-orchestrator",
           "services/policy-matching", "services/compliance-dashboard"]:
    _full = os.path.join(_ROOT, _p)
    if _full not in sys.path:
        sys.path.insert(0, _full)

from ledger import AuditLedger  # noqa: E402
from kisa_client import KISATimestampClient  # noqa: E402
from evidence import EvidenceService  # noqa: E402
from compiler import PIPACompiler  # noqa: E402
from engine import VisaPolicyEngine  # noqa: E402

API_TOKEN = os.getenv("API_TOKEN", "")
DB_PATH = os.getenv("AUDIT_DB", os.path.join(_ROOT, "sovereign_audit.db"))

_ledger = AuditLedger(DB_PATH)
_evidence = EvidenceService(_ledger, KISATimestampClient())
_pipa = PIPACompiler()
_visa = VisaPolicyEngine()
_lock = threading.Lock()


def _read_pipeline():
    """Import the pipeline lazily so a broken OCR stack can't kill the API."""
    from ingestion import KYCExtractor
    return KYCExtractor


class Handler(BaseHTTPRequestHandler):
    server_version = "SovereignImmigration/0.2"

    # ---- helpers ------------------------------------------------------ #
    def _json(self, code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _auth_ok(self) -> bool:
        if not API_TOKEN:
            return True
        return self.headers.get("Authorization", "") == f"Bearer {API_TOKEN}"

    def _body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {}

    def log_message(self, format, *args):  # quieter default logging
        sys.stderr.write("[api] " + format % args + "\n")

    # ---- routing ------------------------------------------------------ #
    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            return self._json(200, {"status": "ok", "service": "sovereign-immigration"})
        if path == "/ready":
            ok = _ledger.verify_chain()
            return self._json(200 if ok else 503,
                              {"status": "ready" if ok else "degraded",
                               "ledger_intact": ok,
                               "entries": _ledger.count()})
        if not self._auth_ok():
            return self._json(401, {"error": "unauthorized"})
        if path == "/v1/pipa/manifest":
            return self._json(200, {"articles": _pipa.describe()})
        if path == "/v1/audit/verify":
            return self._json(200, {"intact": _ledger.verify_chain(),
                                    "entries": _ledger.count()})
        if path == "/v1/audit":
            rows = _ledger._conn.execute(
                """SELECT timestamp, entry_id, action, actor, hash, kisa_timestamp
                   FROM audit_log ORDER BY id DESC LIMIT 50"""
            ).fetchall()
            keys = ["timestamp", "entry_id", "action", "actor", "hash", "kisa_timestamp"]
            return self._json(200, {"entries": [dict(zip(keys, r)) for r in rows]})
        if path.startswith("/v1/audit/"):
            rec = _ledger.get(path.rsplit("/", 1)[-1])
            if rec is None:
                return self._json(404, {"error": "not found"})
            return self._json(200, rec)
        return self._json(404, {"error": "not found", "path": path})

    def do_POST(self):
        path = urlparse(self.path).path
        if not self._auth_ok():
            return self._json(401, {"error": "unauthorized"})
        body = self._body()

        if path == "/v1/visa/evaluate":
            visa = body.get("visa")
            applicant = body.get("applicant", {})
            if not visa:
                return self._json(400, {"error": "visa required"})
            try:
                result = _visa.evaluate(visa, applicant)
            except ValueError:
                return self._json(400, {"error": f"unknown visa: {visa}"})
            with _lock:
                _evidence.record(
                    applicant.get("id", "unknown"), "VISA_EVALUATE", "api",
                    payload={"visa": visa, "eligible": result.eligible},
                    purpose=f"{visa} eligibility")
            return self._json(200, result.to_dict())

        if path == "/v1/visa/evaluate-all":
            applicant = body.get("applicant", {})
            results = [r.to_dict() for r in _visa.evaluate_all(applicant)]
            return self._json(200, {"applicant_id": applicant.get("id", "unknown"),
                                    "results": results})

        if path == "/v1/pipeline/ingest":
            doc_b64 = body.get("doc_b64")
            key_b64 = body.get("key_b64")
            if not doc_b64 or not key_b64:
                return self._json(400, {"error": "doc_b64 and key_b64 required"})
            try:
                doc = base64.b64decode(doc_b64)
                key = base64.b64decode(key_b64)
                KYCExtractor = _read_pipeline()
                extractor = KYCExtractor(key, {}, {}, kisa_client=_evidence.kisa)
                result = extractor.extract_pii(doc)
            except Exception as exc:  # noqa: BLE001 - surface as 500
                return self._json(500, {"error": str(exc)})
            return self._json(200, result)

        return self._json(404, {"error": "not found", "path": path})


def main():
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8787"))
    server = ThreadingHTTPServer((host, port), Handler)
    sys.stderr.write(f"[api] Sovereign Immigration Engine on http://{host}:{port}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()