
import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager
from datetime import datetime, timedelta

# Importing required modules
from db_manager import init_db, register_user, verify_user, get_user_data, get_user_orgs
from authentication import authenticate_salesforce_with_user
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
from datetime import datetime, timedelta

# Initialize the database
init_db()

# Hardcoded password for cookie manager
PASSWORD = "TemporarySecurePassword123!"  # Replace with a secure password in production

# Initialize cookie manager
cookies = EncryptedCookieManager(prefix="salesforce_app_", password=PASSWORD)
if not cookies.ready():
    st.stop()

# Define session timeout (30 minutes)
SESSION_TIMEOUT = timedelta(minutes=30)

# Initialize session state and restore connection
def initialize_session():
    if "is_authenticated" not in st.session_state:
        st.session_state["is_authenticated"] = False
    if "user_data" not in st.session_state:
        st.session_state["user_data"] = None
    if "salesforce" not in st.session_state:
        st.session_state["salesforce"] = None
    if "last_activity" not in st.session_state:
        st.session_state["last_activity"] = datetime.now()

    # Restore authentication from cookies
    if cookies.get("is_authenticated") == "true":
        st.session_state["is_authenticated"] = True
        user_data = cookies.get("user_data")
        if user_data:
            st.session_state["user_data"] = eval(user_data)

        # Re-establish Salesforce connection if it doesn't exist
        if st.session_state["salesforce"] is None and st.session_state["user_data"]:
            try:
                st.session_state["salesforce"] = authenticate_salesforce_with_user(st.session_state["user_data"])
            except Exception as e:
                st.error(f"Failed to reconnect with Salesforce: {e}")
                st.session_state["is_authenticated"] = False

    # Check for session timeout
    if st.session_state["is_authenticated"]:
        current_time = datetime.now()
        if current_time - st.session_state["last_activity"] > SESSION_TIMEOUT:
            st.warning("Session timed out due to inactivity. Please login again.")
            logout()
        else:
            # Update last activity timestamp
            st.session_state["last_activity"] = current_time

# Registration Page
def register():
    st.title("Register")
    username = st.text_input("Salesforce Username")
    password = st.text_input("Salesforce Password", type="password")
    security_token = st.text_input("Salesforce Security Token", type="password")
    client_id = st.text_input("Salesforce Client ID")
    client_secret = st.text_input("Salesforce Client Secret", type="password")
    domain = st.selectbox("Salesforce Domain", ["login", "test"])
    pin = st.text_input("Set a 6-digit PIN", type="password", max_chars=6)
    name = st.text_input("Name")
    email = st.text_input("Email")

    if st.button("Register"):
        if len(pin) == 6 and pin.isdigit():
            if register_user(username, password, security_token, client_id, client_secret, domain, pin, name, email):
                st.success("Registration successful! Please login.")
            else:
                st.error("Username already exists. Please try another username.")
        else:
            st.error("PIN must be exactly 6 digits.")

# Login Page
def login():
    st.title("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    pin = st.text_input("Enter your 6-digit PIN", type="password", max_chars=6)

    if st.button("Login"):
        if verify_user(username, password, pin):
            st.session_state["is_authenticated"] = True
            st.session_state["user_data"] = get_user_data(username)
            st.session_state["user_data"]["password"] = password  # Add password for Salesforce authentication

            try:
                st.session_state["salesforce"] = authenticate_salesforce_with_user(st.session_state["user_data"])

                # Store session in cookies
                cookies["is_authenticated"] = "true"
                cookies["user_data"] = str(st.session_state["user_data"])
                cookies.save()

                st.success("Login successful!")
                st.rerun()
            except Exception as e:
                st.error(f"Salesforce authentication failed: {e}")
                st.session_state["is_authenticated"] = False
        else:
            st.error("Invalid username, password, or PIN.")
            
def my_orgs():
    st.title("My Orgs")
    user_data = st.session_state.get("user_data")
    if user_data:
        orgs = get_user_orgs(user_data["email"])
        for org in orgs:
            if st.button(f"Login to {org[0]} @ {org[1]}"):
                if st.session_state.get("salesforce")["username"] != org[0]:
                    st.session_state["salesforce"] = None  # Clear current session
                    st.warning("You will be logged out from this org.")
                    st.session_state["user_data"] = get_user_data(org[0])
                    st.session_state["user_data"]["password"] = ""  # Clear password for security
                    login()  # Call login function to re-authenticate


# Logout Function
def logout():
    st.session_state["is_authenticated"] = False
    st.session_state["user_data"] = None
    st.session_state["salesforce"] = None

    # Clear cookies
    cookies["is_authenticated"] = "false"
    cookies["user_data"] = ""
    cookies.save()

    st.rerun()

# Main Function
def main():
    # Sidebar Navigation
    with st.sidebar:
        if st.session_state["is_authenticated"]:
            # Update activity timestamp whenever user interacts
            st.session_state["last_activity"] = datetime.now()

            # Display username and options in a dropdown menu
            user_action = option_menu(
                "User",
                [f"Logged in as: {st.session_state['user_data'].get('username', 'Unknown User')}", "Logout", "My Orgs"],
                icons=["person", "box-arrow-right", "building"],
                menu_icon="person-circle",
                default_index=0,
            )

            # Handle user actions
            if user_action == "Logout":
                logout()
            elif user_action == "My Orgs":
                my_orgs(st.session_state["salesforce"])

            # Show options for authenticated users
            selected_section = option_menu(
                "Sections",
                ["Salesforce Tools", "SOQL Builder", "Visualizations", "Admin Tools", "Help & Settings"],
                icons=["briefcase", "fan", "bar-chart-line", "wrench", "gear"],
                menu_icon="menu-app",
                default_index=0,
            )

        else:
            # Show login/register for non-authenticated users
            selected_section = option_menu(
                "Authentication Menu",
                ["Login", "Register", "How to Use"],
                icons=["box-arrow-in-right", "person-plus", "info-circle"],
                menu_icon="lock",
                default_index=0,
            )

    # Main Content Area
    if st.session_state["is_authenticated"]:
        # Handle authenticated user modules based on selected section
        if selected_section == "Salesforce Tools":
            selected_tool = option_menu(
                "Salesforce Tools",
                ["Home", "Query Builder", "Describe Object", "Search Salesforce", "API Tools", "Record Hierarchy", "Global Actions"],
                icons=["house", "wrench", "book", "search", "gear", "diagram-3", "rocket"],
                menu_icon="cloud",
                default_index=0,
            )

            if selected_tool == "Home":
                display_home(st.session_state["salesforce"])
            elif selected_tool == "Query Builder":
                show_query_builder(st.session_state["salesforce"])
            elif selected_tool == "Describe Object":
                show_describe_object(st.session_state["salesforce"])
            elif selected_tool == "Search Salesforce":
                show_search_salesforce(st.session_state["salesforce"])
            elif selected_tool == "API Tools":
                show_api_tools(st.session_state["salesforce"])
            elif selected_tool == "Record Hierarchy":
                hierarchy_viewer(st.session_state["salesforce"])
            elif selected_tool == "Global Actions":
                show_global_actions(st.session_state["salesforce"])

        elif selected_section == "SOQL Builder":
            selected_builder = option_menu(
                "SOQL Builder",
                ["SOQL Builder Child to Parent", "SOQL Builder Parent to Child"],
                icons=["hurricane", "cpu"],
                menu_icon="cloud",
                default_index=0,
            )
            if selected_builder == "SOQL Builder Child to Parent":
                show_soql_query_builder(st.session_state["salesforce"])
            elif selected_builder == "SOQL Builder Parent to Child":
                show_advanced_soql_query_builder(st.session_state["salesforce"])

        elif selected_section == "Visualizations":
            selected_visualization = option_menu(
                "Visualizations",
                ["Data Visualizations", "Smart Visualize"],
                icons=["bar-chart"],
                menu_icon="bar-chart",
                default_index=0,
            )
            if selected_visualization == "Data Visualizations":
                visualize_data(st.session_state["salesforce"])
            elif selected_visualization == "Smart Visualize":
                smart_visualize(st.session_state["salesforce"])

        elif selected_section == "Admin Tools":
            selected_admin = option_menu(
                "Admin Tools",
                ["Data Import/Export", "Scheduled Jobs Viewer", "Audit Logs Viewer"],
                icons=["upload", "clock", "book"],
                menu_icon="tools",
                default_index=0,
            )
            if selected_admin == "Data Import/Export":
                show_data_import_export(st.session_state["salesforce"])
            elif selected_admin == "Scheduled Jobs Viewer":
                view_scheduled_jobs(st.session_state["salesforce"])
            elif selected_admin == "Audit Logs Viewer":
                view_audit_logs(st.session_state["salesforce"])

        elif selected_section == "Help & Settings":
            selected_setting = option_menu(
                "Help & Settings",
                ["How to Use", "Logout"],
                icons=["info-circle", "box-arrow-right"],
                menu_icon="question-circle",
                default_index=0,
            )
            if selected_setting == "How to Use":
                show_how_to_use()

    else:
        # Handle non-authenticated user modules
        if selected_section == "Login":
            login()
        elif selected_section == "Register":
            register()
        elif selected_section == "How to Use":
            show_how_to_use()

if __name__ == "__main__":
    initialize_session()
    main()
