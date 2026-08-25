import logging
import json
import datetime

class AuditLogger:
    def __init__(self, log_file="access_audit.log"):
        self.logger = logging.getLogger("SovereignAudit")
        handler = logging.FileHandler(log_file)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_access(self, talent_id: str, action: str):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "talent_id": talent_id,
            "action": action
        }
        self.logger.info(json.dumps(entry))
