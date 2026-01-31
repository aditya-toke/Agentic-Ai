import json

def observe():
    tickets_json = input("Paste tickets JSON: ")
    logs_json = input("Paste logs JSON: ")
    merchants_json = input("Paste merchants JSON: ")

    tickets = json.loads(tickets_json)
    logs = json.loads(logs_json)
    merchants = json.loads(merchants_json)

    return tickets, logs, merchants
