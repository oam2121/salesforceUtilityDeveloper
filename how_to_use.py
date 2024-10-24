import streamlit as st
from fpdf import FPDF
from io import BytesIO

def show_how_to_use():
    st.title("How to Use the App")
    st.header("Step-by-Step Guide to Setting Up Your Salesforce Connected App")

    # Step 1: Creating a Connected App
    st.subheader("1. Creating a Connected App in Salesforce")
    st.write("""
    - **Log in to Salesforce**: Make sure you have an admin account.
    - Navigate to **Setup**: Click on the gear icon in the upper-right corner, then click on 'Setup'.
    - In the Quick Find box, type **App Manager** and click on it.
    - Click the **New Connected App** button.
    - In the **Basic Information** section, fill in the following fields:
      - **Connected App Name**: Enter a name for your app.
      - **API Name**: This will be auto-filled based on the app name but can be edited.
      - **Contact Email**: Provide your email address.
    - Under **API (Enable OAuth Settings)**, check the box labeled **Enable OAuth Settings**.
    """)

    # Step 2: Enable OAuth Settings
    st.subheader("2. Enable OAuth Settings")
    st.write("""
    - After enabling OAuth, configure the **OAuth Settings**:
      - In the **Callback URL** field, enter `https://localhost/oauth/callback` or your application’s actual URL. This URL is where Salesforce will send responses after authentication.
      - In the **Selected OAuth Scopes** section, choose the permissions your app needs. Add the following scopes:
        - `Full Access (full)`
        - `Perform requests on your behalf at any time (refresh_token, offline_access)`
        - `Access and manage your data (api)`
    - Optionally, add any additional OAuth scopes based on the app's requirements.
    - Click **Save**. You will receive a message indicating that the app may take 2-10 minutes to become available.
    """)

    # Step 3: Obtaining Client ID and Secret
    st.subheader("3. Obtaining the Client ID and Client Secret")
    st.write("""
    - Once your Connected App is ready, click on the **Manage Consumer Details** button.
    - You will see the **Consumer Key** (this is your Client ID) and **Consumer Secret**.
    - Copy these values and store them securely. You will need them to configure OAuth in your application.
    """)

    # Step 4: Obtaining Security Token
    st.subheader("4. Obtaining Your Salesforce Security Token")
    st.write("""
    - Log in to Salesforce.
    - Click on your user icon in the top right and go to **Settings**.
    - Under **My Personal Information**, click on **Reset My Security Token**.
    - Click the **Reset Security Token** button.
    - Salesforce will send a new security token to the email address associated with your account.
    - Check your email and copy the token. You will need this along with your Salesforce password to authenticate API calls.
    """)

    st.write("Once you have the Client ID, Client Secret, and Security Token, you can configure your app to authenticate with Salesforce.")

    # Button to download PDF
    if st.button("Download as PDF"):
        generate_pdf()

# Function to generate a PDF with the same steps
def generate_pdf():
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "How to Use the App: Setting Up a Salesforce Connected App", ln=True, align='C')

    pdf.ln(10)  # Line break

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "1. Creating a Connected App in Salesforce", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, """
    - Log in to Salesforce and navigate to Setup.
    - In the Quick Find box, type 'App Manager' and click on it.
    - Click 'New Connected App'.
    - Fill in the required fields (Connected App Name, API Name, Contact Email).
    - Check the box labeled 'Enable OAuth Settings'.
    """)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "2. Enable OAuth Settings", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, """
    - In the OAuth settings section, enter a Callback URL and select OAuth scopes.
    - Add the following scopes: Full Access (full), Perform requests on your behalf at any time, Access and manage your data.
    - Click 'Save' and wait for the app to become available.
    """)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "3. Obtaining Client ID and Secret", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, """
    - After saving, go to 'Manage Consumer Details'.
    - Copy the Consumer Key (Client ID) and Consumer Secret and store them securely.
    """)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, "4. Obtaining Your Salesforce Security Token", ln=True)
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, """
    - Go to Profile Settings > My Personal Information > Reset My Security Token.
    - Salesforce will email you a new security token.
    """)

    # Use BytesIO to create an in-memory file
    pdf_output = BytesIO()

    # Generate the PDF as a string and write it to the buffer
    pdf_string = pdf.output(dest='S').encode('latin1')
    pdf_output.write(pdf_string)
    pdf_output.seek(0)  # Move the cursor to the start of the file

    # Provide a download link for the PDF using Streamlit's download button
    st.download_button(
        label="Download the guide as PDF",
        data=pdf_output,
        file_name="How_to_Use_Salesforce_App.pdf",
        mime="application/pdf"
    )

# Call the function in your main app
show_how_to_use()
