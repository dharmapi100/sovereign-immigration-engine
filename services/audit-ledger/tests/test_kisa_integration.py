"""
KISA timestamp integration test
===============================
Spins up a mock RFC-3161-style TSA over HTTP and proves the client actually
round-trips: enabled client -> POST /timestamp -> token returned -> attached
to the audit chain. This closes the gap where the client was only exercised
in its disabled (no-op) mode.
"""

import json
import os
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from ledger import AuditEntry, AuditLedger  # noqa: E402
from kisa_client import KISATimestampClient  # noqa: E402
from evidence import EvidenceService  # noqa: E402


class MockTSA(BaseHTTPRequestHandler):
    seen = []

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length) or b"{}")
        MockTSA.seen.append(body)
        resp = json.dumps({"status": "ok",
                           "timestamp": "2026-09-18T00:00:00Z(kisa-mock)"}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(resp)))
        self.end_headers()
        self.wfile.write(resp)

    def log_message(self, *a):
        pass


class TestKISAIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.down = False
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), MockTSA)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def setUp(self):
        MockTSA.seen.clear()
        self.ledger = AuditLedger(":memory:")
        self.client = KISATimestampClient(
            enabled=True, endpoint=f"http://127.0.0.1:{self.port}", api_key="test")

    def tearDown(self):
        self.ledger.close()

    def test_client_round_trip(self):
        ts = self.client.request_timestamp("abc123")
        self.assertIsNotNone(ts)
        self.assertIn("kisa-mock", ts)
        self.assertEqual(MockTSA.seen[-1]["hash"], "abc123")

    def test_timestamp_attached_to_chain(self):
        svc = EvidenceService(self.ledger, self.client)
        rec = svc.record("v1", "VISA_APPLICATION", "officer.kim",
                         payload={"visa": "D-8-4"}, purpose="review")
        self.assertTrue(rec["timestampped"])
        self.assertIn("kisa-mock", rec["kisa_timestamp"])
        self.assertTrue(self.ledger.verify_chain())

    def test_tsa_failure_is_failsafe(self):
        # point at a dead port — record must still succeed, un-timestamped
        dead = KISATimestampClient(enabled=True, endpoint="http://127.0.0.1:1")
        svc = EvidenceService(self.ledger, dead)
        rec = svc.record("v2", "VISA_APPLICATION", "officer.kim")
        self.assertFalse(rec["timestampped"])
        self.assertTrue(self.ledger.verify_chain())  # ledger unaffected
        self.assertEqual(self.ledger.count(), 1)


if __name__ == "__main__":
    unittest.main()