import hashlib
import json

class AuditLedger:
    def __init__(self, log_path="access_audit.log"):
        self.log_path = log_path

    def generate_ledger_hash(self) -> str:
        # creates a PQC-resistant cryptographic hash of audit history
        hasher = hashlib.sha3_512()
        with open(self.log_path, 'r') as f:
            for line in f:
                hasher.update(line.encode('utf-8'))
        return hasher.hexdigest()
