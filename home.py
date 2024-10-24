import streamlit as st
from simple_salesforce import Salesforce

# Function to fetch data from Salesforce
def get_salesforce_data(sf):
    # Get active users count
    active_users_query = "SELECT COUNT() FROM User WHERE IsActive = true"
    active_users_result = sf.query(active_users_query)
    active_users_count = active_users_result['totalSize']

    # Get Salesforce API usage
    limits_result = sf.limits()
    
    # Handle specific key lookups with fallback to 0
    api_calls_made = limits_result.get('DailyApiRequests', {}).get('Remaining', 0)
    api_calls_limit = limits_result.get('DailyApiRequests', {}).get('Max', 0)
    
    # Get scheduled jobs count
    scheduled_jobs_query = "SELECT COUNT() FROM AsyncApexJob WHERE Status = 'Queued'"
    scheduled_jobs_result = sf.query(scheduled_jobs_query)
    scheduled_jobs_count = scheduled_jobs_result['totalSize']

    # Return all useful metrics, adding additional limits as needed
    data_storage = limits_result.get('DataStorageMB', {}).get('Remaining', 0)
    file_storage = limits_result.get('FileStorageMB', {}).get('Remaining', 0)
    workflow_emails = limits_result.get('DailyWorkflowEmails', {}).get('Remaining', 0)

    return active_users_count, api_calls_made, api_calls_limit, scheduled_jobs_count, data_storage, file_storage, workflow_emails

# Function to display the home page with app information and features
def display_home(sf):
    st.title("🚀 Salesforce Developer Utility")
    st.subheader("Elevate your Salesforce Development with Powerful Tools")
    
    # Fetch real data from Salesforce
    active_users_count, api_calls_made, api_calls_limit, scheduled_jobs_count, data_storage, file_storage, workflow_emails = get_salesforce_data(sf)
    
    # Adding metrics section at the top
    st.markdown("---")
    st.markdown("### 🔍 Key App Metrics")
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        st.metric(label="Active Users", value=f"{active_users_count}")
    
    with col_b:
        st.metric(label="Salesforce API Calls", value=f"{api_calls_made}", delta=f"{api_calls_limit - api_calls_made} remaining")
    
    with col_c:
        st.metric(label="Scheduled Jobs", value=f"{scheduled_jobs_count}")
    
    # Second row of metrics
    st.markdown("---")
    st.markdown("### 📊 Storage & Email Quotas")
    col_d, col_e, col_f = st.columns(3)
    
    with col_d:
        st.metric(label="Data Storage (MB)", value=f"{data_storage}")

    with col_e:
        st.metric(label="File Storage (MB)", value=f"{file_storage}")
    
    with col_f:
        st.metric(label="Remaining Workflow Emails", value=f"{workflow_emails}")
    
    # App description and utility cards
    st.markdown("---")
    with st.expander("About the Salesforce Developer Utility"):
        st.write("""
        The **Salesforce Developer Utility** helps Salesforce developers streamline their tasks by providing a suite of tools.
        From querying Salesforce data to managing scheduled jobs, this utility has all the features you need for efficient development.
        """)

    # Create columns for the cards layout
    col1, col2, col3 = st.columns(3)

    # Card 1: Query Builder
    with col1:
        st.markdown("### ⚙️ Query Builder")
        st.write("Build SOQL queries visually and retrieve data from your Salesforce org.")
        if st.button("Go to Query Builder"):
            st.write("Navigating to Query Builder...")  # Handle button logic

    # Card 2: Data Import/Export
    with col2:
        st.markdown("### 📤 Data Import/Export")
        st.write("Import and export data easily between your local environment and Salesforce.")
        if st.button("Go to Data Import/Export"):
            st.write("Navigating to Data Import/Export...")  # Handle button logic

    # Card 3: Describe Object
    with col3:
        st.markdown("### 📄 Describe Object")
        st.write("Get metadata information about any Salesforce object, including field names, types, and more.")
        if st.button("Go to Describe Object"):
            st.write("Navigating to Describe Object...")  # Handle button logic

    # Second row of cards
    col4, col5, col6 = st.columns(3)

    # Card 4: Search Salesforce
    with col4:
        st.markdown("### 🔍 Search Salesforce")
        st.write("Search records, objects, and metadata quickly and efficiently in your Salesforce org.")
        if st.button("Go to Search Salesforce"):
            st.write("Navigating to Search Salesforce...")  # Handle button logic

    # Card 5: Data Visualizations
    with col5:
        st.markdown("### 📊 Data Visualizations")
        st.write("Visualize Salesforce data with interactive charts and graphs.")
        if st.button("Go to Data Visualizations"):
            st.write("Navigating to Data Visualizations...")  # Handle button logic

    # Card 6: Scheduled Jobs Viewer
    with col6:
        st.markdown("### ⏲️ Scheduled Jobs Viewer")
        st.write("View and manage your scheduled jobs in Salesforce.")
        if st.button("Go to Scheduled Jobs Viewer"):
            st.write("Navigating to Scheduled Jobs Viewer...")  # Handle button logic

    # Third row of cards
    col7, col8 = st.columns(2)

    # Card 7: Audit Logs Viewer
    with col7:
        st.markdown("### 📚 Audit Logs Viewer")
        st.write("View audit logs and track user actions within your Salesforce org.")
        if st.button("Go to Audit Logs Viewer"):
            st.write("Navigating to Audit Logs Viewer...")  # Handle button logic

    # Card 8: How to Use
    with col8:
        st.markdown("### ❓ How to Use")
        st.write("Get step-by-step instructions on how to set up and use the app.")
        if st.button("Go to How to Use"):
            st.write("Navigating to How to Use...")  # Handle button logic

    # Additional footer section with alerts and useful links
    st.markdown("---")
    st.success("💡 Tip: Visit the 'How to Use' section for a comprehensive guide on setting up this utility.")
    st.info("🔗 Learn more about [Salesforce API Best Practices](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/intro_what_is_rest_api.htm).")

    # Additional useful links for Apex, LWC, and Trailhead
    st.markdown("### 📚 More Useful Salesforce Resources")
    st.markdown("""
    - **Apex Documentation:** [Apex Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/)
    - **LWC Documentation:** [Lightning Web Components Guide](https://developer.salesforce.com/docs/component-library/documentation/en/lwc)
    - **Trailhead:** [Salesforce Trailhead Learning](https://trailhead.salesforce.com/)
    - **SOQL and SOSL:** [Salesforce Object Query Language (SOQL) Guide](https://developer.salesforce.com/docs/atlas.en-us.224.0.soql_sosl.meta/soql_sosl/)
    - **REST API:** [Salesforce REST API Developer Guide](https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta/api_rest/)
    """)

# Main function to run the app
def main():
    # Salesforce login credentials (example)
    sf = Salesforce(username='your_username', password='your_password', security_token='your_token')

    # List of modules for your application
    modules = {
        'Home': display_home,  # Home function now requires sf
        'Query Builder': None,  # Placeholder for actual function
        'Data Import/Export': None,  # Placeholder for actual function
        'Describe Object': None,  # Placeholder for actual function
        'Search Salesforce': None,  # Placeholder for actual function
        'Data Visualizations': None,  # Placeholder for actual function
        'Scheduled Jobs Viewer': None,  # Placeholder for actual function
        'Audit Logs Viewer': None  # Placeholder for actual function
    }

    # Assuming you have some logic to select the module (e.g., from a sidebar)
    selected_module = 'Home'  # Example, replace this with actual logic

    # When 'Home' is selected, pass the 'sf' instance to display_home
    if selected_module == 'Home':
        modules['Home'](sf)  # Pass Salesforce instance to display_home
    else:
        # Other modules
        module_function = modules[selected_module]
        if module_function:
            module_function()  # Handle other modules

# Call the main function to display the home page
if __name__ == "__main__":
    main()
