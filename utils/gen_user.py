import sqlite3

# Connect to SQLite database (creates a new database if it doesn't exist)
conn = sqlite3.connect('users.db')

# Create a cursor object
cursor = conn.cursor()

# Create users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT,
    email TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    disabled BOOLEAN NOT NULL DEFAULT 0
)
''')

# Insert a test user
cursor.execute('''
INSERT INTO users (username, full_name, email, hashed_password, disabled)
VALUES (?, ?, ?, ?, ?)
''', ('ops', 'Test User', 'testuser@example.com', 'ops', 0))

# Commit the changes and close the connection
conn.commit()
conn.close()
