import os
from dotenv import load_dotenv
import requests
from utils.jwt_utils import JWTUtils


load_dotenv()

class MiningEnginerService:

    ORS_API_KEY = os.getenv("ORS_API_KEY")
    
    @staticmethod
    def update_miningOwner_appointment(token,issue_id,update_data):
        try:
            REDMINE_URL = os.getenv("REDMINE_URL")
            API_KEY = JWTUtils.get_api_key_from_token(token)

            if not REDMINE_URL or not API_KEY:
                return None, "Redmine URL or API Key is missing"
            
            payload = {
            "issue": {
                "status_id": update_data.get("status_id", 31),  # Default status ID
                #"description": appointment_data.get("description", ""),
                "due_date": update_data.get("due_date" ), 
                }
            }

            headers = {
            "Content-Type": "application/json",
            "X-Redmine-API-Key": API_KEY
            }

            response = requests.put(
            f"{REDMINE_URL}/issues/{issue_id}.json",
            json=payload,
            headers=headers
            )

            if response.status_code == 201:
                return response.json(), None
            else:
                error_msg = f"Failed to create appointment. Status: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f", Error: {error_data.get('errors', 'Unknown error')}"
                except:
                    error_msg += f", Response: {response.text}"
                return None, error_msg

        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
        
