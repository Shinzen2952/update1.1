import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS shelf (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    title TEXT NOT NULL,
    img TEXT,
    UNIQUE(user_id, title),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
''')

conn.commit()
conn.close()
