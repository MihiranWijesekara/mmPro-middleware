from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required,check_token
from services.mining_owner_service import MLOwnerService

# Define the Blueprint for mining_owner
mining_owner_bp = Blueprint('mining_owner', __name__)

# GET route for /mining-licenses (already exists)(slt redmine server done)
@mining_owner_bp.route('/mining-licenses', methods=['GET'])
@check_token
@role_required(['MLOwner'])
def get_mining_licenses():
    try:
        # Extract token from the request headers
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            return {"error": "Authorization token is missing"}, 400
        
        # Remove the "Bearer " prefix if it exists
        token = auth_header.replace("Bearer ", "")
        
        if not token:
            return {"error": "Authorization token is invalid"}, 400
        
        # Call the mining_licenses method with the token
        issues, error = MLOwnerService.mining_licenses(token)
        
        if error:
            return {"error": error}, 500
        
        return {"issues": issues}, 200
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500

# POST route for /create-tpl 
# @mining_owner_bp.route('/create-tpl', methods=['POST'])
# @check_token
# @role_required(['MLOwner'])
# def create_tpl():
#     try:
#         # Check if the Authorization token is present in the request
#         auth_header = request.headers.get('Authorization')
#         if not auth_header:
#             return jsonify({"error": "Authorization token is missing"}), 401
        
#         # Check if the token starts with 'Bearer ' (you can also validate it further here if needed)
#         if not auth_header.startswith('Bearer '):
#             return jsonify({"error": "Invalid token format. Expected 'Bearer <token>'"}), 401
        
#         # Extract the token from the header
#         token = auth_header.split(' ')[1]

#         # Now validate the token, you can add your custom token validation logic here
#         # For simplicity, we will assume the token is valid if it's present
#         if not token:  # You can add further validation logic here
#             return jsonify({"error": "Invalid or missing token"}), 401

#         # Get JSON data from the request
#         data = request.get_json()
#         print("Data received")
#         print(data)

#         # Check if data is valid
#         if not data:
#             return jsonify({"error": "No data provided in the request body"}), 400
        

#         # Call the create_tpl method with the provided 'data'
#         issue, error = MLOwnerService.create_tpl(data, auth_header)

#         if error:
#             return jsonify({"error": error}), 400  # Return error message if something went wrong

#         return jsonify({"issue": issue}), 200  # Return created issue if successful

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500  # Return server error message


@mining_owner_bp.route('/create-tpl', methods=['POST'])
@check_token
@role_required(['MLOwner'])
def create_tpl():
    try:
        # Check if the Authorization token is present in the request
        token = request.headers.get('Authorization')

        # Get request data
        data = request.json

        # Call the service to create the TPL issue
        issue, error = MLOwnerService.create_tpl(data, token)

        if error:
            return jsonify({"error": error}), 400  # Return error message if something went wrong

        return jsonify(issue), 201  # Return created issue if successful

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return server error message
    
# View tpl route
# GET route for /view-tpls    http://127.0.0.1:5000/mining-owner/view-tpls?mining_license_number=LLL/100/100
@mining_owner_bp.route('/view-tpls', methods=['GET'])
@check_token
@role_required(['MLOwner'])
def view_tpl_by_license_number():
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

        # Get the mining_license_number from the query parameters
        mining_license_number = request.args.get('mining_license_number')

        # Fetch TPL data for the specific Mining License Number
        issues, error = MLOwnerService.view_tpls(token, mining_license_number)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"view_tpls": issues})

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return server error message

        
#done
@mining_owner_bp.route('/mining-homeLicenses', methods=['GET'])
@check_token
@role_required(['MLOwner'])
def mining_home():
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
        # Validate the token (for now, we simply check if it's present, but you can add further validation logic)
        if not token:
            return jsonify({"error": "Invalid or missing token"}), 401

        # If the token is valid, proceed with the mining_licenses logic
        issues, error = MLOwnerService.mining_homeLicenses(token) # Pass token here
        
        if error:
            return jsonify({"error": error}), 500

        return jsonify({"mining_home": issues})

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@mining_owner_bp.route('/ml-detail', methods=['GET'])
@check_token
@role_required(['MLOwner'])
def ml_detail():
    try:
        # Extract the 'l_number' query parameter
        l_number = request.args.get('l_number')
        if not l_number:
            return jsonify({"error": "Missing 'l_number' query parameter"}), 400

        # Extract the Authorization token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid or missing Authorization token"}), 401

        # Extract only the token value
        token = auth_header.split(' ')[1]

        # Call the service function with l_number and token
        issue, error = MLOwnerService.ml_detail(l_number, auth_header)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"ml_detail": issue})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

        
            # Put route for /update-ML
@mining_owner_bp.route('/user-detail/<int:user_id>', methods=['GET'])
@check_token
@role_required(['MLOwner'])
def user_detail(user_id):
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


        # Call the create_tpl method with the provided 'data'
        # issue, error = MLOwnerService.create_tpl(data)
        detail, error = MLOwnerService.user_detail(user_id, auth_header)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"user_detail": detail})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




















# achintha baranch publish