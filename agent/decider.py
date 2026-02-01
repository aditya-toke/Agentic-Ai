from agent.feedback import feedback_learner

def decide(state):
    if not state.hypotheses:
        state.decision = {"status": "no_action"}
        return

    primary = state.hypotheses[0]
    error_type = primary["cause"]

    learned_action = feedback_learner.best_action(error_type)

    if learned_action:
        action = learned_action
        confidence = min(primary["confidence"] + 0.15, 0.95)
    else:
        action = "Notify merchant with setup guide"
        confidence = primary["confidence"]

    state.decision = {
        "status": "action_proposed",
        "root_cause": error_type,
        "action": action,
        "confidence": round(confidence, 2),
        "risk": primary["risk"]
    }
