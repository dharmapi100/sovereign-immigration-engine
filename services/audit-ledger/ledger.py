import hashlib
import json

class AuditLedger:
    def __init__(self, log_path="access_audit.log"):
        self.log_path = log_path

    def record_transaction(self, entry_id: str, status: str):
        with open(self.log_path, 'a') as f:
            f.write(f"{entry_id}:{status}\n")
