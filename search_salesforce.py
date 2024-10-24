import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer
from reportlab.lib import colors

def show_search_salesforce(sf):
    st.subheader("Search Salesforce using SOSL")
    search_query = st.text_area("Enter SOSL Query (e.g., FIND {Test} IN ALL FIELDS RETURNING Account(Name))", "FIND {Test} IN ALL FIELDS RETURNING Account(Name)")
    if st.button("Run Search"):
        results = search_salesforce(sf, search_query)
        if results['success']:
            if results['records']:
                df = pd.DataFrame([{'Type': rec.get('attributes', {}).get('type', 'N/A'), 
                                    'Name': rec.get('Name', 'N/A'), 
                                    'Id': rec.get('Id', 'N/A')} for rec in results['records']])
                st.dataframe(df)
                export_buttons(df)
            else:
                st.warning("No records found.")
        else:
            st.error(f"Search failed: {results['message']}")

def export_buttons(df):
    st.write("Export Results:")
    pdf = generate_pdf(df)
    csv = df.to_csv(index=False).encode('utf-8')
    excel = generate_excel(df)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button("Download as PDF", data=pdf, file_name="salesforce_results.pdf", mime="application/pdf")
    with col2:
        st.download_button("Download as CSV", data=csv, file_name="salesforce_results.csv", mime="text/csv")
    with col3:
        st.download_button("Download as Excel", data=excel, file_name="salesforce_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def generate_pdf(df):
    """Generate a PDF file from a DataFrame."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    data = [df.columns.to_list()] + df.values.tolist()
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(t)
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf

def generate_excel(df):
    """Generate an Excel file from a DataFrame."""
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    return output.getvalue()

def search_salesforce(sf, sosl_query):
    """Search Salesforce using SOSL (Salesforce Object Search Language)."""
    try:
        results = sf.search(sosl_query)
        if 'searchRecords' in results and len(results['searchRecords']) > 0:
            return {'success': True, 'records': results['searchRecords']}
        else:
            return {'success': True, 'records': [], 'message': 'No records found'}
    except Exception as e:
        return {'success': False, 'message': str(e)}
