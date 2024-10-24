import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import base64
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


def fetch_user_names(sf, user_ids):
    """Fetch user names based on the UserId."""
    formatted_ids = ",".join([f"'{user_id}'" for user_id in user_ids])
    query = f"SELECT Id, Name FROM User WHERE Id IN ({formatted_ids})"
    users = sf.query_all(query)['records']
    return {user['Id']: user['Name'] for user in users}


def fetch_login_history(sf):
    """Fetch login history from Salesforce."""
    query = """
    SELECT UserId, LoginTime, SourceIp, LoginType, Status
    FROM LoginHistory 
    ORDER BY LoginTime DESC LIMIT 100
    """
    login_history = sf.query_all(query)['records']
    
    # Extract UserIds and fetch their corresponding names
    user_ids = [record['UserId'] for record in login_history]
    user_names = fetch_user_names(sf, user_ids)

    # Replace UserId with User Name
    for record in login_history:
        record['UserName'] = user_names.get(record['UserId'], 'Unknown User')

    return login_history


def fetch_audit_logs(sf):
    """Fetch audit logs from Salesforce (Setup Audit Trail)."""
    query = """
    SELECT Action, CreatedDate, CreatedBy.Name 
    FROM SetupAuditTrail 
    ORDER BY CreatedDate DESC LIMIT 100
    """
    audit_logs = sf.query_all(query)['records']
    
    # Clean up the CreatedBy field to only show the Name
    for record in audit_logs:
        created_by_info = record.get('CreatedBy')
        if created_by_info:
            record['CreatedBy'] = created_by_info.get('Name')
        else:
            record['CreatedBy'] = 'None'

    return audit_logs


def export_data_as_pdf(df, title):
    """Export DataFrame to a clean PDF with proper formatting."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Styles
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(title, styles['Title']))

    # Table Data
    table_data = [list(df.columns)] + df.values.tolist()

    # Create Table
    table = Table(table_data)

    # Style Table
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    elements.append(table)

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    elements.append(Paragraph(f"<br/><br/><b>Report generated on:</b> {timestamp}", styles['Normal']))

    # Build PDF
    doc.build(elements)

    # Prepare file for download
    buffer.seek(0)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{title.replace(" ", "_").lower()}_report.pdf">Download PDF File</a>'
    st.markdown(href, unsafe_allow_html=True)


def view_audit_logs(sf):
    st.subheader("Audit Logs Viewer")

    log_type = st.selectbox("Select Log Type", ["Login History", "Audit Logs"])

    if log_type == "Audit Logs":
        logs = fetch_audit_logs(sf)
        title = "Audit Logs Report"
    else:
        logs = fetch_login_history(sf)
        title = "Login History Report"

    if logs:
        df = pd.DataFrame(logs)

        # Remove unnecessary columns
        if 'attributes' in df.columns:
            df = df.drop(columns=['attributes'])

        # Display DataFrame
        st.dataframe(df)

        # Export Options
        st.subheader("Export Data")
        export_format = st.selectbox("Select Export Format", ["PDF", "Excel", "CSV"])

        if st.button("Export Data"):
            if export_format == "PDF":
                export_data_as_pdf(df, title)
            elif export_format == "Excel":
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                    writer.save()
                st.download_button(
                    label="Download Excel File",
                    data=buffer,
                    file_name=f"{title.replace(' ', '_').lower()}_report.xlsx",
                    mime="application/vnd.ms-excel"
                )
            elif export_format == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV File",
                    data=csv,
                    file_name=f"{title.replace(' ', '_').lower()}_report.csv",
                    mime="text/csv"
                )
    else:
        st.error(f"No logs found for {log_type}.")
