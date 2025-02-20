import jwt
import os

class MLOUtils:
    @staticmethod
    def get_user_info_from_token(token):
        """Decode and extract user info from the JWT token."""
        try:
            secret_key = os.getenv("SECRET_KEY")
            if not secret_key:
                return None, "SECRET_KEY is not set in the environment variables"

            token = jwt.decode(token, secret_key, algorithms=[os.getenv("JWT_ALGORITHM")])
            print(f"Decoded token: {token}")  # Debugging: Print decoded token
            user_id = token.get("user_id")
            print(f"User ID from token: {user_id}")  # Debugging: Print user ID from token

            if not user_id:
                return None, "User ID not found in the token"

            return user_id, None  # Return the user_id with no error

        except jwt.ExpiredSignatureError:
            return None, "Token has expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
        except Exception as e:
            return None, f"Error decoding token: {str(e)}"

    @staticmethod
    def issue_belongs_to_user(issue, user_id):
        """
        Check if the issue belongs to the specified user_id.
        This checks the 'assigned_to' field instead of custom fields.
        """
        user_id = str(user_id[0]) if isinstance(user_id, list) else str(user_id)  # Ensure user_id is a string

        # Loop through issues and filter based on assigned_to ID
        assigned_to_id = str(issue.get('assigned_to', {}).get('id'))  # Ensure assigned_to_id is a string
        print(f"Checking Issue {issue.get('id')} - Assigned to ID: {assigned_to_id}, User ID: {user_id}")  # Debugging: Print IDs

        if assigned_to_id == user_id:  # Compare with user_id from token
            return True
        
        return False  # Return False if user_id is not found or doesn't match
