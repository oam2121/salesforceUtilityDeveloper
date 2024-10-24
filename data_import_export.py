import streamlit as st
from salesforce_api import import_csv_to_salesforce, export_salesforce_to_csv, export_salesforce_to_excel

def show_data_import_export(sf):
    data_action = st.sidebar.selectbox(
        "Data Actions",
        ['Import to Salesforce', 'Export from Salesforce']
    )

    if data_action == 'Import to Salesforce':
        st.subheader("Import CSV to Salesforce")
        uploaded_file = st.file_uploader("Choose a CSV file to import", type='csv')
        sobject_type = st.text_input("Enter Salesforce Object Type for import (e.g., Account)")
        if st.button("Import to Salesforce"):
            success, message = import_csv_to_salesforce(sf, sobject_type, uploaded_file)
            if success:
                st.success(message)
            else:
                st.error(message)

    elif data_action == 'Export from Salesforce':
        st.subheader("Export Salesforce to File")
        export_soql = st.text_area("Enter SOQL Query for export", "SELECT Id, Name FROM Account")
        file_format = st.selectbox("Select file format for export", ["CSV", "Excel"])
        if st.button("Export from Salesforce"):
            file_path = f"salesforce_data.{file_format.lower()}"
            if file_format == "CSV":
                success, message = export_salesforce_to_csv(sf, export_soql, file_path)
            else:
                success, message = export_salesforce_to_excel(sf, export_soql, file_path)
            if success:
                st.success(f"{message}. Download the file below:")
                with open(file_path, "rb") as file:
                    btn = st.download_button(
                        label="Download File",
                        data=file,
                        file_name=file_path,
                        mime="application/octet-stream"
                    )
            else:
                st.error(message)
