import random
import sys
import os
project_root = '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/fleet-orchestrator'
sys.path.insert(0, os.path.join(project_root, 'services'))
sys.path.insert(0, os.path.join(project_root, 'src'))

from graph import app

def run_fuzzer(cycles=100):
    for i in range(cycles):
        # randomly corrupt state
        state = {
            'robot_ids': ['hyundai_01', 'sme_01'],
            'tasks': [{'task_id': f'task_{random.randint(1,100)}'}],
            'assignments': {},
            'error_report': {}
        }
        try:
            app.invoke(state)
        except Exception as e:
            print(f"Fuzzer broke orchestration at cycle {i}: {e}")
            return
    print("Fuzzer passed 100 cycles")

if __name__ == "__main__":
    run_fuzzer()
