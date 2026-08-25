from abc import ABC, abstractmethod

class RobotDriver(ABC):
    @abstractmethod
    def get_status(self) -> dict:
        """Returns unified status: {robot_id, status, error_code}."""
        pass

    @abstractmethod
    def execute_task(self, task: dict) -> bool:
        """Dispatches task to specific vendor hardware."""
        pass
