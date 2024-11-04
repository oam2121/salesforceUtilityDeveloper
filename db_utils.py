import sqlite3
from cryptography.fernet import Fernet, InvalidToken
import os

# Path to the key file
KEY_FILE = 'encryption.key'

# Function to generate a key if it doesn't exist
def generate_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, 'wb') as key_file:
            key_file.write(key)

# Function to load the encryption key
def load_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'rb') as key_file:
            return key_file.read()
    else:
        generate_key()
        return load_key()

# Initialize the key and Fernet cipher
generate_key()
key = load_key()
cipher = Fernet(key)

# Function to encrypt data
def encrypt_data(data):
    return cipher.encrypt(data.encode()).decode()

# Function to decrypt data
def decrypt_data(data):
    try:
        return cipher.decrypt(data.encode()).decode()
    except InvalidToken:
        raise ValueError("Decryption failed: Invalid token. Ensure the encryption key is correct.")

# Function to connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect("user_data.db")
    return conn

# Function to initialize the database
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            security_token TEXT,
            client_id TEXT,
            client_secret TEXT,
            domain TEXT,
            pin TEXT,
            name TEXT,
            email TEXT,
            keep_logged_in BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

# Function to save user data
def save_user_data(user_data, keep_logged_in=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Encrypt sensitive information
    password = encrypt_data(user_data['password'])
    security_token = encrypt_data(user_data['security_token'])
    client_id = encrypt_data(user_data['client_id'])
    client_secret = encrypt_data(user_data['client_secret'])
    pin = encrypt_data(user_data['pin'])
    email = encrypt_data(user_data['email'])

    # Insert or update user data
    cursor.execute('''
        INSERT OR REPLACE INTO user_data (id, username, password, security_token, client_id, client_secret, domain, pin, name, email, keep_logged_in)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_data['username'],
        password,
        security_token,
        client_id,
        client_secret,
        user_data['domain'],
        pin,
        user_data['name'],
        email,
        keep_logged_in
    ))
    conn.commit()
    conn.close()

# Function to load user data
def load_user_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM user_data WHERE id = 1')
    row = cursor.fetchone()
    conn.close()

    if row:
        try:
            return {
                'username': row[1],
                'password': decrypt_data(row[2]),
                'security_token': decrypt_data(row[3]),
                'client_id': decrypt_data(row[4]),
                'client_secret': decrypt_data(row[5]),
                'domain': row[6],
                'pin': decrypt_data(row[7]),
                'name': row[8],  # Name is plain text
                'email': decrypt_data(row[9]),  # Decrypt email
                'keep_logged_in': bool(row[10])
            }
        except ValueError as e:
            print(f"Error loading user data: {e}")
            raise e
    return {}

# Function to clear user session data
def clear_user_session_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE user_data SET keep_logged_in = 0 WHERE id = 1')
    conn.commit()
    conn.close()
