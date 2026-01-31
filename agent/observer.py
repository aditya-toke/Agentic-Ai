import json

def observe():
    tickets_json = input("Paste tickets JSON: ")
    logs_json = input("Paste logs JSON: ")
    merchants_json = input("Paste merchants JSON: ")

    tickets = json.loads(tickets_json)
    logs = json.loads(logs_json)
    merchants = json.loads(merchants_json)


    with open("data/tickets.json") as f:
        tickets = json.load(f)

    with open("data/logs.json") as f:
        logs = json.load(f)

    with open("data/merchants.json") as f:
        merchants = json.load(f)

    return tickets, logs, merchants