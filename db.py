import sqlite3
import csv

DB_FILE = "tickets.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id TEXT PRIMARY KEY,
        merchant_id TEXT,
        issue TEXT,
        error TEXT,
        context TEXT,
        time TEXT
    )
    """)
    conn.commit()
    conn.close()

def insert_ticket(ticket):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO tickets(ticket_id, merchant_id, issue, error, context, time)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (ticket['ticket_id'], ticket['merchant_id'], ticket['issue'], ticket['error'], ticket['context'], ticket['time']))
    conn.commit()
    conn.close()

def get_all_tickets():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    rows = cursor.fetchall()
    conn.close()

    tickets = []
    for r in rows:
        tickets.append({
            "ticket_id": r[0],
            "merchant_id": r[1],
            "issue": r[2],
            "error": r[3],
            "context": r[4],
            "time": r[5]
        })
    return tickets

def load_csv(file_path):
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] == "ticket_id":  # skip header
                continue
            ticket = {
                "ticket_id": row[0],
                "merchant_id": row[1],
                "issue": row[2],
                "error": row[3],
                "context": row[4],
                "time": row[5]
            }
            insert_ticket(ticket)
    print(f"✅ Loaded CSV data from {file_path} successfully!")
