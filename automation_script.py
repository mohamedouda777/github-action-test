import requests
import os

# Azure AD app credentials (replace with environment variables or secure storage)
CLIENT_ID = os.getenv('CLIENT_ID')
TENANT_ID = os.getenv('TENANT_ID')

# User credentials
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

# Power BI settings
WORKSPACE_ID = os.getenv('WORKSPACE_ID')
PBIX_FILE_PATH = 'uploaded_files/report11.pbix'  # Update with the actual path
DATASET_NAME = 'Your Dataset Name'  # Replace with your dataset name

# Authenticate and get an access token using ROPC flow
def get_access_token():
    url = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': CLIENT_ID,
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
    url = f'https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/imports?datasetDisplayName={DATASET_NAME}&nameConflict=Overwrite'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    try:
        with open(PBIX_FILE_PATH, 'rb') as pbix_file:
            files = {
                'file': pbix_file
            }
            response = requests.post(url, headers=headers, files=files)
            print("Publish request status code:", response.status_code)
            print("Response headers:", response.headers)
            print("Response text:", response.text)
            response.raise_for_status()
            print('Published the Power BI model successfully.')
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
    # Check if environment variables are loaded correctly
    if not all([CLIENT_ID, TENANT_ID, USERNAME, PASSWORD, WORKSPACE_ID, PBIX_FILE_PATH]):
        print("One or more environment variables are missing. Please ensure all required variables are set.")
        return

    access_token = get_access_token()
    publish_pbix(access_token)

if __name__ == '__main__':
    main()
