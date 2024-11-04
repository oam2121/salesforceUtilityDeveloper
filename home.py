# home.py
import streamlit as st
from simple_salesforce import Salesforce
from global_actions import (
    create_new_contact,
    create_new_opportunity,
    create_new_event,
    create_new_case,
    create_new_lead,
    upload_file_to_salesforce,
)

# Function to fetch data from Salesforce
def get_salesforce_data(sf):
    active_users_query = "SELECT COUNT() FROM User WHERE IsActive = true"
    active_users_result = sf.query(active_users_query)
    active_users_count = active_users_result['totalSize']

    limits_result = sf.limits()
    api_calls_made = limits_result.get('DailyApiRequests', {}).get('Remaining', 0)
    api_calls_limit = limits_result.get('DailyApiRequests', {}).get('Max', 0)
    
    scheduled_jobs_query = "SELECT COUNT() FROM AsyncApexJob WHERE Status = 'Queued'"
    scheduled_jobs_result = sf.query(scheduled_jobs_query)
    scheduled_jobs_count = scheduled_jobs_result['totalSize']

    data_storage = limits_result.get('DataStorageMB', {}).get('Remaining', 0)
    file_storage = limits_result.get('FileStorageMB', {}).get('Remaining', 0)
    workflow_emails = limits_result.get('DailyWorkflowEmails', {}).get('Remaining', 0)

    return active_users_count, api_calls_made, api_calls_limit, scheduled_jobs_count, data_storage, file_storage, workflow_emails

# Function to display the main page with Quick Actions and metrics
def display_home(sf):
    st.markdown("<h1 style='text-align: center; color: #3E8E7E;'>🚀 Salesforce Developer Utility</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #3E8E7E;'>Elevate your Salesforce Development with Powerful Tools</h3>", unsafe_allow_html=True)
    
    # Initialize session state for selected action if it doesn't exist
    if 'selected_action' not in st.session_state:
        st.session_state.selected_action = None

    # Adding Quick Actions section
    st.markdown("### ⚡ Quick Actions", unsafe_allow_html=True)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        if st.button("📇 New Contact", key="contact_button"):
            st.session_state.selected_action = "New Contact"
    with col2:
        if st.button("💼 New Opportunity", key="opportunity_button"):
            st.session_state.selected_action = "New Opportunity"
    with col3:
        if st.button("🗓️ New Event", key="event_button"):
            st.session_state.selected_action = "New Event"
    with col4:
        if st.button("🛠️ New Case", key="case_button"):
            st.session_state.selected_action = "New Case"
    with col5:
        if st.button("👤 New Lead", key="lead_button"):
            st.session_state.selected_action = "New Lead"
    with col6:
        if st.button("📁 Upload File", key="file_button"):
            st.session_state.selected_action = "Upload File"

    # Displaying the selected form below the buttons
    action_function_map = {
        "New Contact": create_new_contact,
        "New Opportunity": create_new_opportunity,
        "New Event": create_new_event,
        "New Case": create_new_case,
        "New Lead": create_new_lead,
        "Upload File": upload_file_to_salesforce
    }

    if st.session_state.selected_action:
        action_function_map[st.session_state.selected_action](sf)

    # Fetch and display Salesforce metrics
    display_metrics(sf)

def display_metrics(sf):
    st.markdown("---")
    st.markdown("### 🔍 Key App Metrics")
    active_users_count, api_calls_made, api_calls_limit, scheduled_jobs_count, data_storage, file_storage, workflow_emails = get_salesforce_data(sf)
    
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric(label="Active Users", value=f"{active_users_count}")
    with col_b:
        st.metric(label="Salesforce API Calls", value=f"{api_calls_made}", delta=f"{api_calls_limit - api_calls_made} remaining")
    with col_c:
        st.metric(label="Scheduled Jobs", value=f"{scheduled_jobs_count}")
    
    st.markdown("---")
    st.markdown("### 📊 Storage & Email Quotas")
    col_d, col_e, col_f = st.columns(3)
    with col_d:
        st.metric(label="Data Storage (MB)", value=f"{data_storage}")
    with col_e:
        st.metric(label="File Storage (MB)", value=f"{file_storage}")
    with col_f:
        st.metric(label="Remaining Workflow Emails", value=f"{workflow_emails}")


# Main function to run the app
def main():
    # Salesforce login credentials (example)
    sf = Salesforce(username='your_username', password='your_password', security_token='your_token')

    # Display the home page with quick actions and metrics
    display_home(sf)

# Run the main function
if __name__ == "__main__":
    main()
