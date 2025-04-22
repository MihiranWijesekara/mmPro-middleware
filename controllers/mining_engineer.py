import os
import tempfile
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required,check_token
from services.auth_service import AuthService
from services.mining_engineer_service import MiningEnginerService


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
    

@mining_enginer_bp.route('/me-pending-licenses', methods=['GET'])
@check_token
@role_required(['miningEngineer'])
def get_me_pending_licenses():
    try:
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401
            
        # Split the header to get the token part (handle both "Bearer token" and just "token")
        parts = auth_header.split()
        token = parts[1] if len(parts) == 2 else auth_header
        
        # Fetch Mining Licenses from the service
        mining_licenses, error = MiningEnginerService.get_me_pending_licenses(token)
        
        if error:
            return jsonify({"error": error}), 500 if "Server error" in error else 400
            
        return jsonify({"success": True, "data": mining_licenses}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# @mining_enginer_bp.route('/miningEngineer-approve/<int:issue_id>', methods=['PUT'])
# @check_token
# @role_required(['miningEngineer'])
# def miningEngineer_approve(issue_id):                               
#     try:
#         # Extract token from headers
#         auth_header = request.headers.get("Authorization")
#         if not auth_header:
#             return {"error": "Authorization token is missing"}, 400
        
#         token = auth_header.replace("Bearer ", "")
#         if not token:
#             return {"error": "Authorization token is invalid"}, 400
        
#         # Initialize custom fields
#         custom_fields = []
#         me_report_file = request.files.get('me_report') 

#         # Upload the file to Redmine and get the file ID
#         me_report_file_id = AuthService.upload_file_to_redmine(me_report_file) if me_report_file else None

#         if me_report_file_id:
#             custom_fields.append({"id": 94, "value": me_report_file_id})

#         # Get update data from request body
#         update_data = request.get_json()
#         if not update_data:
#             return {"error": "No update data provided"}, 400

#         # Add custom fields to the update data
#         update_data['custom_fields'] = custom_fields
        
#         # Call service to update the appointment
#         result, error = MiningEnginerService.miningEngineer_approve(
#             token=token,
#             issue_id=issue_id,
#             update_data=update_data
#         )
        
#         if error:
#             return {"error": error}, 500
        
#         return {"message": "Appointment updated successfully", "issue": result}, 200
    
#     except Exception as e:
#         return {"error": f"Unexpected error: {str(e)}"}, 500

@mining_enginer_bp.route('/miningEngineer-approve/<int:issue_id>', methods=['PUT'])
@check_token
@role_required(['miningEngineer'])
def miningEngineer_approve(issue_id):                               
    try:
        # Extract token from headers
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return {"error": "Authorization token is missing"}, 400
        
        token = auth_header.replace("Bearer ", "")
        if not token:
            return {"error": "Authorization token is invalid"}, 400
        
        me_report_file = request.files.get('me_report') 


        # Upload the file to Redmine and get the file ID
        me_report_file_id = AuthService.upload_file_to_redmine(me_report_file) if me_report_file else None



        # Get form data (not JSON)
        update_data = {
            "status_id": request.form.get("status_id", 32),
            "start_date": request.form.get("start_date", ""),
            "due_date": request.form.get("due_date", ""),
            "Capacity": request.form.get("Capacity", ""),
            "month_capacity": request.form.get("month_capacity", ""),
            "me_comment": request.form.get("me_comment", ""),
            "me_report":me_report_file_id
        }
        
        # Call service to update the appointment
        result, error = MiningEnginerService.miningEngineer_approve(
            token=token,
            issue_id=issue_id,
            update_data=update_data,
            attachments={"me_report": me_report_file} if me_report_file else None
        )
        
        if error:
            return {"error": error}, 500
        
        return {"message": "Mining license updated successfully", "issue": result}, 200
    
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}, 500
   