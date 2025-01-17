import os
import requests
import sys

# Azure AD app credentials
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID')

# Service account credentials
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# Power BI settings
WORKSPACE_ID = os.getenv('WORKSPACE_ID')
PBIX_FILE_PATH = os.getenv('PBIX_FILE_PATH')  # Path to the .pbix file

# Function to check for missing environment variables and provide debug output
def check_env_variables():
    missing_vars = []
    required_vars = {
        'CLIENT_ID': CLIENT_ID,
        'CLIENT_SECRET': CLIENT_SECRET,
        'TENANT_ID': TENANT_ID,
        'USERNAME': USERNAME,
        'PASSWORD': PASSWORD,
        'WORKSPACE_ID': WORKSPACE_ID,
        'PBIX_FILE_PATH': PBIX_FILE_PATH
    }
    
    for var_name, var_value in required_vars.items():
        if not var_value:
            missing_vars.append(var_name)
            print(f"[ERROR] Missing environment variable: {var_name}")

    if missing_vars:
        print("Please ensure all required environment variables are set.")
        sys.exit(1)

# Authenticate and get an access token using ROPC flow
def get_access_token():
    url = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'scope': 'https://analysis.windows.net/powerbi/api/.default',
        'grant_type': 'password',
        'username': USERNAME,
        'password': PASSWORD
    }
    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        access_token = response.json().get('access_token')
        print("Access token retrieved successfully.")
        return access_token
    except requests.exceptions.HTTPError as e:
        print("Failed to retrieve access token:")
        print("Status Code:", e.response.status_code)
        print("Response:", e.response.text)
        raise

# Publish the .pbix file to Power BI
def publish_pbix(access_token):
    if not PBIX_FILE_PATH or not os.path.exists(PBIX_FILE_PATH):
        print(f"[ERROR] PBIX file not found at specified path: {PBIX_FILE_PATH}")
        sys.exit(1)

    url = f'https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/imports?datasetDisplayName={os.path.basename(PBIX_FILE_PATH)}&nameConflict=CreateOrOverwrite'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    try:
        with open(PBIX_FILE_PATH, 'rb') as pbix_file:
            files = {
                'file': pbix_file
            }
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            print('Published the Power BI report successfully.')
    except requests.exceptions.HTTPError as e:
        print("Failed to publish the .pbix file:")
        print("Status Code:", e.response.status_code)
        print("Response:", e.response.text)
        raise
    except FileNotFoundError:
        print("File not found. Please check the PBIX_FILE_PATH.")
    except Exception as e:
        print("An unexpected error occurred:", str(e))

def main():
    print("Starting Power BI publish process...")
    # Check that all required environment variables are set
    check_env_variables()

    # Get the access token
    access_token = get_access_token()
    if access_token:
        publish_pbix(access_token)
    else:
        print("Failed to obtain access token.")

if __name__ == '__main__':
    main()
