import streamlit as st
import pandas as pd
from salesforce_api import retrieve_records, create_record, update_record, delete_record

def show_query_builder(sf):
    query_action = st.sidebar.selectbox(
        "Query Actions",
        ['Fetch Records', 'Create Record', 'Update Record', 'Delete Record']
    )

    if query_action == 'Fetch Records':
        st.subheader("SOQL Query Runner")
        query = st.text_area("Enter SOQL Query", "SELECT Id, Name FROM Account LIMIT 10")
        if st.button("Run Query"):
            records = retrieve_records(sf, query)
            if records:
                df = pd.DataFrame(records)
                st.dataframe(df)
            else:
                st.error("No records fetched or query failed.")

    elif query_action == 'Create Record':
        st.subheader("Create Record")
        sobject = st.text_input("Salesforce Object Type (e.g., Account)")
        record_details = st.text_area("Enter record details in dictionary format", "{}")
        if st.button("Create Record"):
            record_data = eval(record_details)
            result = create_record(sf, sobject, record_data)
            if result.get('success'):
                st.success(f"Record created successfully. ID: {result['id']}")
            else:
                st.error(f"Failed to create record: {result.get('message')}")

    elif query_action == 'Update Record':
        st.subheader("Update Record")
        sobject = st.text_input("Salesforce Object Type (e.g., Account)", key='update_sobject')
        if st.button("Fetch Records to Update", key='update_fetch'):
            records = retrieve_records(sf, f"SELECT Id, Name FROM {sobject} LIMIT 50")
            if records:
                record_names = [rec['Name'] for rec in records]
                record_ids = {rec['Name']: rec['Id'] for rec in records}
                st.session_state['update_records'] = record_ids
                st.session_state['update_names'] = record_names
            else:
                st.error("No records found or query failed.")
        if 'update_names' in st.session_state:
            selected_name = st.selectbox("Select Record to Update", st.session_state['update_names'])
            update_details = st.text_area("Enter update details in dictionary format", "{}")
            if st.button("Update Record"):
                record_id = st.session_state['update_records'][selected_name]
                update_data = eval(update_details)
                result = update_record(sf, sobject, record_id, update_data)
                if result.get('success'):
                    st.success("Record updated successfully.")
                else:
                    st.error(f"Failed to update record: {result.get('message')}")

    elif query_action == 'Delete Record':
        st.subheader("Delete Record")
        sobject = st.text_input("Salesforce Object Type (e.g., Account)", key='delete_sobject')
        if st.button("Fetch Records to Delete", key='delete_fetch'):
            records = retrieve_records(sf, f"SELECT Id, Name FROM {sobject} LIMIT 50")
            if records:
                delete_names = [rec['Name'] for rec in records]
                delete_ids = {rec['Name']: rec['Id'] for rec in records}
                st.session_state['delete_records'] = delete_ids
                st.session_state['delete_names'] = delete_names
            else:
                st.error("No records found or query failed.")
        if 'delete_names' in st.session_state:
            selected_name = st.selectbox("Select Record to Delete", st.session_state['delete_names'])
            if st.button("Delete Record"):
                record_id = st.session_state['delete_records'][selected_name]
                result = delete_record(sf, sobject, record_id)
                if result.get('success'):
                    st.success("Record deleted successfully.")
                else:
                    st.error(f"Failed to delete record: {result.get('message')}")

# Assuming 'sf' is your Salesforce connection object
# show_query_builder(sf)
