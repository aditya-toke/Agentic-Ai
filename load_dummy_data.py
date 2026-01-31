import json
from db import insert_ticket, init_db

init_db()

with open("data/tickets.json", "r") as f:
    tickets = json.load(f)

for t in tickets:
    insert_ticket(t)

print("✅ Dummy data inserted into SQLite successfully")
