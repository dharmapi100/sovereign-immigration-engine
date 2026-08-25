import random

class FaultFuzzer:
    @staticmethod
    def inject_random_fault(robot_id: str):
        # randomly simulate high-frequency failures
        faults = ["low_battery", "network_timeout", "sensor_calibration_error", "critical_shutdown"]
        return {"robot_id": robot_id, "error": random.choice(faults)}
