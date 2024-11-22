import sqlite3
from passlib.hash import bcrypt
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from random import randint
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

DB_FILE = "app_database.db"

def init_db():
    """ Initialize the database and create tables if they don't exist. """
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
            pin TEXT NOT NULL,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def send_otp_email(email, otp):
    """ Send an OTP to the user's email using SendGrid. """
    message = MIMEMultipart()
    message['From'] = 'oamshah2121@gmail.com'
    message['To'] = email
    message['Subject'] = 'Your OTP for Registration'
    body = f'Hello, your OTP for registration is: {otp}'
    message.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.sendgrid.net', 587)
    server.starttls()
    server.login('apikey', os.getenv('SENDGRID_API_KEY'))
    server.sendmail('oamshah2121@gmail.com', email, message.as_string())
    server.quit()

def register_user(username, password, security_token, client_id, client_secret, domain, pin, name, email):
    """ Register a new user with the details provided, including sending an OTP. """
    password_hash = bcrypt.hash(password)
    otp = randint(100000, 999999)  # Generate a 6-digit OTP
    send_otp_email(email, otp)
    return otp, password_hash  # Return OTP and hashed password for further processing outside this function.

def save_user(username, password_hash, security_token, client_id, client_secret, domain, pin, name, email):
    """ Save the user to the database after OTP verification. """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO users (username, password_hash, security_token, client_id, client_secret, domain, pin, name, email)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (username, password_hash, security_token, client_id, client_secret, domain, pin, name, email))
        conn.commit()
    finally:
        conn.close()

def verify_user(username, password, pin):
    """ Verify user credentials. """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, pin FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    if result:
        password_hash, stored_pin = result
        return bcrypt.verify(password, password_hash) and pin == stored_pin
    return False

def get_user_data(username):
    """ Fetch user data by username. """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT username, security_token, client_id, client_secret, domain, pin, name, email
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
            "email": user_data[7]
        }
    return None
