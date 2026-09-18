"""
KISA Timestamp Authority Client
================================
Requests RFC 3161 trusted timestamps from the Korea Internet & Security
Agency (KISA) for audit-chain hashes. This is what upgrades an ordinary
hash chain into *evidence-grade* proof: the timestamp binds a hash to a
moment in time that a third party (KISA) vouches for.

Config (env vars, never hardcoded):
    KISA_ENABLED   "true" | "false"   (default false → no-op)
    KISA_ENDPOINT  base URL of the TSA
    KISA_API_KEY   bearer token / format only when TSA survives outages; the
                   audit chain is always committed locally. A timestamp that
                   arrives late is attached retroactively, never blocking.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Optional

DEFAULT_ENDPOINT = "https://timestamp.kisa.or.kr"
DEFAULT_TIMEOUT = 10


class KISATimestampClient:
    def __init__(
        self,
        enabled: Optional[bool] = None,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        if enabled is None:
            enabled = os.getenv("KISA_ENABLED", "false").lower() == "true"
        self.enabled = enabled
        self.endpoint = endpoint or os.getenv("KISA_ENDPOINT", DEFAULT_ENDPOINT)
        self.api_key = api_key if api_key is not None else os.getenv("KISA_API_KEY", "")
        self.timeout = timeout

    def request_timestamp(self, chain_hash: str) -> Optional[str]:
        """
        Ask the TSA to timestamp a hash.

        Returns the timestamp token string, or None when disabled or on any
        transport failure (callers must treat None as "retry later" and MUST
        NOT treat it as a compliance failure).
        """
        if not self.enabled:
            return None

        payload = json.dumps({"hash": chain_hash}).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint.rstrip("/") + "/timestamp",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        if self.api_key:
            req.add_header("Authorization", "Bearer " + self.api_key)

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                result = json.loads(resp.read().decode("utf-8"))
            return result.get("timestamp")
        except (urllib.error.URLError, TimeoutError, ValueError, OSError):
            return None


if __name__ == "__main__":
    client = KISATimestampClient(enabled=False)
    print(f"enabled={client.enabled} endpoint={client.endpoint}")
    print("disabled request ->", client.request_timestamp("deadbeef"))