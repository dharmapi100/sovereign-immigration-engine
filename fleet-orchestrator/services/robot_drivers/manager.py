import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from robot_drivers.drivers.hyundai_driver import HyundaiDriver
from robot_drivers.drivers.sme_driver import SMEDriver

class RobotManager:
    def __init__(self):
        self.drivers = {
            "hyundai": HyundaiDriver(),
            "sme": SMEDriver()
        }

    def get_all_status(self) -> dict:
        return {k: v.get_status() for k, v in self.drivers.items()}

    def dispatch(self, robot_type: str, task: dict) -> bool:
        from graph import encryptor
        # PQC secured command dispatch
        encrypted_task = encryptor.secure_sensor_input(task)
        driver = self.drivers.get(robot_type)
        if driver:
            # Simulated: driver receives encrypted signal
            return driver.execute_task({"data": encrypted_task})
        return False
