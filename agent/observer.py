def observe(state, tickets):
    """
    Observe incoming tickets and store them for reasoning
    """
    state.observations = {
        "tickets": tickets
    }
