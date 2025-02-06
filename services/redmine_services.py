import requests
from config import Config

def get_redmine_issues():
    url = 'https://your-redmine-instance.com/api/v1/issues.json'
    headers = {'X-Redmine-API-Key': Config.REDMINE_API_KEY}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"message": "Failed to retrieve data from Redmine"}, response.status_code
