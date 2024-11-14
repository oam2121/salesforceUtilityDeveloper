import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager

# Importing required modules
from db_manager import init_db, register_user, verify_user, get_user_data
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

# Initialize the database
st.write("Initializing the database...")
init_db()

# Temporarily hardcoded password for debugging purposes
PASSWORD = "TemporarySecurePassword123!"  # Replace with your production secret
st.write("Setting up cookie manager...")

# Initialize the cookie manager
cookies = EncryptedCookieManager(prefix="salesforce_app_", password=PASSWORD)
if not cookies.ready():
    st.error("Cookies are not ready. Stopping app.")
    st.stop()

# Initialize session state
def initialize_session():
    if "is_authenticated" not in st.session_state:
        st.session_state["is_authenticated"] = False
    if "user_data" not in st.session_state:
        st.session_state["user_data"] = None
    if "salesforce" not in st.session_state:
        st.session_state["salesforce"] = None

    # Restore authentication from cookies if available
    if cookies.get("is_authenticated") == "true":
        st.session_state["is_authenticated"] = True
        user_data = cookies.get("user_data")
        if user_data:
            st.session_state["user_data"] = eval(user_data)
        st.write("Session restored from cookies.")

initialize_session()

# Function to handle registration
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
                st.error("Username already exists. Please try another username.")
        else:
            st.error("PIN must be exactly 6 digits.")

# Function to handle login
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
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Salesforce authentication failed: {e}")
                st.session_state["is_authenticated"] = False
        else:
            st.error("Invalid username, password, or PIN.")

# Function to handle logout
def logout():
    st.session_state["is_authenticated"] = False
    st.session_state["user_data"] = None
    st.session_state["salesforce"] = None

    # Clear cookies
    cookies["is_authenticated"] = "false"
    cookies["user_data"] = ""
    cookies.save()

    st.experimental_rerun()

# Main application
def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")

        if st.session_state["is_authenticated"]:
            # Authenticated User Menu
            selected_section = option_menu(
                "Sections",
                ["Salesforce Tools", "SOQL Builder", "Visualizations", "Admin Tools", "Help & Settings"],
                icons=["briefcase", "fan", "bar-chart-line", "wrench", "gear"],
                menu_icon="menu-app", default_index=0
            )

            # Nested Menus
            if selected_section == "Salesforce Tools":
                selected_module = option_menu(
                    "Salesforce Tools",
                    ["Query Builder", "Describe Object", "Search Salesforce", "API Tools", "Record Hierarchy"],
                    icons=["wrench", "book", "search", "gear", "tree"],
                    menu_icon="cloud", default_index=0
                )
                # Call relevant module functions
                if selected_module == "Query Builder":
                    show_query_builder(st.session_state["salesforce"])
                elif selected_module == "Describe Object":
                    show_describe_object(st.session_state["salesforce"])
                elif selected_module == "Search Salesforce":
                    show_search_salesforce(st.session_state["salesforce"])
                elif selected_module == "API Tools":
                    show_api_tools(st.session_state["salesforce"])
                elif selected_module == "Record Hierarchy":
                    hierarchy_viewer(st.session_state["salesforce"])

            elif selected_section == "SOQL Builder":
                selected_module = option_menu(
                    "SOQL Builder",
                    ["SOQL Builder Child to Parent", "SOQL BUILDER Parent to Child"],
                    icons=["hurricane", "cpu"],
                    menu_icon="cloud", default_index=0
                )
                if selected_module == "SOQL Builder Child to Parent":
                    show_soql_query_builder(st.session_state["salesforce"])
                elif selected_module == "SOQL BUILDER Parent to Child":
                    show_advanced_soql_query_builder(st.session_state["salesforce"])

            elif selected_section == "Visualizations":
                selected_module = option_menu(
                    "Visualizations",
                    ["Data Visualizations", "Smart Visualize"],
                    icons=["bar-chart"],
                    menu_icon="bar-chart", default_index=0
                )
                if selected_module == "Data Visualizations":
                    visualize_data(st.session_state["salesforce"])
                elif selected_module == "Smart Visualize":
                    smart_visualize(st.session_state["salesforce"])

            elif selected_section == "Admin Tools":
                selected_module = option_menu(
                    "Admin Tools",
                    ["Data Import/Export", "Scheduled Jobs Viewer", "Audit Logs Viewer"],
                    icons=["upload", "clock", "book"],
                    menu_icon="tools", default_index=0
                )
                if selected_module == "Data Import/Export":
                    show_data_import_export(st.session_state["salesforce"])
                elif selected_module == "Scheduled Jobs Viewer":
                    view_scheduled_jobs(st.session_state["salesforce"])
                elif selected_module == "Audit Logs Viewer":
                    view_audit_logs(st.session_state["salesforce"])

            elif selected_section == "Help & Settings":
                selected_module = option_menu(
                    "Help & Settings",
                    ["How to Use", "Logout"],
                    icons=["info-circle", "box-arrow-right"],
                    menu_icon="question-circle", default_index=0
                )
                if selected_module == "How to Use":
                    show_how_to_use()
                elif selected_module == "Logout":
                    logout()

        else:
            # Non-Authenticated Menu
            selected_module = option_menu(
                "Authentication Menu",
                ["Login", "Register", "How to Use"],
                icons=["box-arrow-in-right", "person-plus", "info-circle"],
                menu_icon="lock", default_index=0
            )

            if selected_module == "Login":
                login()
            elif selected_module == "Register":
                register()
            elif selected_module == "How to Use":
                show_how_to_use()

    # Load content based on authentication state
    if st.session_state["is_authenticated"]:
        st.write("Welcome to Salesforce Utility App!")
    else:
        st.write("Please log in to continue.")

if __name__ == "__main__":
    main()
