import requests
import os

# Azure AD app credentials (replace with environment variables or secure storage)
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID')

# Power BI settings
WORKSPACE_ID = os.getenv('WORKSPACE_ID')
PBIX_FILE_PATH = 'uploaded_files/report11.pbix'  # Update with the actual path
DATASET_NAME = 'report11'

# Authenticate and get an access token
def get_access_token():
    url = f'https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'client_id': CLIENT_ID,
        'scope': 'https://analysis.windows.net/powerbi/api/.default',
        'client_secret': CLIENT_SECRET,
        'grant_type': 'client_credentials'
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    access_token = response.json().get('access_token')
    return access_token

# Publish the .pbix file
def publish_pbix(access_token):
    url = f'https://api.powerbi.com/v1.0/myorg/groups/{WORKSPACE_ID}/imports?datasetDisplayName={DATASET_NAME}&nameConflict=Overwrite'
    headers = {
        'Authorization': f'Bearer {access_token}'
    }
    with open(PBIX_FILE_PATH, 'rb') as pbix_file:
        files = {
            'file': pbix_file
        }
        response = requests.post(url, headers=headers, files=files)
        response.raise_for_status()
        print('Published the Power BI model successfully.')

def main():
    access_token = get_access_token()
    publish_pbix(access_token)

if __name__ == '__main__':
    main()
