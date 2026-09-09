# Sovereign Guardrail: Operational Hardening Spec

## 1. Zero-Trust Audit Integrity
*   **Cryptographic Chaining:** Current ledger uses SHA-256 chaining. Extending to include `PreviousHash` verification in every new entry to detect ledger tampering.
*   **Remote Attestation:** Generate an hourly heartbeat signature signed by an embedded private key, allowing remote administrators to verify the proxy process hasn't been injected or halted.

## 2. Resource Management & Bottleneck Mitigation
*   **Buffered Async Logging:** SQLite writes currently block the request thread. Refactoring to a buffered channel-based log-writer to decouple audit-IO from proxy-latency.
*   **Memory Paging:** Limit `io.ReadAll` for payloads > 10MB; partial inspection of headers/metadata to prevent OOM errors on large file uploads.

## 3. Deployment Reliability
*   **Healthcheck Endpoint:** Added `GET /health` with internal connectivity status to Naver/NHN and SQLite integrity status.
*   **Self-Healing:** Systemd unit configuration to auto-restart on panic with backoff limit.
*   **Secret Management:** Move `sovereign-key` from hardcoded constant to encrypted `env` variable or mounted secret path (e.g., `/run/secrets/`).

## 4. Implementation Schedule
1.  **Async Buffer (Immediate):** Decouple IO to prevent latency spikes.
2.  **Secret Rotation:** Implement secure credential injection.
3.  **Heartbeat:** Expose internal health state for monitoring dashboards.

---
### Updated Proxy Core Logic
```go
// ... logic for async log buffer
var auditChan = make(chan AuditEntry, 1000)

func worker() {
    for entry := range auditChan {
        // batched sqlite writes
    }
}
```
***
Ready to commit these changes to the proxy logic and build the deployment hardening suite. Urgency is high.
