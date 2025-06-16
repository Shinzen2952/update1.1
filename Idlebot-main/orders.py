import sqlite3

conn = sqlite3.connect('orders.db')
cursor = conn.cursor()

# Add column if it doesn't exist
try:
    cursor.execute("ALTER TABLE orders ADD COLUMN expected_return_date TEXT;")
    print("Column added.")
except sqlite3.OperationalError:
    print("Column already exists or table error.")

conn.commit()
conn.close()
