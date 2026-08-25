import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_driver import RobotDriver

class SMEDriver(RobotDriver):
    def get_status(self):
        # mock SME-robot api call
        return {"robot_id": "sme_01", "status": "active", "error_code": 0}

    def execute_task(self, task):
        # SME-robot command protocol
        return True
