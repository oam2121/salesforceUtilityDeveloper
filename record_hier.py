import streamlit as st
from simple_salesforce import Salesforce

# Function to fetch all records of an object
def fetch_records(sf, object_name):
    try:
        query = f"SELECT Id, Name FROM {object_name} ORDER BY Name LIMIT 100"
        result = sf.query(query)
        if result['records']:
            return result['records']
        else:
            st.warning(f"No records found for object '{object_name}'")
            return []
    except Exception as e:
        st.error(f"Error fetching records from {object_name}: {str(e)}")
        return []

# Function to get hierarchy of records
def get_hierarchy(sf, object_name, record_id, parent_field):
    try:
        hierarchy = []
        query = f"SELECT Id, Name, {parent_field} FROM {object_name} WHERE Id = '{record_id}'"
        record = sf.query(query)['records'][0]

        while record:
            hierarchy.append(record)
            parent_id = record.get(parent_field)
            if parent_id:
                record = sf.query(f"SELECT Id, Name, {parent_field} FROM {object_name} WHERE Id = '{parent_id}'")['records'][0] if sf.query(f"SELECT Id, Name, {parent_field} FROM {object_name} WHERE Id = '{parent_id}'")['records'] else None
            else:
                break

        return hierarchy
    except Exception as e:
        st.error(f"Error fetching hierarchy: {str(e)}")
        return []

# Function to display hierarchy with arrows
def display_hierarchy(hierarchy):
    if hierarchy:
        st.write("### Hierarchy:")
        for i, record in enumerate(hierarchy):
            st.write(f"{'→' * i} {record['Name']} (ID: {record['Id']})")
    else:
        st.write("No hierarchy found.")

# Main function to run the hierarchy viewer
def hierarchy_viewer(sf):
    st.title("Record Hierarchy Viewer")
    st.write("Visualize hierarchical relationships between records in Salesforce.")

    object_name = st.text_input("Enter the Salesforce object name (e.g., Account, CustomObject__c)", "Account")
    records = fetch_records(sf, object_name)
    
    if records:
        record_names = {rec['Name']: rec['Id'] for rec in records}
        selected_name = st.selectbox("Select a record", list(record_names.keys()))

        if st.button("Show Hierarchy"):
            selected_id = record_names[selected_name]
            st.write(f"Search results for '{selected_name}':")
            st.write(f"Name: {selected_name}, ID: {selected_id}")
            hierarchy = get_hierarchy(sf, object_name, selected_id, 'ParentId')
            display_hierarchy(hierarchy)

# Assuming the Salesforce connection `sf` is already available from your main application
def main(sf):
    hierarchy_viewer(sf)

# Example Salesforce connection initialization
if __name__ == "__main__":
    sf = Salesforce(username="your_username", password="your_password", security_token="your_token")
    main(sf)
