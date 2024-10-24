import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
from simple_salesforce import Salesforce, SalesforceMalformedRequest

# Function to filter out unnecessary metadata fields from Salesforce fields
def filter_out_metadata_fields(fields):
    """Filter out unnecessary metadata fields from the Salesforce fields."""
    return [field for field in fields if not field.startswith('attributes') and not field.startswith('Opportunities.')]

# Function to generate the SOQL filter query based on filter conditions
def generate_filter_query(filter_conditions, numeric_fields):
    """Generate the SOQL filter query based on filter conditions."""
    filter_query = ""
    for condition in filter_conditions:
        obj_field = condition['field'].split('.')[1]  # Remove object prefix
        filter_type = condition['operator']
        value = condition['value']
        
        # Determine if the field is numeric
        is_numeric = obj_field in numeric_fields

        if filter_type == "equals":
            if is_numeric:
                filter_query += f"{obj_field} = {value} AND "
            else:
                filter_query += f"{obj_field} = '{value}' AND "
        elif filter_type == "greater than":
            if is_numeric:
                filter_query += f"{obj_field} > {value} AND "
            else:
                filter_query += f"{obj_field} > '{value}' AND "
        elif filter_type == "less than":
            if is_numeric:
                filter_query += f"{obj_field} < {value} AND "
            else:
                filter_query += f"{obj_field} < '{value}' AND "
        elif filter_type == "between" and isinstance(value, tuple):
            if is_numeric:
                filter_query += f"{obj_field} >= {value[0]} AND {obj_field} <= {value[1]} AND "
            else:
                filter_query += f"{obj_field} >= '{value[0]}' AND {obj_field} <= '{value[1]}' AND "

    # Remove the trailing 'AND ' if filters exist
    if filter_query.endswith("AND "):
        filter_query = filter_query[:-4]

    return filter_query

def ensure_group_by(fields, group_by_fields, numeric_fields=None):
    """Ensure all selected fields are either grouped or aggregated."""
    cleaned_fields = []
    for field in fields:
        # Check if the field contains a period (object.field) format
        if '.' in field:
            obj_field = field.split('.')[1]  # Remove object prefix
        else:
            obj_field = field  # Field without an object prefix

        cleaned_fields.append(obj_field)

    return list(set(cleaned_fields + group_by_fields))



# Function to identify numeric fields for a given Salesforce object
def get_numeric_fields(sf, object_name):
    """Retrieve numeric fields for a given Salesforce object."""
    object_description = sf.__getattr__(object_name).describe()
    numeric_fields = [field['name'] for field in object_description['fields'] if field['type'] in ['currency', 'double', 'int', 'percent']]
    return numeric_fields

# Main visualization function
def visualize_data(sf):
    st.subheader("Salesforce Reports and Dashboards")

    # Initialize session state variables if they don't exist
    if 'soql_query' not in st.session_state:
        st.session_state['soql_query'] = ""
    if 'records' not in st.session_state:
        st.session_state['records'] = None

    # Step 1: Select objects and their fields
    st.write("**Step 1: Select Salesforce Objects and Fields**")
    
    # Fetch and display Salesforce objects
    try:
        objects = sf.describe()["sobjects"]
    except Exception as e:
        st.error(f"Error fetching Salesforce objects: {str(e)}")
        return

    object_names = [obj["name"] for obj in objects]
    
    # Allow the user to select a single object for simplicity (Salesforce SOQL typically operates on single objects)
    selected_object = st.selectbox("Select Object", object_names)
    
    if not selected_object:
        st.warning("Please select a Salesforce object to proceed.")
        return

    # Retrieve fields for the selected object
    try:
        object_description = sf.__getattr__(selected_object).describe()
        fields = [field['name'] for field in object_description['fields']]
        filtered_fields = filter_out_metadata_fields(fields)
    except Exception as e:
        st.error(f"Error fetching fields for {selected_object}: {str(e)}")
        return

    # Identify numeric fields for aggregation
    numeric_fields = get_numeric_fields(sf, selected_object)

    # Allow the user to select fields
    selected_fields = st.multiselect(f"Select fields from {selected_object}", filtered_fields, key=f"{selected_object}_fields")
    
    if not selected_fields:
        st.warning("Please select at least one field to proceed.")
        return

    # Step 2: Apply Filters
    st.write("**Step 2: Apply Filters**")
    
    filter_conditions = []
    filter_count = st.number_input("Number of Filters", min_value=0, max_value=5, value=0, step=1)
    
    for i in range(filter_count):
        field = st.selectbox(f"Filter Field {i + 1}", [f"{selected_object}.{field}" for field in selected_fields], key=f"filter_field_{i}")
        operator = st.selectbox(f"Condition Type {i + 1}", ["equals", "greater than", "less than", "between"], key=f"filter_operator_{i}")
        
        # Determine if the field is numeric
        field_name = field.split('.')[1]  # Remove object prefix
        is_numeric = field_name in numeric_fields

        if operator == "between":
            if is_numeric:
                value1 = st.number_input(f"Value 1 for {field} (numeric)", key=f"filter_value1_{i}")
                value2 = st.number_input(f"Value 2 for {field} (numeric)", key=f"filter_value2_{i}")
                filter_conditions.append({"field": field, "operator": operator, "value": (value1, value2)})
            else:
                value1 = st.text_input(f"Value 1 for {field}", key=f"filter_value1_{i}")
                value2 = st.text_input(f"Value 2 for {field}", key=f"filter_value2_{i}")
                filter_conditions.append({"field": field, "operator": operator, "value": (value1, value2)})
        else:
            if is_numeric:
                value = st.number_input(f"Value for {field} (numeric)", key=f"filter_value_{i}")
            else:
                value = st.text_input(f"Value for {field}", key=f"filter_value_{i}")
            filter_conditions.append({"field": field, "operator": operator, "value": value})
    
    # Date Filter (Optional)
    st.write("**Date Filters (Optional)**")
    date_fields = [f"{selected_object}.{field}" for field in selected_fields if "Date" in field]
    if date_fields:
        date_field = st.selectbox("Select Date Field for Filtering", date_fields, key="date_field_filter")
        if date_field:
            date_range = st.date_input("Select Date Range", value=(datetime.now(), datetime.now()), key="date_range")
            if len(date_range) == 2:
                start_date = date_range[0].strftime('%Y-%m-%d')
                end_date = date_range[1].strftime('%Y-%m-%d')
                filter_conditions.append({
                    'field': date_field,
                    'operator': 'between',
                    'value': (start_date, end_date)
                })
    else:
        st.info("No date fields available for filtering.")

    # Step 3: Group By and Aggregations
    st.write("**Step 3: Group By**")
    group_by_fields = st.multiselect("Group By", [f"{selected_object}.{field}" for field in selected_fields if field in numeric_fields or field not in numeric_fields], key="group_by_fields")
    
    # Step 4: Generate SOQL Query
    if st.button("Generate Report"):
        if selected_fields:
            # Prepare fields for SELECT clause
            aggregated_fields = ensure_group_by(selected_fields, group_by_fields, numeric_fields)
            
            # Clean field names by removing object prefix
            clean_aggregated_fields = [field.split('.')[1] if '.' in field else field for field in aggregated_fields]
            
            soql_select = ', '.join(clean_aggregated_fields)
            soql_from = selected_object
            
            # Generate filter query
            soql_where = generate_filter_query(filter_conditions, numeric_fields)
            
            # Generate GROUP BY clause
            if group_by_fields:
                clean_group_by_fields = [field.split('.')[1] for field in group_by_fields]
                soql_group_by = ', '.join(clean_group_by_fields)
                soql_query = f"SELECT {soql_select} FROM {soql_from} WHERE {soql_where} GROUP BY {soql_group_by} LIMIT 200"
            else:
                soql_query = f"SELECT {soql_select} FROM {soql_from} WHERE {soql_where} LIMIT 200"
            
            # Display the generated SOQL query
            st.write(f"**Generated SOQL Query:**\n```sql\n{soql_query}\n```")
            st.session_state['soql_query'] = soql_query
        else:
            st.error("Please select at least one field to generate the report.")
    
    # Step 5: Fetch and Display Report
    if 'soql_query' in st.session_state and st.session_state['soql_query']:
        soql_query = st.session_state['soql_query']
        
        if st.button("Run Query"):
            try:
                results = sf.query(soql_query)
                records = results.get('records', [])
                if records:
                    df = pd.json_normalize(records)
                    st.session_state['records'] = df
                    st.success(f"Query successful. {len(df)} records fetched.")
                    st.write(df)
                else:
                    st.error("No records returned.")
                    st.session_state['records'] = None
            except SalesforceMalformedRequest as e:
                st.error(f"Malformed SOQL Query: {str(e)}")
                st.session_state['records'] = None
            except Exception as e:
                st.error(f"Failed to execute query: {str(e)}")
                st.session_state['records'] = None
    
    # Step 6: Visualization
    if 'records' in st.session_state and st.session_state['records'] is not None:
        df = st.session_state['records']
        
        st.write("**Step 6: Data Visualization**")
        chart_type = st.selectbox("Select Chart Type", ['Bar Chart', 'Pie Chart', 'Line Chart'], key="chart_type_visual")
        st.write("Choose fields for visualization:")
        
        if chart_type == 'Bar Chart':
            x_axis = st.selectbox("Select X-Axis", df.columns, key="bar_x_axis")
            y_axis = st.selectbox("Select Y-Axis", df.columns, key="bar_y_axis")
            if x_axis and y_axis:
                fig = px.bar(df, x=x_axis, y=y_axis, title=f"{y_axis} by {x_axis}")
                st.plotly_chart(fig)
        
        elif chart_type == 'Pie Chart':
            labels = st.selectbox("Select Labels", df.columns, key="pie_labels")
            numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns.tolist()
            if numeric_columns:
                values = st.selectbox("Select Values", numeric_columns, key="pie_values")
                if labels and values:
                    fig = px.pie(df, names=labels, values=values, title=f"Distribution of {values} by {labels}")
                    st.plotly_chart(fig)
            else:
                st.error("No numeric fields available for Pie Chart values.")
        
        elif chart_type == 'Line Chart':
            x_axis = st.selectbox("Select X-Axis", df.columns, key="line_x_axis")
            y_axis = st.selectbox("Select Y-Axis", df.columns, key="line_y_axis")
            if x_axis and y_axis:
                fig = px.line(df, x=x_axis, y=y_axis, title=f"{y_axis} over {x_axis}")
                st.plotly_chart(fig)
    else:
        st.info("No data available for visualization. Please generate and run a report.")

# Main function to run the Streamlit app
def main():
    st.title("Salesforce Reporting and Dashboard Tool")
    
    # Connect to Salesforce
    st.sidebar.header("Salesforce Connection")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    security_token = st.sidebar.text_input("Security Token", type="password")
    domain = st.sidebar.selectbox("Domain", ["login", "test"], index=0)
    
    if st.sidebar.button("Connect to Salesforce"):
        try:
            sf = Salesforce(username=username, password=password, security_token=security_token, domain=domain)
            st.success("Successfully connected to Salesforce!")
            visualize_data(sf)
        except Exception as e:
            st.error(f"Failed to connect to Salesforce: {str(e)}")
    else:
        st.info("Enter your Salesforce credentials to connect.")

if __name__ == "__main__":
    main()
