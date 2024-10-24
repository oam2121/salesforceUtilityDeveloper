import streamlit as st
import pandas as pd
from salesforce_api import describe_object
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def show_describe_object(sf):
    st.subheader("Describe Salesforce Object")
    object_name = st.text_input("Enter Salesforce Object API Name (e.g., Account)")
    if st.button("Describe Object"):
        result = describe_object(sf, object_name)
        if result['success']:
            fields = result['fields']
            df = pd.DataFrame(fields)
            st.dataframe(df)
            generate_pdf(df)
        else:
            st.error(f"Failed to describe object: {result['message']}")

def generate_pdf(df):
    pdf_path = "salesforce_object_description.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    elements = []
    
    data = [df.columns.to_list()] + df.values.tolist()
    t = Table(data)
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                           ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                           ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                           ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                           ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(t)
    doc.build(elements)
    
    with open(pdf_path, "rb") as f:
        st.download_button(
            label="Download Data as PDF",
            data=f.read(),
            file_name=pdf_path,
            mime='application/pdf'
        )

