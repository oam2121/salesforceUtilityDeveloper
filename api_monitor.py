import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce
import io
import datetime

# Function to fetch API usage limits from Salesforce
def get_api_limits(sf):
    try:
        # Fetch limits from Salesforce
        limits_result = sf.limits()

        # Create a dictionary to store the limits data
        limits_data = {key: value for key, value in limits_result.items()}
        
        return limits_data
    except Exception as e:
        st.error(f"Error fetching API usage data: {e}")
        return {}

# Function to filter API limits by search term
def filter_limits(limits_data, search_term):
    if search_term:
        # Filter limits based on the search term
        return {key: value for key, value in limits_data.items() if search_term.lower() in key.lower()}
    return limits_data

# Function to export DataFrame to Excel
def convert_df_to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
        writer.close()
    return output.getvalue()

# Function to export DataFrame to CSV
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# Function to display API limits in the Streamlit app
def show_api_tools(sf):
    st.title("Salesforce API Tools")
    
    st.write("Here you can monitor your API usage and view limits across various resources.")
    st.write("This tool helps you understand your current API usage and limits to ensure you stay within your allocated limits. "
             "If you exceed these limits, you may experience disruptions in API access.")
    
    st.header("📊 API Usage and Limits")
    
    limits_data = get_api_limits(sf)
    
    if limits_data:
        st.subheader("API Usage and Limits Overview")
        
        # Search bar for filtering limits
        search_term = st.text_input("Search for a limit (e.g., 'API Requests')", "")
        st.markdown("**Tip:** Use the search bar to filter the API limits based on keywords. Hover over the information icons for more details.")
        
        # Filter the limits data based on the search term
        filtered_limits = filter_limits(limits_data, search_term)

        if filtered_limits:
            # Display data in table format with background color
            df = pd.DataFrame([{
                'Limit': key,
                'Max': value.get('Max', 'N/A'),
                'Used': value.get('Max', 0) - value.get('Remaining', 0),
                'Remaining': value.get('Remaining', 'N/A')
            } for key, value in filtered_limits.items()])
            
            # Show DataFrame in a table format with background color
            st.write(df.style.set_properties(**{'background-color': '#f0f2f6', 'color': 'black', 'border-color': 'black'}))

            # Download section for Excel and CSV
            st.subheader("Download Report")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name_prefix = f"API_Usage_Report_{timestamp}"

            col1, col2 = st.columns(2)
            with col1:
                excel_data = convert_df_to_excel(df)
                st.download_button(label="Download Excel", data=excel_data, file_name=f"{file_name_prefix}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with col2:
                csv_data = convert_df_to_csv(df)
                st.download_button(label="Download CSV", data=csv_data, file_name=f"{file_name_prefix}.csv", mime="text/csv")

            # Display collapsible sections for each limit
            for key, value in filtered_limits.items():
                with st.expander(f"{key} (Max: {value.get('Max', 'N/A')})"):
                    st.write(f"**Max:** {value.get('Max', 'N/A')}")
                    st.write(f"**Used:** {value.get('Max', 0) - value.get('Remaining', 0)} / **Remaining:** {value.get('Remaining', 'N/A')}")
                    # Information icon for additional context
                    st.info(f"This limit indicates the maximum number of {key.lower()} allowed. If you approach the limit, consider optimizing your API calls to prevent disruptions.")
        else:
            st.warning("No limits found matching your search term.")
    else:
        st.error("Failed to fetch API usage information.")

# Main function to run the app
def main(sf):
    show_api_tools(sf)

# Assuming the Salesforce connection `sf` is already available from your main application
if __name__ == "__main__":
    sf = Salesforce(username="your_username", password="your_password", security_token="your_token")
    main(sf)
