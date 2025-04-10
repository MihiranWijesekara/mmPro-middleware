import os
import tempfile
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required,check_token
from services.auth_service import AuthService
from services.mining_enginer_service import MiningEnginerService


# Define the Blueprint for mining_enginer
mining_enginer_bp = Blueprint('mining_enginer', __name__)

@mining_enginer_bp.route('/miningOwner-appointment/<int:issue_id>', methods=['PUT'])
@check_token
@role_required(['miningEngineer'])
def update_miningOwner_appointment(issue_id):
    try:
        # Extract token from headers
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"error": "Authorization token is missing"}, 400
        
        token = auth_header.replace("Bearer ", "")
        if not token:
            return {"error": "Authorization token is invalid"}, 400
        
        # Get update data from request body
        update_data = request.get_json()
        if not update_data:
            return {"error": "No update data provided"}, 400
        
        # Call service to update the appointment
        result, error = MiningEnginerService.update_miningOwner_appointment(
            token=token,
            issue_id=issue_id,
            update_data=update_data
        )
        
        if error:
            return {"error": error}, 500
        
        return {"message": "Appointment updated successfully", "issue": result}, 200
    
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500