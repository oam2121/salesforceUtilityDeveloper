import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.units import inch
from datetime import datetime
import base64


def fetch_scheduled_jobs(sf):
    """Fetch scheduled jobs from Salesforce, including the 'Created By' information."""
    query = """
        SELECT Id, CronJobDetail.Name, State, NextFireTime, CreatedBy.Name 
        FROM CronTrigger
    """
    jobs = sf.query_all(query)['records']
    return jobs


def export_data_as_pdf(df):
    """Export DataFrame to PDF with a clean table format, including Created By and timestamp."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    # Define a basic style sheet
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title = Paragraph("Scheduled Jobs Report", styles['Title'])
    elements.append(title)

    # Table Data with "Created By" field
    data = [['Job Name', 'State', 'NextFireTime', 'Created By']]

    for i, row in df.iterrows():
        data.append([row['Job Name'], row['State'], row['NextFireTime'], row['CreatedBy']])

    # Create the table
    table = Table(data)

    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)

    # Append the table to elements
    elements.append(table)

    # Get current date and time
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Add timestamp at the end of the PDF
    timestamp_data = [['Report Generated On:', timestamp]]
    timestamp_table = Table(timestamp_data, colWidths=[2.5 * inch, 2.5 * inch])

    # Style the timestamp table
    timestamp_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    timestamp_table.setStyle(timestamp_style)

    # Append timestamp to elements
    elements.append(Paragraph("<br/><br/>", styles['Normal']))  # Add some space before the timestamp
    elements.append(timestamp_table)

    # Build the PDF
    doc.build(elements)

    # Get the value of the BytesIO buffer and encode it for download
    buffer.seek(0)
    b64 = base64.b64encode(buffer.getvalue()).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="scheduled_jobs_report.pdf">Download PDF File</a>'
    st.markdown(href, unsafe_allow_html=True)


def view_scheduled_jobs(sf):
    st.subheader("Scheduled Jobs Viewer")
    jobs = fetch_scheduled_jobs(sf)

    if jobs:
        df = pd.DataFrame(jobs)

        # Extracting nested fields for display and export
        df['Job Name'] = df.apply(lambda x: x['CronJobDetail']['Name'], axis=1)
        df['CreatedBy'] = df.apply(lambda x: x['CreatedBy']['Name'], axis=1)

        st.dataframe(df[['Job Name', 'State', 'NextFireTime', 'CreatedBy']])

        # Option to export the data
        st.subheader("Export Data")
        export_format = st.selectbox("Select Export Format", ["PDF", "Excel", "CSV"])

        if st.button("Export Data"):
            if export_format == "PDF":
                export_data_as_pdf(df[['Job Name', 'State', 'NextFireTime', 'CreatedBy']])
            elif export_format == "Excel":
                # Export to Excel
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df[['Job Name', 'State', 'NextFireTime', 'CreatedBy']].to_excel(writer, index=False)
                    writer.save()

                st.download_button(
                    label="Download Excel File",
                    data=buffer,
                    file_name="scheduled_jobs_report.xlsx",
                    mime="application/vnd.ms-excel"
                )
            elif export_format == "CSV":
                csv = df[['Job Name', 'State', 'NextFireTime', 'CreatedBy']].to_csv(index=False)
                st.download_button(
                    label="Download CSV File",
                    data=csv,
                    file_name="scheduled_jobs_report.csv",
                    mime="text/csv"
                )
    else:
        st.error("No scheduled jobs found.")
