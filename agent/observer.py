def observe(state, tickets):
    state.observations = {
        "tickets": tickets,
        "ticket_count": len(tickets)
    }
