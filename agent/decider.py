def decide(reasoning):
    cause = reasoning["root_cause"]

    if "platform regression" in cause:
        action = "Escalate to engineering and alert all migrated merchants"
    elif "webhook" in cause:
        action = "Send configuration guide to affected merchants"
    else:
        action = "Wait for more data"

    return action
