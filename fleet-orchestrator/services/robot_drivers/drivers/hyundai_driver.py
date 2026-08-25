import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_driver import RobotDriver

class HyundaiDriver(RobotDriver):
    def get_status(self):
        # mock hyundai-specific api call
        return {"robot_id": "hyundai_01", "status": "active", "error_code": 1}

    def execute_task(self, task):
        # hyundai-specific command protocol
        return True
