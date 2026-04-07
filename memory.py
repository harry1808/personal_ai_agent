import sqlite3

conn = sqlite3.connect("memory.db", check_same_thread=False)
cursor = conn.cursor()

# Create table
cursor.execute("""
CREATE TABLE IF NOT EXISTS memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_input TEXT,
    response TEXT
)
""")
conn.commit()


def save_memory(user_input, response):
    cursor.execute(
        "INSERT INTO memory (user_input, response) VALUES (?, ?)",
        (user_input, response)
    )
    conn.commit()


def get_memory():
    cursor.execute("SELECT user_input, response FROM memory ORDER BY id DESC LIMIT 5")
    return cursor.fetchall()