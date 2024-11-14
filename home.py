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

# Fetch data from Salesforce
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

# Fetch recent activity dynamically
def get_recent_activity(sf):
    recent_opportunities_query = """
        SELECT Id, Name, LastModifiedDate 
        FROM Opportunity 
        ORDER BY LastModifiedDate DESC 
        LIMIT 5
    """
    recent_opportunities = sf.query(recent_opportunities_query).get('records', [])

    recent_contacts_query = """
        SELECT Id, Name, LastModifiedDate 
        FROM Contact 
        ORDER BY LastModifiedDate DESC 
        LIMIT 5
    """
    recent_contacts = sf.query(recent_contacts_query).get('records', [])

    recent_activity = []
    for opportunity in recent_opportunities:
        recent_activity.append({
            "Id": opportunity["Id"],
            "Action": f"Updated Opportunity: {opportunity['Name']}",
            "Timestamp": opportunity["LastModifiedDate"]
        })

    for contact in recent_contacts:
        recent_activity.append({
            "Id": contact["Id"],
            "Action": f"Updated Contact: {contact['Name']}",
            "Timestamp": contact["LastModifiedDate"]
        })

    sorted_activity = sorted(recent_activity, key=lambda x: x["Timestamp"], reverse=True)[:5]
    return sorted_activity

# Display recent activity
def display_recent_activity(sf):
    st.markdown("---")
    st.markdown("### 🔄 Recent Activity")
    recent_activity = get_recent_activity(sf)

    for activity in recent_activity:
        st.markdown(
            f"""
            <div style="border: 1px solid #ddd; border-radius: 5px; padding: 10px; margin-bottom: 10px;">
                <strong>{activity['Action']}</strong><br>
                <small>Timestamp: {activity['Timestamp']}</small>
            </div>
            """,
            unsafe_allow_html=True
        )

# Display metrics
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

# Display Home Page
def display_home(sf):
    st.markdown("<h1 style='text-align: center; color: #3E8E7E;'>🚀 Salesforce Developer Utility</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #3E8E7E;'>Elevate your Salesforce Development with Powerful Tools</h3>", unsafe_allow_html=True)
    
    st.markdown("### ⚡ Quick Actions", unsafe_allow_html=True)
    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        if st.button("📇 New Contact", key="contact_button"):
            st.session_state.selected_action = "New Contact"
    with col2:
        if st.button("💼 New Opp", key="opportunity_button"):
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

    display_metrics(sf)
    display_recent_activity(sf)

# Main function
def main():
    sf = Salesforce(username="your_username", password="your_password", security_token="your_token")
    display_home(sf)

if __name__ == "__main__":
    main()
