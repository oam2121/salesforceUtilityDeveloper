import streamlit as st
import pandas as pd
from io import BytesIO
from simple_salesforce import Salesforce

# Function to create an Excel file for download
def convert_df_to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.close()  # Use close() instead of save()
    output.seek(0)
    return output

# Function to create a CSV file for download
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to fetch list of users along with their licenses and basic info
def fetch_users_and_licenses(sf):
    try:
        query = """
            SELECT Id, Name, Username, Profile.Name, UserRole.Name, IsActive, UserType
            FROM User
        """
        user_data = sf.query(query)['records']
        return user_data
    except Exception as e:
        st.error(f"Error fetching users: {str(e)}")
        return []

# Function to fetch profiles (both standard and custom)
def fetch_profiles(sf):
    try:
        query = "SELECT Id, Name, UserLicense.Name FROM Profile"
        profiles_data = sf.query(query)['records']
        return profiles_data
    except Exception as e:
        st.error(f"Error fetching profiles: {str(e)}")
        return []

# Function to fetch role hierarchy (showing parent-child relationships)
def fetch_role_hierarchy(sf):
    try:
        query = """
            SELECT Id, Name, ParentRoleId 
            FROM UserRole
        """
        roles_data = sf.query(query)['records']
        return roles_data
    except Exception as e:
        st.error(f"Error fetching roles: {str(e)}")
        return []

# Display users, licenses, profiles, and role hierarchy in separate dropdowns
def display_user_info(sf):
    st.title("Salesforce Users, Licenses, Profiles, and Role Hierarchy")
    
    # Section for User Information and Licenses
    with st.expander("📋 User Information and Licenses"):
        user_data = fetch_users_and_licenses(sf)
        if user_data:
            st.write("Here is a list of users, their profiles, and their assigned roles.")
            user_table = []
            for user in user_data:
                profile = user.get('Profile')
                profile_name = profile['Name'] if profile else 'No Profile'
                user_role = user.get('UserRole')
                role_name = user_role['Name'] if user_role else 'No Role'
                is_active = "Active" if user['IsActive'] else "Inactive"
                user_table.append([user['Name'], user['Username'], profile_name, role_name, is_active])

            # Display users in a table
            user_df = pd.DataFrame(user_table, columns=["Name", "Username", "Profile", "Role", "Status"])
            st.table(user_df)

            # Add download buttons
            st.download_button(
                label="📥 Download as CSV",
                data=convert_df_to_csv(user_df),
                file_name='user_info.csv',
                mime='text/csv'
            )
            st.download_button(
                label="📥 Download as Excel",
                data=convert_df_to_excel(user_df),
                file_name='user_info.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.error("No user data available.")

    # Section for Profile Information
    with st.expander("🔑 Profile Information"):
        profiles_data = fetch_profiles(sf)
        if profiles_data:
            st.write("Here is a list of profiles and their associated licenses.")
            profile_table = []
            for profile in profiles_data:
                profile_table.append([profile['Name'], profile.get('UserLicense', {}).get('Name', 'N/A')])
            
            # Display profiles in a table
            profile_df = pd.DataFrame(profile_table, columns=["Profile Name", "License"])
            st.table(profile_df)

            # Add download buttons
            st.download_button(
                label="📥 Download as CSV",
                data=convert_df_to_csv(profile_df),
                file_name='profile_info.csv',
                mime='text/csv'
            )
            st.download_button(
                label="📥 Download as Excel",
                data=convert_df_to_excel(profile_df),
                file_name='profile_info.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.error("No profile data available.")

    # Section for Role Hierarchy
    with st.expander("🏢 Role Hierarchy"):
        roles_data = fetch_role_hierarchy(sf)
        if roles_data:
            st.write("Roles are shown with their parent-child relationships.")
            
            # Prepare role hierarchy table
            role_table = []

            def display_role_hierarchy(roles, parent_role_id=None, level=0):
                """Recursively display the role hierarchy with indentation."""
                for role in roles:
                    if role['ParentRoleId'] == parent_role_id:
                        role_table.append([role['Name'], ' ' * (level * 2), role['Id']])
                        # Recursive call to display children roles
                        display_role_hierarchy(roles, role['Id'], level + 1)
            
            display_role_hierarchy(roles_data)

            # Display role hierarchy in a table
            role_df = pd.DataFrame(role_table, columns=["Role Name", "Indentation", "Role ID"])
            st.table(role_df)

            # Add download buttons
            st.download_button(
                label="📥 Download as CSV",
                data=convert_df_to_csv(role_df),
                file_name='role_hierarchy.csv',
                mime='text/csv'
            )
            st.download_button(
                label="📥 Download as Excel",
                data=convert_df_to_excel(role_df),
                file_name='role_hierarchy.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            st.error("No role hierarchy data available.")

# Main function to run the app
def main(sf):
    display_user_info(sf)

# Example Salesforce connection initialization
if __name__ == "__main__":
    # sf = Salesforce(username="your_username", password="your_password", security_token="your_token")
    # Example call to main function
    main(sf)
