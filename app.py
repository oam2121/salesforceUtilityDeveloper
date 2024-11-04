import streamlit as st
import random
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from db_utils import initialize_database, save_user_data, load_user_data, clear_user_session_data
from db_utils import encrypt_data, get_db_connection
from authentication import authenticate_salesforce_with_user
from email_template import generate_email_template
from streamlit_option_menu import option_menu

# Import other modules
from smart_visualize import smart_visualize
from how_to_use import show_how_to_use
from query_builder import show_query_builder
from data_import_export import show_data_import_export
from describe_object import show_describe_object
from search_salesforce import show_search_salesforce
from data_visualizations import visualize_data
from scheduled_jobs import view_scheduled_jobs
from audit_logs import view_audit_logs
from home import display_home
from api_monitor import show_api_tools
from record_hier import hierarchy_viewer
from basic_info import display_user_info
from soql_query_builder import show_soql_query_builder
from soql_query_builder_p_c import show_advanced_soql_query_builder
from global_actions import show_global_actions
import uuid

# Load environment variables
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

# Initialize the database
initialize_database()

# Helper function to generate a unique session ID
def generate_session_id():
    return str(uuid.uuid4())

# Helper function to send OTP using SendGrid
def send_otp(email):
    otp = random.randint(100000, 999999)
    st.session_state['otp'] = otp

    message_content = generate_email_template(otp)
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = email
    message["Subject"] = "Your OTP for Registration"
    message.attach(MIMEText(message_content, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login("apikey", SENDGRID_API_KEY)
            server.send_message(message)
        st.success("OTP sent to your email.")
    except Exception as e:
        st.error(f"Failed to send OTP: {e}")

# Registration Screen 1
def register_screen_1():
    st.title("Register - Step 1")
    name = st.text_input("Full Name", placeholder="Enter your full name")
    email = st.text_input("Email", placeholder="Enter your email address")

    if st.button("Send OTP"):
        send_otp(email)

    otp_input = st.text_input("Enter OTP", type="password", max_chars=6)
    if 'otp' in st.session_state and otp_input:
        if otp_input == str(st.session_state['otp']):
            st.success("OTP verified successfully!")
            st.session_state['name'] = name
            st.session_state['email'] = email
            st.session_state['otp_verified'] = True
            st.rerun()
        else:
            st.error("Invalid OTP. Please try again.")

def register_screen_2():
    st.title("Register - Step 2")
    username = st.text_input("Salesforce Username")
    password = st.text_input("Salesforce Password", type="password")
    security_token = st.text_input("Salesforce Security Token", type="password")
    client_id = st.text_input("Salesforce Client ID")
    client_secret = st.text_input("Salesforce Client Secret", type="password")
    domain = st.selectbox("Salesforce Domain", ["login", "test"])
    pin = st.text_input("Set a 6-digit PIN", type="password", max_chars=6)

    if st.button("Register"):
        if st.session_state.get('otp_verified') and len(pin) == 6 and pin.isdigit():
            user_data = {
                'name': st.session_state['name'],
                'email': st.session_state['email'],
                'username': username,
                'password': password,
                'security_token': security_token,
                'client_id': client_id,
                'client_secret': client_secret,
                'domain': domain,
                'pin': pin
            }
            save_user_data(user_data)

            st.session_state['session_id'] = generate_session_id()
            st.session_state['is_authenticated'] = False
            st.session_state['user_name'] = user_data['name']
            st.session_state['email'] = user_data['email']
            st.success("Registration successful! Please login.")
        else:
            st.error("Please complete the OTP verification and ensure the PIN is 6 digits.")

def login():
    st.title("Login")
    user_data = load_user_data()
    
    if not user_data:
        st.error("No registered user found. Please register first.")
        return

    username = st.text_input("Username", value="")
    password = st.text_input("Password", type="password")
    pin = st.text_input("Enter your 6-digit PIN", type="password", max_chars=6)
    keep_logged_in = st.checkbox("Keep me logged in")

    if st.button("Login"):
        if username == user_data.get('username') and password == user_data.get('password') and pin == user_data.get('pin'):
            st.session_state['session_id'] = generate_session_id()
            st.session_state['is_authenticated'] = True
            st.session_state['keep_logged_in'] = keep_logged_in
            st.session_state['salesforce'] = authenticate_salesforce_with_user(user_data)
            st.session_state['user_name'] = user_data['name']
            st.session_state['email'] = user_data['email']
            save_user_data(user_data, keep_logged_in=keep_logged_in)
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials or PIN.")

# Logout function
def logout():
    keys_to_clear = ['is_authenticated', 'salesforce', 'keep_logged_in', 'user_name', 'email', 'session_id']
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    clear_user_session_data()
    st.rerun()

# Check session persistence
def check_session():
    if 'session_id' in st.session_state and st.session_state['session_id']:
        return True
    return False

# Main function
def main():
    if 'session_id' not in st.session_state:
        st.session_state['session_id'] = None

    if 'is_authenticated' not in st.session_state:
        st.session_state['is_authenticated'] = False

    if not st.session_state['is_authenticated'] and check_session():
        st.session_state['is_authenticated'] = True

    with st.sidebar:
        st.title("Navigation")
        if st.session_state['is_authenticated']:
            user_name = st.session_state.get('user_name', 'User')
            st.sidebar.write(f"Hello, {user_name}!")
            if st.sidebar.button("Logout"):
                logout()

            selected_section = option_menu(
                "Sections", 
                ["General", "Salesforce Tools", "SOQL Builder", "Visualizations", "Admin Tools", "Help & Settings"],
                icons=["grid", "briefcase", "fan", "bar-chart-line", "wrench", "gear"],
                menu_icon="menu-app", default_index=0
            )

    if st.session_state['is_authenticated']:
        sf = st.session_state.get('salesforce')
        st.title("Salesforce Developer Utility")


        # Display content in the main area
        if selected_section == "General":
            selected_module = option_menu(
                "General", 
                ["Home", "User, Profile, Roles Info", "Global Actions", "How to Use"],
                icons=["house", "person", "app-indicator", "info-circle"],
                menu_icon="list", default_index=0, orientation="horizontal"
            )
            if selected_module == "Home":
                display_home(sf)
            elif selected_module == "User, Profile, Roles Info":
                display_user_info(sf)
            elif selected_module == "Global Actions":
                show_global_actions(sf)
            elif selected_module == "How to Use":
                show_how_to_use()

        elif selected_section == "Salesforce Tools":
            selected_module = option_menu(
                "Salesforce Tools", 
                ["Query Builder", "Describe Object", "Search Salesforce", "API Tools", "Record Hierarchy"],
                icons=["wrench", "book", "search", "gear", "bezier"],
                menu_icon="cloud", default_index=0, orientation="horizontal"
            )
            if selected_module == "Query Builder":
                show_query_builder(sf)
            elif selected_module == "Describe Object":
                show_describe_object(sf)
            elif selected_module == "Search Salesforce":
                show_search_salesforce(sf)
            elif selected_module == "API Tools":
                show_api_tools(sf)
            elif selected_module == "Record Hierarchy":
                hierarchy_viewer(sf)

        elif selected_section == "SOQL Builder":
            selected_module = option_menu(
                "SOQL Builder", 
                ["SOQL Query Runner", "SOQL BUILDER Parent to Child"],
                icons=["hurricane", "cpu"],
                menu_icon="cloud", default_index=0, orientation="horizontal"
            )
            if selected_module == "SOQL Query Runner":
                show_soql_query_builder(sf)
            elif selected_module == "SOQL BUILDER Parent to Child":
                show_advanced_soql_query_builder(sf)

        elif selected_section == "Visualizations":
            selected_module = option_menu(
                "Visualizations", 
                ["Data Visualizations", "Smart Visualize"],
                icons=["bar-chart", "tv"],
                menu_icon="bar-chart", default_index=0, orientation="horizontal"
            )
            if selected_module == "Data Visualizations":
                visualize_data(sf)
            elif selected_module == "Smart Visualize":
                smart_visualize(sf)

        elif selected_section == "Admin Tools":
            selected_module = option_menu(
                "Admin Tools", 
                ["Data Import/Export", "Scheduled Jobs Viewer", "Audit Logs Viewer"],
                icons=["upload", "clock", "book"],
                menu_icon="tools", default_index=0, orientation="horizontal"
            )
            if selected_module == "Data Import/Export":
                show_data_import_export(sf)
            elif selected_module == "Scheduled Jobs Viewer":
                view_scheduled_jobs(sf)
            elif selected_module == "Audit Logs Viewer":
                view_audit_logs(sf)

        elif selected_section == "Help & Settings":
            selected_module = option_menu(
                "Help & Settings", 
                ["How to Use", "Logout"],
                icons=["info-circle", "box-arrow-right"],
                menu_icon="question-circle", default_index=0, orientation="horizontal"
            )
            if selected_module == "How to Use":
                show_how_to_use()
            elif selected_module == "Logout":
                logout()

    else:
        selected_module = option_menu(
            "Authentication Menu", 
            ["Login", "Register - Step 1", "How to Use"],
            icons=["box-arrow-in-right", "person-plus", "info-circle"],
            menu_icon="lock", default_index=0
        )
        if selected_module == "Login":
            login()
        elif selected_module == "Register - Step 1":
            if st.session_state.get('otp_verified'):
                register_screen_2()
            else:
                register_screen_1()
        elif selected_module == "How to Use":
            show_how_to_use()

# Main entry point
if __name__ == "__main__":
    main()