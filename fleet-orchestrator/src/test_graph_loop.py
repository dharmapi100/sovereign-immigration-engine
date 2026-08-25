from graph import app, FleetState

initial_state = FleetState(robot_ids=["hyundai_01", "sme_01"], tasks=[], assignments={}, error_report={})
final_state = app.invoke(initial_state)

print(f"Final assignments: {final_state['assignments']}")
print(f"Final error report: {final_state['error_report']}")
