import requests
from simple_salesforce import Salesforce, SalesforceLogin

def authenticate_salesforce_with_user(user_data):
    """
    Authenticate with Salesforce using provided user credentials.
    
    Args:
    user_data (dict): A dictionary containing Salesforce login credentials which includes
                      username, password, security_token, client_id, client_secret, and domain.
    
    Returns:
    Salesforce object if authentication is successful, None otherwise.
    """
    try:
        # Attempt to authenticate using simple_salesforce's built-in function
        sf = Salesforce(
            username=user_data['username'],
            password=user_data['password'],
            security_token=user_data['security_token'],
            domain=user_data['domain']
        )
        return sf
    except Exception as e:
        # Fallback to manual authentication if the first method fails
        print(f"Automatic Salesforce authentication failed: {str(e)}. Attempting manual authentication...")
        return manual_authenticate_salesforce(user_data)

def manual_authenticate_salesforce(user_data):
    """
    Manually authenticate with Salesforce by constructing the request for an access token.
    
    Args:
    user_data (dict): A dictionary containing Salesforce login credentials which includes
                      username, password, security_token, client_id, client_secret, and domain.
    
    Returns:
    Salesforce object if authentication is successful, None otherwise.
    """
    token_url = f"https://{user_data['domain']}.salesforce.com/services/oauth2/token"
    payload = {
        'grant_type': 'password',
        'client_id': user_data['client_id'],
        'client_secret': user_data['client_secret'],
        'username': user_data['username'],
        'password': f"{user_data['password']}{user_data['security_token']}"
    }
    
    try:
        response = requests.post(token_url, data=payload)
        response.raise_for_status()  # Will raise an HTTPError for bad requests
        access_info = response.json()
        sf_instance = Salesforce(instance_url=access_info['instance_url'], session_id=access_info['access_token'])
        return sf_instance
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred during manual authentication: {http_err}")
    except Exception as err:
        print(f"Other error occurred during manual authentication: {err}")

    return None
