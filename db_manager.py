import sqlite3
from passlib.hash import bcrypt

DB_FILE = "app_database.db"

# Initialize the database and create/alter tables if needed
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create the users table if it doesn't exist
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            security_token TEXT,
            client_id TEXT,
            client_secret TEXT,
            domain TEXT,
            pin TEXT NOT NULL
        )
    """)

    # Check if new columns exist, if not, add them
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [column[1] for column in cursor.fetchall()]

    if "name" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN name TEXT")
    if "email" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
    if "phone" not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN phone TEXT")

    conn.commit()
    conn.close()

# Add a new user to the database
def register_user(username, password, security_token, client_id, client_secret, domain, pin):
    password_hash = bcrypt.hash(password)
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (username, password_hash, security_token, client_id, client_secret, domain, pin)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, password_hash, security_token, client_id, client_secret, domain, pin))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

# Verify user credentials
def verify_user(username, password, pin):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, pin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        password_hash, stored_pin = result
        if bcrypt.verify(password, password_hash) and pin == stored_pin:
            return True
    return False

# Fetch user data by username
def get_user_data(username):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, security_token, client_id, client_secret, domain, pin, name, email, phone
        FROM users WHERE username = ?
    """, (username,))
    user_data = cursor.fetchone()
    conn.close()
    if user_data:
        return {
            "username": user_data[0],
            "security_token": user_data[1],
            "client_id": user_data[2],
            "client_secret": user_data[3],
            "domain": user_data[4],
            "pin": user_data[5],
            "name": user_data[6],
            "email": user_data[7],
            "phone": user_data[8]
        }
    return None

# Update user profile
def update_user_profile(username, name, email, phone):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users
        SET name = ?, email = ?, phone = ?
        WHERE username = ?
    """, (name, email, phone, username))
    conn.commit()
    conn.close()
