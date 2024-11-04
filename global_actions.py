import streamlit as st
from simple_salesforce import Salesforce
from datetime import datetime
import base64

# Function to create a new contact
def create_new_contact(sf):
    st.title("New Contact")
    salutation = st.selectbox("Salutation", ["--None--", "Mr.", "Ms.", "Mrs.", "Dr.", "Prof.", "Mx."])
    first_name = st.text_input("First Name")
    last_name = st.text_input("* Last Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    account_name = st.selectbox("Account Name", ["Search Accounts..."] + get_account_names(sf))

    if st.button("Create Contact"):
        try:
            contact = {
                'Salutation': salutation if salutation != "--None--" else None,
                'FirstName': first_name,
                'LastName': last_name,
                'Email': email,
                'Phone': phone,
                'AccountId': get_account_id_by_name(sf, account_name)
            }
            sf.Contact.create(contact)
            st.success("Contact created successfully!")
        except Exception as e:
            st.error(f"Error creating contact: {e}")

# Function to create a new opportunity
def create_new_opportunity(sf):
    st.title("New Opportunity")
    name = st.text_input("Opportunity Name")
    account_name = st.selectbox("Account Name", ["Search Accounts..."] + get_account_names(sf))
    close_date = st.date_input("Close Date")
    stage = st.selectbox("Stage", ["--None--", "Prospecting", "Qualification", "Proposal", "Closed Won", "Closed Lost"])
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")

    if st.button("Create Opportunity"):
        try:
            opportunity = {
                'Name': name,
                'AccountId': get_account_id_by_name(sf, account_name),
                'CloseDate': close_date.strftime("%Y-%m-%d"),
                'StageName': stage,
                'Amount': amount
            }
            sf.Opportunity.create(opportunity)
            st.success("Opportunity created successfully!")
        except Exception as e:
            st.error(f"Error creating opportunity: {e}")

# Function to create a new event
def create_new_event(sf):
    st.title("New Event")
    
    event_name = st.text_input("Event Name")
    related_contact = st.selectbox("Related To (Contact)", ["Search Contacts..."] + get_contact_names(sf))
    related_account = st.selectbox("Related To (Account)", ["Search Accounts..."] + get_account_names(sf))
    assigned_to = st.selectbox("Assigned To", ["Search Users..."] + get_user_names(sf))
    start_date = st.date_input("Start Date")
    start_time = st.time_input("Start Time")
    duration_minutes = st.number_input("Duration (in minutes)", min_value=1, value=30)

    if st.button("Create Event"):
        try:
            event = {
                'Subject': event_name,
                'WhatId': get_account_id_by_name(sf, related_account),
                'WhoId': get_contact_id_by_name(sf, related_contact),
                'OwnerId': get_user_id_by_name(sf, assigned_to),
                'ActivityDateTime': datetime.combine(start_date, start_time).isoformat(),
                'DurationInMinutes': duration_minutes
            }
            sf.Event.create(event)
            st.success("Event created successfully!")
        except Exception as e:
            st.error(f"Error creating event: {e}")

# Function to create a new case
def create_new_case(sf):
    st.title("New Case")
    contact_name = st.selectbox("Contact Name", ["Search Contacts..."] + get_contact_names(sf))
    status = st.selectbox("Status", ["New", "Working", "Escalated", "Closed"])
    subject = st.text_input("Subject")
    description = st.text_area("Description")

    if st.button("Create Case"):
        try:
            case = {
                'ContactId': get_contact_id_by_name(sf, contact_name),
                'Status': status,
                'Subject': subject,
                'Description': description
            }
            sf.Case.create(case)
            st.success("Case created successfully!")
        except Exception as e:
            st.error(f"Error creating case: {e}")

# Function to create a new lead
def create_new_lead(sf):
    st.title("New Lead")
    salutation = st.selectbox("Salutation", ["--None--", "Mr.", "Ms.", "Mrs.", "Dr.", "Prof.", "Mx."])
    first_name = st.text_input("First Name")
    last_name = st.text_input("* Last Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    company = st.text_input("* Company")

    if st.button("Create Lead"):
        try:
            lead = {
                'Salutation': salutation if salutation != "--None--" else None,
                'FirstName': first_name,
                'LastName': last_name,
                'Email': email,
                'Phone': phone,
                'Company': company
            }
            sf.Lead.create(lead)
            st.success("Lead created successfully!")
        except Exception as e:
            st.error(f"Error creating lead: {e}")

# Helper functions to fetch names and IDs
def get_account_names(sf):
    accounts = sf.query("SELECT Name FROM Account")
    return [account['Name'] for account in accounts['records']]

def get_contact_names(sf):
    contacts = sf.query("SELECT Name FROM Contact")
    return [contact['Name'] for contact in contacts['records']]

def get_user_names(sf):
    users = sf.query("SELECT Name FROM User")
    return [user['Name'] for user in users['records']]

def get_account_id_by_name(sf, account_name):
    accounts = sf.query(f"SELECT Id FROM Account WHERE Name = '{account_name}'")
    return accounts['records'][0]['Id'] if accounts['records'] else None

def get_contact_id_by_name(sf, contact_name):
    contacts = sf.query(f"SELECT Id FROM Contact WHERE Name = '{contact_name}'")
    return contacts['records'][0]['Id'] if contacts['records'] else None

def get_user_id_by_name(sf, user_name):
    users = sf.query(f"SELECT Id FROM User WHERE Name = '{user_name}'")
    return users['records'][0]['Id'] if users['records'] else None
# Function to upload a file
def upload_file_to_salesforce(sf):
    st.title("Upload File")
    file = st.file_uploader("Choose a file", type=["pdf", "doc", "docx", "png", "jpg", "jpeg", "txt"])
    
    if file is not None:
        file_name = file.name
        file_data = file.read()

        # Encode the file data
        file_data_encoded = base64.b64encode(file_data).decode('utf-8')

        # Create a ContentVersion object to upload the file
        content_version = {
            'Title': file_name,
            'PathOnClient': file_name,
            'VersionData': file_data_encoded,
            'IsMajorVersion': True
        }

        try:
            # Create a new content version in Salesforce
            sf.ContentVersion.create(content_version)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error uploading file: {e}")

# Function to display global actions in the Streamlit app
def show_global_actions(sf):
    st.title("Global Actions")
    action = st.selectbox("Select an Action", [
        "New Contact",
        "New Opportunity",
        "New Event",
        "New Case",
        "New Lead",
        "Upload File"
    ])

    if action == "New Contact":
        create_new_contact(sf)
    elif action == "New Opportunity":
        create_new_opportunity(sf)
    elif action == "New Event":
        create_new_event(sf)
    elif action == "New Case":
        create_new_case(sf)
    elif action == "New Lead":
        create_new_lead(sf)
    elif action == "Upload File":
        upload_file_to_salesforce(sf)  # Call the upload file function