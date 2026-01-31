import json

def observe():
    with open("data/tickets.json") as f:
        tickets = json.load(f)

    with open("data/logs.json") as f:
        logs = json.load(f)

    with open("data/merchants.json") as f:
        merchants = json.load(f)

    return tickets, logs, merchants
