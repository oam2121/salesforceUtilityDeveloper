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


USER_DATA_FILE = 'user_data.json'
# Function to save user data persistently to a JSON file
def save_user_data(user_data, keep_logged_in=False):
    user_data['keep_logged_in'] = keep_logged_in
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(user_data, f)
# Function to load user data from the JSON file
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            return json.load(f)
    return {}
# Function to clear saved user data (used on logout)
def clear_user_data():
    if os.path.exists(USER_DATA_FILE):
        os.remove(USER_DATA_FILE)
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
            user_data = {
                'username': username,
                'password': password,
                'security_token': security_token,
                'client_id': client_id,
                'client_secret': client_secret,
                'domain': domain,
                'pin': pin
            }
            save_user_data(user_data)
            st.success("Registration successful! Please login.")
            st.session_state['is_authenticated'] = False
        else:
            st.error("PIN must be 6 digits.")
# Login page
def login():
    st.title("Login")
    user_data = load_user_data()
    if not user_data:
        st.error("No registered user found. Please register first.")
        return
    username = st.text_input("Username", value=user_data.get('username', ''))
    password = st.text_input("Password", type="password", value=user_data.get('password', ''))
    pin = st.text_input("Enter your 6-digit PIN", type="password", max_chars=6)
    # Add a toggle to keep the user logged in
    keep_logged_in = st.checkbox("Keep me logged in", value=user_data.get('keep_logged_in', False))
    if st.button("Login"):
        if username == user_data.get('username') and password == user_data.get('password') and pin == user_data.get('pin'):
            st.session_state['is_authenticated'] = True
            st.session_state['keep_logged_in'] = keep_logged_in  # Store the toggle state
            # Authenticate Salesforce instance and store it in session state
            st.session_state['salesforce'] = authenticate_salesforce_with_user(user_data)
            
            # Save user data with the "Keep me logged in" option
            save_user_data(user_data, keep_logged_in=keep_logged_in)
            st.success("Login successful!")
            st.rerun()  # Rerun to refresh state
        else:
            st.error("Invalid credentials or PIN.")
            st.error('Please Try Again')
# Logout function
def logout():
    st.session_state['is_authenticated'] = False
    st.session_state['salesforce'] = None
    st.session_state['keep_logged_in'] = False
    clear_user_data()
    st.rerun()
# Check if user session should persist after refresh
def check_session():
    user_data = load_user_data()
    if user_data and user_data.get('keep_logged_in'):
        st.session_state['is_authenticated'] = True
        st.session_state['salesforce'] = authenticate_salesforce_with_user(user_data)
        return True
    return False

# Main function
def main():
    if 'is_authenticated' not in st.session_state:
        st.session_state['is_authenticated'] = False
    # Check for persistent session on page load
    if not st.session_state['is_authenticated'] and check_session():
        st.session_state['is_authenticated'] = True
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        if st.session_state['is_authenticated']:
            # Main Menu for logged-in users
            selected_section = option_menu(
                "Sections",
                ["General", "Salesforce Tools", "SOQL Builder", "Visualizations", "Admin Tools", "Help & Settings"],
                icons=["grid", "briefcase", "fan", "bar-chart-line", "wrench", "gear"],
                menu_icon="menu-app", default_index=0
            )
            # Nested menu based on the selected section
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
                    ["SOQL Builder Child to Parent","SOQL BUILDER Parent to Child"],
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
                
            # Logout button
            if st.button("Logout", on_click=logout):
                st.session_state['is_authenticated'] = False
        else:
            # Menu for non-authenticated users
            selected_module = option_menu(
                "Authentication Menu", 
                ["Login", "Register", "How to Use"],
                icons=["box-arrow-in-right", "person-plus", "info-circle"],
                menu_icon="lock", default_index=0
            )
    # Display corresponding content based on the selected option
    if st.session_state['is_authenticated']:
        # If the user is authenticated, load the selected module
        sf = st.session_state.get('salesforce')
        modules_with_sf = {
            'Home': display_home,  
            'Query Builder': show_query_builder,
            'Describe Object': show_describe_object,
            'Search Salesforce': show_search_salesforce,
            'API Tools': show_api_tools,
            'Record Hierarchy': hierarchy_viewer,
            'Data Visualizations': visualize_data,
            'Smart Visualize': smart_visualize,  # Background Dash App for Smart Visualize
            'Data Import/Export': show_data_import_export,
            'Scheduled Jobs Viewer': view_scheduled_jobs,
            'Audit Logs Viewer': view_audit_logs,
            'SOQL Builder Child to Parent':show_soql_query_builder,
            'Global Actions':show_global_actions,
            'SOQL BUILDER Parent to Child':show_advanced_soql_query_builder,
            'User, Profile, Roles Info':display_user_info
        }
        modules_without_sf = {
            'How to Use': show_how_to_use
        }
        # Run the selected module with or without `sf` depending on the function requirements
        if selected_module in modules_with_sf:
            modules_with_sf[selected_module](sf)  # Requires Salesforce connection
        elif selected_module in modules_without_sf:
            modules_without_sf[selected_module]()  # Does not require Salesforce connection
    else:
        # If the user is not authenticated, show either login, register form, or the "How to Use" page
        if selected_module == "Login":
            login()
        elif selected_module == "Register":
            register()
        elif selected_module == "How to Use":
            show_how_to_use()
if __name__ == "__main__":
    main()