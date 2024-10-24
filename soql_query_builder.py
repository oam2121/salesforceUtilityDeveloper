import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce
from st_aggrid import AgGrid

def show_soql_query_builder(sf):
    st.title("Advanced SOQL Query Builder")

    # Fetching Salesforce objects
    try:
        sobjects = sf.describe()['sobjects']
        object_names = [obj['name'] for obj in sobjects if obj['queryable']]
    except Exception as e:
        st.error(f"Failed to fetch objects: {e}")
        return

    # Selecting Salesforce object
    object_selected = st.selectbox("Select Salesforce Object", object_names, index=0)
    field_details = {}
    field_names = []
    parent_relationships = {}
    selected_fields = []

    if object_selected:
        try:
            object_description = sf.__getattr__(object_selected).describe()
            field_details = {field['name']: field for field in object_description['fields']}
            field_names = list(field_details.keys())

            # Parent relationship extraction
            parent_relationships = {
                field['relationshipName']: field['referenceTo'][0]
                for field in object_description['fields']
                if field.get('relationshipName') and 'referenceTo' in field
            }

            # Asking user if they want to add parent fields
            add_parent = st.checkbox("Do you want to add parent fields?")

            if add_parent and parent_relationships:
                parent_object = st.selectbox("Select Parent Object", list(parent_relationships.keys()))
                parent_object_name = parent_relationships[parent_object]

                # Fetching fields from the parent object
                parent_object_description = sf.__getattr__(parent_object_name).describe()
                parent_field_names = [f"{parent_object_name}.{field['name']}" for field in parent_object_description['fields']]

                # Displaying fields of the selected parent object
                selected_parent_fields = st.multiselect(f"Select Fields from {parent_object_name}", parent_field_names)
                selected_fields.extend(selected_parent_fields)

            # Selecting fields for the main query
            selected_child_fields = st.multiselect("Select Fields", field_names)
            selected_fields.extend(selected_child_fields)

        except Exception as e:
            st.error(f"Failed to fetch fields for {object_selected}: {str(e)}")
            return

    # Initialize filters in session state if not already done
    if 'filters' not in st.session_state:
        st.session_state.filters = []

    # Filters section
    with st.expander("Add Filters"):
        filter_field = st.selectbox("Field to Filter", selected_fields, key="filter_field")
        
        # Determine if the selected field is a picklist and fetch its values if so
        if filter_field and field_details[filter_field]['type'] == 'picklist':
            picklist_values = [option['value'] for option in field_details[filter_field]['picklistValues']]
            value = st.selectbox("Value", picklist_values, key="value_select")
            operator = st.selectbox("Operator", ["=", "IN"], key="operator")  # Restricting operators for picklists
        else:
            operator = st.selectbox("Operator", ["=", ">", "<", "LIKE", "IN"], key="operator")
            value = st.text_input("Value", key="value_text")

        if st.button("Add Filter"):
            if filter_field and operator and value:
                formatted_value = f"'{value}'" if field_details[filter_field]['type'] in ['string', 'picklist'] else value
                st.session_state.filters.append(f"{filter_field} {operator} {formatted_value}")
                st.success(f"Added filter: {filter_field} {operator} {formatted_value}")
            else:
                st.warning("Please fill all filter fields.")

    # Display current filters
    if st.session_state.filters:
        st.write("Current Filters:")
        for f in st.session_state.filters:
            st.write(f)

    # Advanced Filters
    with st.expander("Advanced Filters"):
        order_by_field = st.selectbox("Order By Field", selected_fields, key="order_by_field")
        order_direction = st.selectbox("Order Direction", ["ASC", "DESC"], key="order_direction")
        limit = st.number_input("Limit", min_value=1, value=100, step=1, key="limit")

    # Construct Query
    if st.button("Run Query"):
        query = f"SELECT {', '.join(selected_fields)} FROM {object_selected}"
        
        # Adding WHERE filters
        if st.session_state.filters:
            query += " WHERE " + " AND ".join(st.session_state.filters)
        
        # Adding ORDER BY and LIMIT clauses
        if order_by_field and order_by_field in selected_fields:
            query += f" ORDER BY {order_by_field} {order_direction} LIMIT {limit}"
        else:
            query += f" LIMIT {limit}"  # Default to just a limit if no valid order by

        st.write("Constructed Query:", query)

        # Execute Query
        try:
            results = sf.query_all(query)
            df = pd.DataFrame(results['records'])

            # Displaying Account names correctly
            for field in selected_fields:
                if 'Account.' in field:
                    df[field] = df.apply(lambda x: x['Account'].get(field.split('.')[1]) if isinstance(x['Account'], dict) else '', axis=1)

            AgGrid(df)
        except Exception as e:
            st.error(f"Failed to run query: {e}")

    if st.button("Clear Filters and Subqueries"):
        st.session_state.filters.clear()
        selected_fields.clear()

if __name__ == "__main__":
    sf = Salesforce(username='your_username', password='your_password', security_token='your_token')
    show_soql_query_builder(sf)
