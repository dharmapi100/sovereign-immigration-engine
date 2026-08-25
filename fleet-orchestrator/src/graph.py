import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../services/sovereign-sidecar'))

import random
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Any
from sovereign_sidecar.encryptor import SovereignEncryptor

class FleetState(TypedDict):
    robot_ids: List[str]
    tasks: List[Any]
    assignments: dict
    error_report: dict

import sys
import os
# sys.path hacking is fragile. Use absolute path to the project root.
# System paths
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'tests/fuzzer'))

from robot_drivers.manager import RobotManager
from recovery_logic.fault_handler import FaultHandler
from sovereign_sidecar.encryptor import SovereignEncryptor

def ingest_sensor_data(encrypted_data: bytes) -> dict:
    """Decrypts incoming sensor data stream before processing."""
    return encryptor.decrypt_sensor_input(encrypted_data)

def mock_robot_status():
    # simulate robot error codes
    return {"robot_id": "robot_01", "error": "low_battery"}

from robot_drivers.manager import RobotManager

# Initialize manager and encryptor
manager = RobotManager()
encryptor = SovereignEncryptor(key_file="secure.key")

def orchestrator_node(state: FleetState):
    # dynamic injection from sensor stream
    if not state['tasks']:
        # simulate receiving and decrypting sensor data
        test_payload = {"task_id": f"task_{random.randint(100, 999)}", "priority": "high"}
        raw_sensor_data = encryptor.secure_sensor_input(test_payload)
        new_task = ingest_sensor_data(raw_sensor_data)
        state['tasks'].append(new_task)
        
    assignments = {}
    
    # integrate real status reports from robot drivers
    fleet_status = manager.get_all_status()
    
    for robot_type, status in fleet_status.items():
        if status['error_code'] != 0:
            assignments[robot_type] = FaultHandler.resolve_maintenance_fault(robot_type)
        elif state['tasks']:
            task = state['tasks'].pop(0)
            manager.dispatch(robot_type, task)
            assignments[robot_type] = task
        else:
            assignments[robot_type] = "standby"
    return {"assignments": assignments, "error_report": fleet_status}

workflow = StateGraph(FleetState)
workflow.add_node("orchestrator", orchestrator_node)
workflow.set_entry_point("orchestrator")
workflow.add_edge("orchestrator", END)

app = workflow.compile()
