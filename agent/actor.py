from agent.feedback import feedback_learner

def act(state, approved):
    decision = state.decision

    error_type = decision["root_cause"]
    action = decision["action"]

    feedback_learner.record(
        error_type=error_type,
        action=action,
        approved=approved
    )

    state.action_result = "approved" if approved else "rejected"
