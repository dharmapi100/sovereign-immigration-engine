import base64
import json
import os
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from cryptography.fernet import Fernet

_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, "services")) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, "services/api"))

import server as api  # noqa: E402


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        api._ledger = api.AuditLedger(":memory:")
        api._evidence = api.EvidenceService(api._ledger, api.KISATimestampClient(enabled=False))
        api.API_TOKEN = ""  # dev mode
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), api.Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def _get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}") as r:
            return r.status, json.loads(r.read())

    def _post(self, path, payload):
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}{path}", data=data,
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())

    def test_health(self):
        status, body = self._get("/health")
        self.assertEqual(status, 200)
        self.assertEqual(body["status"], "ok")

    def test_ready(self):
        status, body = self._get("/ready")
        self.assertEqual(status, 200)
        self.assertTrue(body["ledger_intact"])

    def test_pipa_manifest(self):
        status, body = self._get("/v1/pipa/manifest")
        self.assertEqual(set(body["articles"]), {"Art.21", "Art.22", "Art.39"})

    def test_visa_evaluate(self):
        status, body = self._post("/v1/visa/evaluate",
                                  {"visa": "D-8-4", "applicant": {
                                      "id": "f1", "investment_capital_krw": 150_000_000,
                                      "business_plan": True, "incubator_letter": True,
                                      "ip_assets": ["patent"]}})
        self.assertEqual(status, 200)
        self.assertTrue(body["eligible"])

    def test_visa_evaluate_bad_class(self):
        try:
            self._post("/v1/visa/evaluate", {"visa": "Z-9", "applicant": {}})
            self.fail("expected 400")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)

    def test_evaluate_all(self):
        status, body = self._post("/v1/visa/evaluate-all", {"applicant": {"id": "x"}})
        self.assertEqual(len(body["results"]), 4)

    def test_audit_verify_and_retrieve(self):
        self._post("/v1/visa/evaluate",
                   {"visa": "E-7", "applicant": {"id": "carol", "degree": "master",
                                                 "job_offer": True, "salary_krw": 50_000_000,
                                                 "occupation_in_list": True}})
        _, body = self._get("/v1/audit/verify")
        self.assertTrue(body["intact"])
        _, listing = self._get("/v1/audit")
        self.assertGreaterEqual(len(listing["entries"]), 1)
        h = listing["entries"][0]["hash"]
        status, rec = self._get(f"/v1/audit/{h}")
        self.assertEqual(rec["hash"], h)

    def test_pipeline_ingest(self):
        key = Fernet.generate_key()
        doc = {"id": "talent_api", "name": "API", "consent": True,
               "ocr_text": "신청인 900101-1234567"}
        enc = Fernet(key).encrypt(json.dumps(doc).encode())
        status, body = self._post("/v1/pipeline/ingest", {
            "doc_b64": base64.b64encode(enc).decode(),
            "key_b64": base64.b64encode(key).decode(),
        })
        self.assertEqual(status, 200)
        self.assertTrue(body["validation"]["valid"])
        self.assertIn("RRN_REDACTED", body["ocr_text"])

    def test_auth_required_when_token_set(self):
        api.API_TOKEN = "secret"
        try:
            self._get("/v1/audit")
            self.fail("expected 401")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 401)
        finally:
            api.API_TOKEN = ""

    def test_compliance_report(self):
        status, body = self._post("/v1/report", {
            "applicant_id": "rep_1",
            "applicant": {"id": "rep_1", "consent": True,
                          "investment_capital_krw": 150_000_000,
                          "business_plan": True, "incubator_letter": True,
                          "ip_assets": ["patent"]},
            "visa": "D-8-4"})
        self.assertEqual(status, 200)
        self.assertTrue(body["report_hash"])
        self.assertTrue(body["audit_proof"]["intact"])
        self.assertEqual(len(body["visa_decisions"]), 1)

    def test_compliance_report_markdown(self):
        status, body = self._post("/v1/report", {
            "applicant_id": "rep_2",
            "applicant": {"id": "rep_2", "consent": True},
            "format": "markdown"})
        self.assertEqual(status, 200)
        self.assertIn("Compliance Report", body["markdown"])


if __name__ == "__main__":
    unittest.main()