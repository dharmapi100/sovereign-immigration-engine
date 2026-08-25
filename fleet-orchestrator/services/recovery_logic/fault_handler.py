class FaultHandler:
    @staticmethod
    def resolve_maintenance_fault(robot_id: str):
        # logic for automated rerouting or safety stop
        return {"status": "rerouted", "safety_stop": False}

    @staticmethod
    def emergency_shutdown(robot_id: str):
        # critical failure response
        return {"status": "shutdown", "safety_stop": True}
