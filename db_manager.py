
import sqlite3
import os
from passlib.hash import bcrypt

DB_FILE = "app_database.db"

# Initialize the database and create tables if they don't exist
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
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
        SELECT username, security_token, client_id, client_secret, domain, pin
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
            "pin": user_data[5]
        }
    return None