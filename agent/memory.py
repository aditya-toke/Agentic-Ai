incident_history = []

def remember(state):
    incident_history.append({
        "decision": state.decision,
        "result": state.action_result
    })
