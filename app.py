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
import uuid

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
from streamlit_cookies_controller import CookieController  # Correct import for CookieController

# Load environment variables
load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))

# Initialize the database
initialize_database()

# Initialize the CookieController
cookies = CookieController()

# Helper function to generate a unique session ID
def generate_session_id():
    return str(uuid.uuid4())

# Helper function to send OTP using SendGrid
def send_otp(email):
    otp = random.randint(100000, 999999)
    st.session_state['otp'] = otp
    message_content = "Your OTP is: {}".format(otp)
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = email
    message["Subject"] = "Your OTP for Registration"
    message.attach(MIMEText(message_content, "html"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDGRID_API_KEY)
            server.send_message(message)
        st.success("OTP sent to your email.")
    except Exception as e:
        st.error("Failed to send OTP: {}".format(e))

# Save session to cookies
def save_session_to_cookies():
    cookies.set('session_id', st.session_state.get('session_id', ''))
    cookies.set('is_authenticated', st.session_state.get('is_authenticated', False))
    cookies.set('user_name', st.session_state.get('user_name', ''))
    cookies.set('email', st.session_state.get('email', ''))

# Load session from cookies
def load_session_from_cookies():
    st.session_state['session_id'] = cookies.get('session_id', None)
    st.session_state['is_authenticated'] = cookies.get('is_authenticated', False)
    st.session_state['user_name'] = cookies.get('user_name', '')
    st.session_state['email'] = cookies.get('email', '')

# Registration Screen 1
def register_screen_1():
    st.title("Register - Step 1")
    name = st.text_input("Full Name")
    email = st.text_input("Email")

    if st.button("Send OTP"):
        send_otp(email)

    otp_input = st.text_input("Enter OTP", type="password")
    if 'otp' in st.session_state and otp_input:
        if otp_input == str(st.session_state['otp']):
            st.session_state['name'] = name
            st.session_state['email'] = email
            st.session_state['otp_verified'] = True
            register_screen_2()
        else:
            st.error("Invalid OTP.")

# Registration Screen 2
def register_screen_2():
    st.title("Register - Step 2")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Register"):
        user_data = {
            'username': username,
            'password': password,
            'name': st.session_state['name'],
            'email': st.session_state['email']
        }
        save_user_data(user_data)
        st.session_state['session_id'] = generate_session_id()
        st.session_state['is_authenticated'] = True
        st.session_state['user_name'] = user_data['name']
        save_session_to_cookies()
        st.success("Registration successful!")

# Login function
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user_data = load_user_data(username)
        if user_data and user_data['password'] == password:
            st.session_state['session_id'] = generate_session_id()
            st.session_state['is_authenticated'] = True
            st.session_state['user_name'] = user_data['name']
            save_session_to_cookies()
            st.success("Login successful!")

# Logout function
def logout():
    cookies.delete('session_id')
    cookies.delete('is_authenticated')
    cookies.delete('user_name')
    cookies.delete('email')
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.info("Logged out successfully.")

# Main function
def main():
    # Load session data from cookies if available
    load_session_from_cookies()

    # Initialize session state variables if not already set
    if 'is_authenticated' not in st.session_state:
        st.session_state['is_authenticated'] = False

    # Sidebar navigation setup
    with st.sidebar:
        st.title("Navigation")

        # If the user is authenticated, display the main navigation
        if st.session_state.get('is_authenticated'):
            # Display a welcome message with the user's name
            user_name = st.session_state.get('user_name', 'User')
            st.sidebar.write(f"Hello, {user_name}!")

            # Logout button
            if st.sidebar.button("Logout"):
                logout()

            # Main sections menu
            selected_section = option_menu(
                "Sections",
                ["General", "Salesforce Tools", "SOQL Builder", "Visualizations", "Admin Tools", "Help & Settings"],
                icons=["grid", "briefcase", "fan", "bar-chart-line", "wrench", "gear"],
                menu_icon="menu-app", default_index=0
            )

            # Handle each section's content
            if selected_section == "General":
                selected_module = option_menu(
                    "General",
                    ["Home", "User, Profile, Roles Info", "Global Actions", "How to Use"],
                    icons=["house", "person", "app-indicator", "info-circle"],
                    menu_icon="list", default_index=0, orientation="horizontal"
                )
                if selected_module == "Home":
                    display_home(st.session_state['salesforce'])
                elif selected_module == "User, Profile, Roles Info":
                    display_user_info(st.session_state['salesforce'])
                elif selected_module == "Global Actions":
                    show_global_actions(st.session_state['salesforce'])
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
                    show_query_builder(st.session_state['salesforce'])
                elif selected_module == "Describe Object":
                    show_describe_object(st.session_state['salesforce'])
                elif selected_module == "Search Salesforce":
                    show_search_salesforce(st.session_state['salesforce'])
                elif selected_module == "API Tools":
                    show_api_tools(st.session_state['salesforce'])
                elif selected_module == "Record Hierarchy":
                    hierarchy_viewer(st.session_state['salesforce'])

            elif selected_section == "SOQL Builder":
                selected_module = option_menu(
                    "SOQL Builder",
                    ["SOQL Query Runner", "SOQL BUILDER Parent to Child"],
                    icons=["hurricane", "cpu"],
                    menu_icon="cloud", default_index=0, orientation="horizontal"
                )
                if selected_module == "SOQL Query Runner":
                    show_soql_query_builder(st.session_state['salesforce'])
                elif selected_module == "SOQL BUILDER Parent to Child":
                    show_advanced_soql_query_builder(st.session_state['salesforce'])

            elif selected_section == "Visualizations":
                selected_module = option_menu(
                    "Visualizations",
                    ["Data Visualizations", "Smart Visualize"],
                    icons=["bar-chart", "tv"],
                    menu_icon="bar-chart", default_index=0, orientation="horizontal"
                )
                if selected_module == "Data Visualizations":
                    visualize_data(st.session_state['salesforce'])
                elif selected_module == "Smart Visualize":
                    smart_visualize(st.session_state['salesforce'])

            elif selected_section == "Admin Tools":
                selected_module = option_menu(
                    "Admin Tools",
                    ["Data Import/Export", "Scheduled Jobs Viewer", "Audit Logs Viewer"],
                    icons=["upload", "clock", "book"],
                    menu_icon="tools", default_index=0, orientation="horizontal"
                )
                if selected_module == "Data Import/Export":
                    show_data_import_export(st.session_state['salesforce'])
                elif selected_module == "Scheduled Jobs Viewer":
                    view_scheduled_jobs(st.session_state['salesforce'])
                elif selected_module == "Audit Logs Viewer":
                    view_audit_logs(st.session_state['salesforce'])

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
            # Menu for non-authenticated users
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