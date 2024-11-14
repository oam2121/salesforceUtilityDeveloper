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


# Initialize the database
init_db()

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
            st.session_state['salesforce'] = authenticate_salesforce_with_user(st.session_state['user_data'])
            st.success("Login successful!")
            st.experimental_rerun()  # Refresh state
        else:
            st.error("Invalid username, password, or PIN.")

# Logout function
def logout():
    st.session_state['is_authenticated'] = False
    st.session_state['user_data'] = None
    st.session_state['salesforce'] = None
    st.experimental_rerun()

# Main function
def main():
    # Initialize session state
    if 'is_authenticated' not in st.session_state:
        st.session_state['is_authenticated'] = False

    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")
        if st.session_state['is_authenticated']:
            # Main menu for logged-in users
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

    # Display content based on the selected option
    if st.session_state['is_authenticated']:
        # Modules requiring authentication
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
            'Global Actions': show_global_actions,
            'SOQL BUILDER Parent to Child': show_advanced_soql_query_builder,
            'User, Profile, Roles Info': display_user_info
        }
        modules_without_sf = {
            'How to Use': show_how_to_use
        }

        if selected_module in modules_with_sf:
            modules_with_sf[selected_module](st.session_state['salesforce'])
        elif selected_module in modules_without_sf:
            modules_without_sf[selected_module]()
    else:
        # Non-authenticated pages
        if selected_module == "Login":
            login()
        elif selected_module == "Register":
            register()
        elif selected_module == "How to Use":
            show_how_to_use()

if __name__ == "__main__":
    main()