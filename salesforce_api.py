import pandas as pd
from simple_salesforce import Salesforce

def retrieve_records(sf, soql_query):
    """Retrieve records using a SOQL query."""
    try:
        results = sf.query(soql_query)
        return results['records']
    except Exception as e:
        print(f"Error retrieving records: {str(e)}")
        return []

def create_record(sf, sobject, data):
    """Create a record in a Salesforce object."""
    try:
        result = sf.__getattr__(sobject).create(data)
        return {'success': True, 'id': result.get('id'), 'message': 'Record created successfully.'}
    except Exception as e:
        print(f"Error creating record: {str(e)}")
        return {'success': False, 'message': str(e)}

def update_record(sf, sobject, record_id, data):
    """Update a Salesforce record."""
    try:
        result = sf.__getattr__(sobject).update(record_id, data)
        return {'success': True, 'message': 'Record updated successfully.'}
    except Exception as e:
        print(f"Error updating record: {str(e)}")
        return {'success': False, 'message': str(e)}

def delete_record(sf, sobject, record_id):
    """Delete a Salesforce record."""
    try:
        result = sf.__getattr__(sobject).delete(record_id)
        return {'success': True, 'message': 'Record deleted successfully.'}
    except Exception as e:
        print(f"Error deleting record: {str(e)}")
        return {'success': False, 'message': str(e)}

def get_object_fields(sf, object_name):
    """Fetch metadata for a Salesforce object."""
    try:
        object_description = sf.__getattr__(object_name).describe()
        return {'success': True, 'fields': object_description['fields'], 'message': 'Object described successfully.'}
    except Exception as e:
        print(f"Error describing object: {str(e)}")
        return {'success': False, 'message': str(e)}

def import_csv_to_salesforce(sf, sobject_type, file_path):
    """Import data from a CSV file into Salesforce."""
    try:
        df = pd.read_csv(file_path)
        records = df.to_dict('records')
        for record in records:
            sf.__getattr__(sobject_type).create(record)
        return True, "Import successful."
    except Exception as e:
        print(f"Error importing CSV to Salesforce: {str(e)}")
        return False, str(e)

def export_salesforce_to_csv(sf, soql_query, file_path):
    """Export data from Salesforce to a CSV file."""
    try:
        records = sf.query(soql_query)['records']
        df = pd.DataFrame(records)
        df.to_csv(file_path, index=False)
        return True, "Export successful."
    except Exception as e:
        print(f"Error exporting Salesforce data to CSV: {str(e)}")
        return False, str(e)

def export_salesforce_to_excel(sf, soql_query, file_path):
    """Export data from Salesforce to an Excel file."""
    try:
        records = sf.query(soql_query)['records']
        df = pd.DataFrame(records)
        df.to_excel(file_path, index=False)
        return True, "Export successful."
    except Exception as e:
        print(f"Error exporting Salesforce data to Excel: {str(e)}")
        return False, str(e)

def describe_object(sf, object_name):
    """
    Fetch and return the description of a Salesforce object including its fields.

    Args:
    sf (Salesforce): An authenticated Salesforce session.
    object_name (str): API name of the Salesforce object to describe.

    Returns:
    dict: A dictionary containing success status, fields of the object if successful, and an error message if not.
    """
    try:
        description = sf.__getattr__(object_name).describe()
        fields = description['fields']
        clean_fields = [{
            'label': field['label'],
            'name': field['name'],
            'type': field['type'],
            'updateable': field['updateable'],
            'nillable': field['nillable']
        } for field in fields]

        return {
            'success': True,
            'fields': clean_fields,
            'message': 'Object described successfully.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f"Failed to describe object {object_name}: {str(e)}"
        }
