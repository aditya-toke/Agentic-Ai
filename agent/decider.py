def decide(state):
    """
    Decide what action to take based on hypotheses.
    Handles uncertainty safely.
    """

    # 🟡 Case 1: No hypothesis → insufficient evidence
    if not state.hypotheses:
        state.decision = {
            "status": "no_action",
            "reason": "Insufficient evidence to determine root cause",
            "confidence": 0.0,
            "risk": "Low"
        }
        return

    # 🟢 Case 2: Use strongest hypothesis
    primary = state.hypotheses[0]

    # 🔴 High-risk actions are blocked
    if primary.get("risk") == "High":
        state.decision = {
            "status": "blocked",
            "reason": "Proposed action affects money or live checkouts",
            "confidence": primary.get("confidence", 0.0),
            "risk": "High"
        }
        return

    # 🟢 Safe proposal
    state.decision = {
        "status": "proposed",
        "root_cause": primary.get("cause"),
        "confidence": primary.get("confidence", 0.0),
        "risk": primary.get("risk", "Medium")
    }
