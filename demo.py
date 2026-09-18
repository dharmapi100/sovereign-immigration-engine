#!/usr/bin/env python3
"""
Sovereign Immigration Engine — end-to-end demo
==============================================
Starts the API in-process and walks through the full flow:
  1. PIPA Article-as-Code manifest
  2. D-8-4 founder eligibility (with citations)
  3. E-7 professional eligibility
  4. Document ingest with PII redaction
  5. Audit chain integrity verification
  6. Tamper detection

Run:  python3 demo.py
"""

import base64
import json
import sys
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "services" / "api"))
sys.path.insert(0, str(ROOT / "services" / "audit-ledger"))
sys.path.insert(0, str(ROOT / "services" / "kyc-pipeline"))
sys.path.insert(0, str(ROOT / "services" / "kyc-pipeline" / "ocr"))
sys.path.insert(0, str(ROOT / "services" / "kyc-pipeline" / "ocr" / "preprocessor"))
sys.path.insert(0, str(ROOT / "services" / "visa-policy"))
sys.path.insert(0, str(ROOT / "services" / "pipa-dsl"))
sys.path.insert(0, str(ROOT / "services" / "doc-classifier"))
sys.path.insert(0, str(ROOT / "services" / "visa-validation"))
sys.path.insert(0, str(ROOT / "services" / "fleet-orchestrator"))
sys.path.insert(0, str(ROOT / "services" / "policy-matching"))
sys.path.insert(0, str(ROOT / "services" / "compliance-dashboard"))

import server as api  # noqa: E402

try:
    from cryptography.fernet import Fernet
    HAS_CRYPTO = True
except ImportError:
    HAS_CRYPTO = False


def hr(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def main():
    api._ledger = api.AuditLedger(":memory:")
    api._evidence = api.EvidenceService(api._ledger, api.KISATimestampClient(enabled=False))
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
    port = httpd.server_address[1]
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"

    def get(path):
        with urllib.request.urlopen(base + path) as r:
            return json.loads(r.read())

    def post(path, payload):
        req = urllib.request.Request(base + path, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"},
                                     method="POST")
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read())

    hr("1. PIPA Article-as-Code manifest")
    m = get("/v1/pipa/manifest")
    for art, info in m["articles"].items():
        print(f"  {art:<8} {info['title']}")

    hr("2. D-8-4 founder eligibility")
    r = post("/v1/visa/evaluate", {"visa": "D-8-4", "applicant": {
        "id": "founder_kim", "investment_capital_krw": 150_000_000,
        "business_plan": True, "incubator_letter": True,
        "ip_assets": ["PIPA-Article-Compiler"]}})
    print(f"  eligible={r['eligible']}  score={r['score']}/{r['max_score']}")
    for rule in r["rules"]:
        mark = "PASS" if rule["passed"] else "FAIL"
        print(f"    [{mark}] {rule['rule_id']:<12} {rule['reason']}")
        print(f"           └ cite: {rule['citation']}")

    hr("3. E-7 professional eligibility")
    r = post("/v1/visa/evaluate", {"visa": "E-7", "applicant": {
        "id": "eng_lee", "degree": "master", "job_offer": True,
        "salary_krw": 50_000_000, "occupation_in_list": True}})
    print(f"  eligible={r['eligible']}  score={r['score']}/{r['max_score']}")

    hr("4. Document ingest + PIPA redaction")
    if HAS_CRYPTO:
        key = Fernet.generate_key()
        doc = {"id": "applicant_park", "name": "Park", "consent": True,
               "ocr_text": "신청인 900101-1234567 여권 M1234567"}
        enc = Fernet(key).encrypt(json.dumps(doc).encode())
        r = post("/v1/pipeline/ingest", {
            "doc_b64": base64.b64encode(enc).decode(),
            "key_b64": base64.b64encode(key).decode()})
        print(f"  valid={r['validation']['valid']}")
        print(f"  raw:      신청인 900101-1234567 여권 M1234567")
        print(f"  redacted: {r['ocr_text']}")
        print(f"  PIPA decisions:")
        for d in r["pipa"]:
            print(f"    {d['article']:<8} {d['outcome']:<7} {d['reason']}")
    else:
        print("  (cryptography not installed — skipping ingest)")

    hr("5. Audit chain integrity")
    v = get("/v1/audit/verify")
    print(f"  entries={v['entries']}  intact={v['intact']}")
    listing = get("/v1/audit")
    for e in listing["entries"][:5]:
        print(f"    {e['action']:<16} {e['entry_id']:<16} {e['hash'][:16]}…")

    hr("6. Tamper detection")
    original = api._ledger._conn.execute(
        "SELECT hash FROM audit_log WHERE id=1").fetchone()[0]
    api._ledger._conn.execute("UPDATE audit_log SET hash='deadbeef' WHERE id=1")
    api._ledger._conn.commit()
    v = get("/v1/audit/verify")
    print(f"  after tampering id=1: intact={v['intact']}  (expected False)")
    # restore
    api._ledger._conn.execute("UPDATE audit_log SET hash=? WHERE id=1", (original,))
    api._ledger._conn.commit()
    v = get("/v1/audit/verify")
    print(f"  after restore:        intact={v['intact']}  (expected True)")

    httpd.shutdown()
    hr("DEMO COMPLETE")


if __name__ == "__main__":
    main()
