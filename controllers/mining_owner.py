from flask import Blueprint, jsonify,request
from middleware.auth_middleware import role_required
from services.mining_owner_service import MLOwnerService

# Define the Blueprint for mining_owner
mining_owner_bp = Blueprint('mining_owner', __name__)

# GET route for /mining-licenses (already exists)
@mining_owner_bp.route('/mining-licenses', methods=['GET'])
@role_required(['MLOwner'])
def get_mining_licenses():
    issues, error = MLOwnerService.mining_licenses()
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"mining_licenses": issues})


# POST route for /dispatch-tpl
@mining_owner_bp.route('/create_tpl', methods=['POST'])
def create_tpl():
    try:
        # Get JSON data from the request
        data = request.get_json()

        # Check if data is valid
        if not data:
            return jsonify({"error": "No data provided in the request body"}), 400

        # Now call the create_tpl method with the provided 'data'
        issue, error = MLOwnerService.create_tpl(data)

        if error:
            return jsonify({"error": error}), 400  # Return error message if something went wrong

        return jsonify({"issue": issue}), 200  # Return created issue if successful

    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return server error message
