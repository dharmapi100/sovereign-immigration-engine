import json
import time

class AuditMonitor:
    def __init__(self, audit_log_path="access_audit.log"):
        self.audit_log_path = audit_log_path

    def scan_for_unauthorized_access(self):
        # scan logs for anomalous PII extraction attempts
        with open(self.audit_log_path, 'r') as f:
            for line in f:
                entry = json.loads(line)
                if entry.get("action") == "PII_EXTRACT_UNAUTHORIZED":
                    print(f"ALERT: Unauthorized access detected: {entry}")
                    return True
        return False
