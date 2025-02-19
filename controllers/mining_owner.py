from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required
from services.mining_owner_service import MLOwnerService

# Define the Blueprint for mining_owner
mining_owner_bp = Blueprint('mining_owner', __name__)

# GET route for /mining-licenses (already exists)
@mining_owner_bp.route('/mining-licenses', methods=['GET'])
# @role_required(['MLOwner'])
def get_mining_licenses():
    issues, error = MLOwnerService.mining_licenses()
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"mining_licenses": issues})

# POST route for /create-tpl
@mining_owner_bp.route('/create-tpl', methods=['POST'])
@role_required(['MLOwner'])
def create_tpl():
    try:
        # Check if the Authorization token is present in the request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization token is missing"}), 401
        
        # Check if the token starts with 'Bearer ' (you can also validate it further here if needed)
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid token format. Expected 'Bearer <token>'"}), 401
        
        # Extract the token from the header
        token = auth_header.split(' ')[1]

        # Now validate the token, you can add your custom token validation logic here
        # For simplicity, we will assume the token is valid if it's present
        if not token:  # You can add further validation logic here
            return jsonify({"error": "Invalid or missing token"}), 401

        # Get JSON data from the request
        data = request.get_json()
        print("Data received")
        print(data)

        # Check if data is valid
        if not data:
            return jsonify({"error": "No data provided in the request body"}), 400
        

        # Call the create_tpl method with the provided 'data'
        issue, error = MLOwnerService.create_tpl(data)

        if error:
            return jsonify({"error": error}), 400  # Return error message if something went wrong

        return jsonify({"issue": issue}), 200  # Return created issue if successful

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return server error message

# View tpl route
# GET route for /view-tpls
@mining_owner_bp.route('/view-tpls', methods=['GET'])
@role_required(['MLOwner'])
def view_tpls():
    try:
        # Check if the Authorization token is present in the request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization token is missing"}), 401
        
        # Check if the token starts with 'Bearer ' (you can also validate it further here if needed)
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid token format. Expected 'Bearer <token>'"}), 401
        
        # Extract the token from the header
        token = auth_header.split(' ')[1]

        # Now validate the token, you can add your custom token validation logic here
        # For simplicity, we will assume the token is valid if it's present
        if not token:  # You can add further validation logic here
            return jsonify({"error": "Invalid or missing token"}), 401

        # Fetch tpl data
        issues, error = MLOwnerService.view_tpls()

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"view_tpls": issues})

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return server error message
    
        # Put route for /update-ML
@mining_owner_bp.route('/update-ml/<int:issue_id>', methods=['PUT'])
@role_required(['MLOwner'])
def update_ml(issue_id):
    try:
        # Check if the Authorization token is present in the request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization token is missing"}), 401
        
        # Check if the token starts with 'Bearer ' (you can also validate it further here if needed)
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid token format. Expected 'Bearer <token>'"}), 401
        
        # Extract the token from the header
        token = auth_header.split(' ')[1]

        # Now validate the token, you can add your custom token validation logic here
        # For simplicity, we will assume the token is valid if it's present
        if not token:  # You can add further validation logic here
            return jsonify({"error": "Invalid or missing token"}), 401

        # Get JSON data from the request
        data = request.get_json()
        

        # Check if data is valid
        # if not data:
        #     return jsonify({"error": "No data provided in the request body"}), 400
        if not data or "issue" not in data:
            return jsonify({"error": "No valid issue detail provided"}), 400
        
        print(data)

        # Call the create_tpl method with the provided 'data'
        # issue, error = MLOwnerService.create_tpl(data)
        updated_issue, error = MLOwnerService.update_issue(issue_id, data)

        if error:
            return jsonify({"error": error}), 400  # Return error message if something went wrong

        return jsonify({"message": "Issue updated successfully", "updated_issue": updated_issue}), 200 # Return created issue if successful

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return server error message


