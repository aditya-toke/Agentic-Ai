import sqlite3

DB_NAME = "tickets.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
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

    
def update_ticket_status(ticket_id, status):
    conn = sqlite3.connect("agentic_ai.db")
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tickets SET status=? WHERE ticket_id=?",
        (status, ticket_id)
    )
    conn.commit()
    conn.close()


def insert_ticket(ticket):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ticket["ticket_id"],
        ticket["merchant_id"],
        ticket["issue"],
        ticket["error"],
        ticket["context"],
        ticket["time"]
    ))

    conn.commit()
    conn.close()


def get_all_tickets():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("SELECT * FROM tickets")
    rows = c.fetchall()
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
