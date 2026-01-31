def act(state, approved):
    if state.decision["status"] == "blocked":
        state.action_result = "blocked"
    else:
        state.action_result = "approved" if approved else "rejected"
