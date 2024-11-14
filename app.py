import streamlit as st
import threading
import json
import os
from streamlit_option_menu import option_menu
from smart_visualize import smart_visualize
from how_to_use import show_how_to_use  # Import the how to use page
from authentication import authenticate_salesforce_with_user
# Importing other module functions
from query_builder import show_query_builder
from data_import_export import show_data_import_export
from describe_object import show_describe_object
from search_salesforce import show_search_salesforce
from data_visualizations import visualize_data
from scheduled_jobs import view_scheduled_jobs
from audit_logs import view_audit_logs
from home import display_home
from api_monitor import show_api_tools  # Importing the API Tools functionality
from record_hier import hierarchy_viewer
from basic_info import display_user_info
from soql_query_builder import show_soql_query_builder
from soql_query_builder_p_c import show_advanced_soql_query_builder
from global_actions import show_global_actions

from db_manager import init_db, register_user, verify_user, get_user_data
from authentication import authenticate_salesforce_with_user
import uuid  # For generating session IDs
from streamlit_cookies_manager import EncryptedCookieManager
from dotenv import load_dotenv


# Initialize database
init_db()

password = st.secrets.get("COOKIE_PASSWORD")
if not password:
    st.error("COOKIE_PASSWORD is not set in Streamlit Secrets!")
    st.stop()
# Initialize the cookie manager with the password
cookies = EncryptedCookieManager(
    prefix="salesforce_app_",  # Prefix for cookie names
    password=st.secrets.get("COOKIE_PASSWORD")  # Retrieve the secret
)

if not cookies.ready():
    st.stop()  # Ensure the cookie password is set

# Function to initialize session state
def initialize_session():
    if 'is_authenticated' not in st.session_state:
        st.session_state['is_authenticated'] = False
    if 'user_data' not in st.session_state:
        st.session_state['user_data'] = None
    if 'salesforce' not in st.session_state:
        st.session_state['salesforce'] = None

    # Restore authentication from cookies
    if cookies.get("is_authenticated") == "true":
        st.session_state['is_authenticated'] = True
        st.session_state['user_data'] = cookies.get("user_data")
        if st.session_state['user_data']:
            st.session_state['user_data'] = eval(st.session_state['user_data'])

# Registration page
def register():
    st.title("Register")
    username = st.text_input("Salesforce Username")
    password = st.text_input("Salesforce Password", type="password")
    security_token = st.text_input("Salesforce Security Token", type="password")
    client_id = st.text_input("Salesforce Client ID")
    client_secret = st.text_input("Salesforce Client Secret", type="password")
    domain = st.selectbox("Salesforce Domain", ["login", "test"])
    pin = st.text_input("Set a 6-digit PIN", type="password", max_chars=6)

    if st.button("Register"):
        if len(pin) == 6 and pin.isdigit():
            if register_user(username, password, security_token, client_id, client_secret, domain, pin):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists. Please choose another username.")
        else:
            st.error("PIN must be 6 digits.")

# Login page
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    pin = st.text_input("Enter your 6-digit PIN", type="password", max_chars=6)

    if st.button("Login"):
        if verify_user(username, password, pin):
            st.session_state['is_authenticated'] = True
            st.session_state['user_data'] = get_user_data(username)
            st.session_state['user_data']['password'] = password  # Add password for Salesforce authentication

            try:
                st.session_state['salesforce'] = authenticate_salesforce_with_user(st.session_state['user_data'])

                # Store authentication in cookies
                cookies["is_authenticated"] = "true"
                cookies["user_data"] = str(st.session_state['user_data'])
                cookies.save()

                st.success("Login successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Salesforce authentication failed: {e}")
                st.session_state['is_authenticated'] = False
        else:
            st.error("Invalid username, password, or PIN.")

# Logout function
def logout():
    st.session_state['is_authenticated'] = False
    st.session_state['user_data'] = None
    st.session_state['salesforce'] = None

    # Clear cookies
    cookies["is_authenticated"] = "false"
    cookies["user_data"] = ""
    cookies.save()

    st.rerun()

# Main function
def main():
    initialize_session()  # Ensure session state is initialized

    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")

        if st.session_state['is_authenticated']:
            # Authenticated User Menu
            selected_section = option_menu(
                "Sections",
                ["General", "Salesforce Tools", "SOQL Builder", "Visualizations", "Admin Tools", "Help & Settings"],
                icons=["grid", "briefcase", "fan", "bar-chart-line", "wrench", "gear"],
                menu_icon="menu-app", default_index=0
            )

            # Nested Menu Based on Selected Section
            if selected_section == "General":
                selected_module = option_menu(
                    "General",
                    ["Home", "User, Profile, Roles Info", "Global Actions", "How to Use"],
                    icons=["house", "person", "app-indicator", "info-circle"],
                    menu_icon="list", default_index=0
                )
            elif selected_section == "Salesforce Tools":
                selected_module = option_menu(
                    "Salesforce Tools",
                    ["Query Builder", "Describe Object", "Search Salesforce", "API Tools", "Record Hierarchy"],
                    icons=["wrench", "book", "search", "gear", "tree"],
                    menu_icon="cloud", default_index=0
                )
            elif selected_section == "SOQL Builder":
                selected_module = option_menu(
                    "SOQL Builder",
                    ["SOQL Builder Child to Parent", "SOQL BUILDER Parent to Child"],
                    icons=["hurricane", "cpu"],
                    menu_icon="cloud", default_index=0
                )
            elif selected_section == "Visualizations":
                selected_module = option_menu(
                    "Visualizations",
                    ["Data Visualizations", "Smart Visualize"],
                    icons=["bar-chart"],
                    menu_icon="bar-chart", default_index=0
                )
            elif selected_section == "Admin Tools":
                selected_module = option_menu(
                    "Admin Tools",
                    ["Data Import/Export", "Scheduled Jobs Viewer", "Audit Logs Viewer"],
                    icons=["upload", "clock", "book"],
                    menu_icon="tools", default_index=0
                )
            elif selected_section == "Help & Settings":
                selected_module = option_menu(
                    "Help & Settings",
                    ["How to Use", "Logout"],
                    icons=["info-circle", "box-arrow-right"],
                    menu_icon="question-circle", default_index=0
                )

                # If Logout is selected, trigger logout functionality
                if selected_module == "Logout":
                    logout()

        else:
            # Non-Authenticated User Menu
            selected_module = option_menu(
                "Authentication Menu",
                ["Login", "Register", "How to Use"],
                icons=["box-arrow-in-right", "person-plus", "info-circle"],
                menu_icon="lock", default_index=0
            )

            # Handle Menu Options
            if selected_module == "Login":
                login()
            elif selected_module == "Register":
                register()
            elif selected_module == "How to Use":
                show_how_to_use()

    # Main Content Display Based on Authentication State
    if st.session_state['is_authenticated']:
        # Handle Modules for Authenticated Users
        modules_with_sf = {
            'Home': display_home,
            'Query Builder': show_query_builder,
            'Describe Object': show_describe_object,
            'Search Salesforce': show_search_salesforce,
            'API Tools': show_api_tools,
            'Record Hierarchy': hierarchy_viewer,
            'Data Visualizations': visualize_data,
            'Smart Visualize': smart_visualize,
            'Data Import/Export': show_data_import_export,
            'Scheduled Jobs Viewer': view_scheduled_jobs,
            'Audit Logs Viewer': view_audit_logs,
            'SOQL Builder Child to Parent': show_soql_query_builder,
            'SOQL BUILDER Parent to Child': show_advanced_soql_query_builder,
            'User, Profile, Roles Info': display_user_info
        }
        modules_without_sf = {
            'How to Use': show_how_to_use
        }

        # Check and Display Module Content
        if selected_module in modules_with_sf:
            try:
                modules_with_sf[selected_module](st.session_state['salesforce'])
            except KeyError as e:
                st.error(f"Error loading Salesforce data: {e}")
                logout()
        elif selected_module in modules_without_sf:
            modules_without_sf[selected_module]()
    else:
        # Non-Authenticated Content
        st.write("Please log in to continue.")