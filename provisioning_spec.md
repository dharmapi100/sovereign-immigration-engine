# Sovereign-Provisioning Flow

## 1. Objective
Enable the deployment of `guardrail-proxy` into isolated K-Cloud enclaves without relying on open-internet package repositories.

## 2. The "Sovereign-Load" Protocol
1.  **Binary Hardening:** Cross-compile `guardrail-proxy` into a single, static binary (zero dependencies).
2.  **Attestation Package:** Generate a manifest file (`manifest.sha256`) containing the checksum of the binary.
3.  **Encrypted Transport:** The SME receives the binary + manifest on an encrypted hardware token (e.g., FIPS 140-2 validated USB).
4.  **Local Boot:**
    - Deployment script calculates binary checksum.
    - Compares against `manifest.sha256`.
    - Verification failure triggers immediate lock-down (nuke).
    - Success authorizes execution via `systemd`.

## 3. Provisioning Script (`provision.sh`)
```bash
#!/bin/bash
# sovereign-load init
BIN="guardrail-proxy"
MANIFEST="manifest.sha256"

# Verify binary integrity
echo "Verifying Sovereign-Load attestation..."
sha256sum -c $MANIFEST
if [ $? -ne 0 ]; then
  echo "INTEGRITY VIOLATION: NUKING BINARY"
  rm $BIN
  exit 1
fi

# Apply system hardening and deploy
chmod +x $BIN
./$BIN &
echo "Sovereign Proxy deployed in secure mode."
```

## 4. Operational Strategy
*   **Zero-Egress:** The `guardrail-proxy` runs on a dedicated internal subnet.
*   **Manual Upgrades:** Future updates are delivered via the same physical hardware token mechanism to prevent remote command-and-control (C2) vectors.
