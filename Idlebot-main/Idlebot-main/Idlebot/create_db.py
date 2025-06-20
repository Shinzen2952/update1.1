import sqlite3

conn = sqlite3.connect('users.db')

cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE
    )
''')


conn.commit()
conn.close()

print("✅ users.db and users table created!")
