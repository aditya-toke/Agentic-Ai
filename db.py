import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "tickets.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id TEXT PRIMARY KEY,
        merchant_id TEXT,
        issue TEXT,
        error TEXT,
        context TEXT,
        time TEXT,
        status TEXT DEFAULT 'OPEN',
        created_by TEXT
    )
    """)

    conn.commit()
    conn.close()

def insert_ticket(ticket):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (
            ticket_id, merchant_id, issue, error, context, time, status, created_by
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket["ticket_id"],
        ticket["merchant_id"],
        ticket["issue"],
        ticket["error"],
        ticket["context"],
        ticket["time"],
        ticket["status"],
        ticket["created_by"]
    ))
    conn.commit()
    conn.close()

def get_all_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    rows = cursor.fetchall()
    cols = [c[0] for c in cursor.description]
    conn.close()
    return [dict(zip(cols, row)) for row in rows]

def update_ticket_status(ticket_id, status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tickets SET status=? WHERE ticket_id=?",
        (status, ticket_id)
    )
    conn.commit()
    conn.close()
