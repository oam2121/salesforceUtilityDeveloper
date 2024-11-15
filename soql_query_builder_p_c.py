import streamlit as st
import pandas as pd
from simple_salesforce import Salesforce

def show_advanced_soql_query_builder(sf):
    st.title("Advanced SOQL Query Builder with Parent-Child Relationship")

    # Fetching Salesforce objects
    try:
        sobjects = sf.describe()['sobjects']
        object_names = [obj['name'] for obj in sobjects if obj['queryable']]
    except Exception as e:
        st.error(f"Failed to fetch objects: {e}")
        return

    # Initialize state for filters if not already done
    if 'parent_filters' not in st.session_state:
        st.session_state.parent_filters = []
    if 'child_filters' not in st.session_state:
        st.session_state.child_filters = {}

    # Parent Object Selection
    parent_object = st.selectbox("Select Parent Object", object_names)
    parent_fields, child_relationships, selected_parent_fields = [], {}, []
    selected_child_fields, child_order_by, child_limits = {}, {}, {}
    parent_field_details = {}
    summary_mode = st.checkbox("Display as Summary Table")

    if parent_object:
        try:
            # Describe parent object
            parent_description = sf.__getattr__(parent_object).describe()
            parent_field_details = {field['name']: field for field in parent_description['fields']}
            parent_fields = list(parent_field_details.keys())

            # Gather child relationships for potential subqueries
            child_relationships = {
                relationship['relationshipName']: relationship['childSObject']
                for relationship in parent_description['childRelationships']
                if relationship['relationshipName']
            }

            # Select fields from Parent Object
            selected_parent_fields = st.multiselect("Select Fields from Parent Object", parent_fields)

            # Parent filters section (optional)
            with st.expander("Parent Filters (Optional)"):
                st.subheader("Parent Filters")
                parent_filter_field = st.selectbox("Parent Filter Field", selected_parent_fields, key="parent_filter_field")
                if parent_filter_field:
                    field_type = parent_field_details[parent_filter_field]['type']
                    
                    # Check if the field is a picklist
                    if field_type == 'picklist':
                        picklist_values = [option['value'] for option in parent_field_details[parent_filter_field]['picklistValues']]
                        parent_filter_value = st.selectbox("Parent Filter Value", picklist_values, key="parent_filter_value")
                    else:
                        parent_filter_value = st.text_input("Parent Filter Value", key="parent_filter_value")

                parent_filter_operator = st.selectbox("Parent Filter Operator", ["=", ">", "<", "LIKE", "IN"], key="parent_filter_operator")
                if st.button("Add Parent Filter"):
                    if parent_filter_field and parent_filter_operator and parent_filter_value:
                        formatted_value = f"'{parent_filter_value}'" if field_type in ['string', 'picklist'] else parent_filter_value
                        st.session_state.parent_filters.append(f"{parent_filter_field} {parent_filter_operator} {formatted_value}")
                        st.write("Added Parent Filter:", st.session_state.parent_filters[-1])

                # Display current parent filters
                st.write("Current Parent Filters:")
                for f in st.session_state.parent_filters:
                    st.write(f)

            # Parent order and limit (optional)
            with st.expander("Parent Advanced Filters (Optional)"):
                st.subheader("Parent Advanced Filters")
                parent_order_by = st.selectbox("Parent Order By", selected_parent_fields, key="parent_order_by")
                parent_order_direction = st.selectbox("Order Direction", ["ASC", "DESC"], key="parent_order_direction")
                parent_limit = st.number_input("Parent Limit", min_value=1, value=100, key="parent_limit")

        except Exception as e:
            st.error(f"Failed to fetch fields for {parent_object}: {str(e)}")
            return

    # Child Relationships Section (optional)
    with st.expander("Child Relationships and Filters (Optional)"):
        st.subheader("Add Child Relationships (Subqueries)")

        if child_relationships:
            selected_child_relationship = st.selectbox("Select Child Relationship", list(child_relationships.keys()))
            
            if selected_child_relationship:
                child_object_name = child_relationships[selected_child_relationship]
                if selected_child_relationship not in st.session_state.child_filters:
                    st.session_state.child_filters[selected_child_relationship] = []

                try:
                    # Describe child object
                    child_description = sf.__getattr__(child_object_name).describe()
                    child_field_details = {field['name']: field for field in child_description['fields']}
                    child_fields = list(child_field_details.keys())

                    # Select fields from Child Object
                    selected_child_fields[selected_child_relationship] = st.multiselect(f"Select Fields from {child_object_name}", child_fields)

                    # Filters for child object
                    st.subheader(f"Filters for {child_object_name}")
                    child_filter_field = st.selectbox(f"Filter Field for {child_object_name}", selected_child_fields[selected_child_relationship], key="child_filter_field")
                    if child_filter_field:
                        child_field_type = child_field_details[child_filter_field]['type']
                        
                        # Check if the field is a picklist
                        if child_field_type == 'picklist':
                            child_picklist_values = [option['value'] for option in child_field_details[child_filter_field]['picklistValues']]
                            child_filter_value = st.selectbox(f"Filter Value for {child_object_name}", child_picklist_values, key="child_filter_value")
                        else:
                            child_filter_value = st.text_input(f"Filter Value for {child_object_name}", key="child_filter_value")

                    child_filter_operator = st.selectbox(f"Filter Operator for {child_object_name}", ["=", ">", "<", "LIKE", "IN"], key="child_filter_operator")
                    if st.button(f"Add Filter for {child_object_name}"):
                        if child_filter_field and child_filter_operator and child_filter_value:
                            formatted_child_value = f"'{child_filter_value}'" if child_field_type in ['string', 'picklist'] else child_filter_value
                            st.session_state.child_filters[selected_child_relationship].append(
                                f"{child_filter_field} {child_filter_operator} {formatted_child_value}"
                            )
                            st.write(f"Added Filter for {child_object_name}:", st.session_state.child_filters[selected_child_relationship][-1])

                    # Display current child filters
                    st.write("Current Filters for", child_object_name)
                    for f in st.session_state.child_filters[selected_child_relationship]:
                        st.write(f)

                    # Order by and limit for child
                    child_order_by[selected_child_relationship] = st.selectbox(f"Order By for {child_object_name}", selected_child_fields[selected_child_relationship], key="child_order_by")
                    child_order_direction = st.selectbox(f"Order Direction for {child_object_name}", ["ASC", "DESC"], key="child_order_direction")
                    child_limits[selected_child_relationship] = st.number_input(f"Limit for {child_object_name}", min_value=1, value=100, key="child_limit")

                except Exception as e:
                    st.error(f"Failed to fetch fields for {child_object_name}: {str(e)}")
                    return

    # Constructing the SOQL Query
    if st.button("Run Query"):
        if not selected_parent_fields:
            st.warning("Please select at least one field from the Parent Object.")
            return

        # Build query with parent fields
        parent_fields_str = ", ".join(selected_parent_fields)
        query = f"SELECT {parent_fields_str}"

        # Build child subqueries
        child_queries = []
        for child_relationship, fields in selected_child_fields.items():
            if fields:
                fields_str = ", ".join(fields)
                child_query = f"(SELECT {fields_str} FROM {child_relationship}"

                # Add child filters
                if st.session_state.child_filters[child_relationship]:
                    child_query += " WHERE " + " AND ".join(st.session_state.child_filters[child_relationship])

                # Add child order and limit
                if child_order_by.get(child_relationship):
                    child_query += f" ORDER BY {child_order_by[child_relationship]} {child_order_direction}"
                if child_limits.get(child_relationship):
                    child_query += f" LIMIT {child_limits[child_relationship]}"

                child_query += ")"
                child_queries.append(child_query)

        if child_queries:
            query += ", " + ", ".join(child_queries)

        query += f" FROM {parent_object}"

        # Add parent filters
        if st.session_state.parent_filters:
            query += " WHERE " + " AND ".join(st.session_state.parent_filters)

        # Add parent order and limit
        if parent_order_by:
            query += f" ORDER BY {parent_order_by} {parent_order_direction}"
        if parent_limit:
            query += f" LIMIT {parent_limit}"

        st.write("Constructed Query:", query)

        # Execute query
        try:
            results = sf.query_all(query)
            records = results['records']

            if summary_mode:
                flattened_data = []
                for record in records:
                    account_data = {field: record.get(field) for field in selected_parent_fields}
                    for child_relationship in selected_child_fields.keys():
                        if child_relationship in record and record[child_relationship]:
                            for child_record in record[child_relationship]['records']:
                                child_data = {f"{child_relationship}.{field}": child_record.get(field) for field in selected_child_fields[child_relationship]}
                                flattened_data.append({**account_data, **child_data})
                        else:
                            flattened_data.append(account_data)

                df = pd.DataFrame(flattened_data)
                st.dataframe(df)

            else:
                for record in records:
                    st.markdown(f"### Record: {record.get('Name', 'No Name')}")
                    account_data = {field: record.get(field) for field in selected_parent_fields}
                    for field, value in account_data.items():
                        st.write(f"**{field}:** {value}")

                    # Child data in expanders
                    for child_relationship in selected_child_fields.keys():
                        if child_relationship in record and record[child_relationship]:
                            st.markdown(f"**{child_relationship}**")
                            with st.expander(f"Show {child_relationship}"):
                                child_records = record[child_relationship]['records']
                                child_data = [
                                    {field: child_record.get(field) for field in selected_child_fields[child_relationship]}
                                    for child_record in child_records
                                ]
                                st.table(pd.DataFrame(child_data))
                        else:
                            st.write(f"No records found for {child_relationship}")

        except Exception as e:
            st.error(f"Failed to run query: {e}")


if __name__ == "__main__":
    # Initialize Salesforce connection
    sf = Salesforce(username='your_username', password='your_password', security_token='your_token')
    show_advanced_soql_query_builder(sf)
