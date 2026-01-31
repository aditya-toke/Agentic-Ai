def decide(state):
    primary = state.hypotheses[0]

    if primary["risk"] == "High":
        state.decision = {
            "status": "blocked",
            "reason": "High-risk action blocked"
        }
    else:
        state.decision = {
            "status": "proposed",
            "root_cause": primary["cause"],
            "confidence": primary["confidence"],
            "risk": primary["risk"]
        }
