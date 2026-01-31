from db import init_db, load_csv

init_db()  # Make sure DB exists
load_csv("tickets.csv")  # Load all dummy CSV tickets
