import os
import tempfile
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required,check_token
from services.auth_service import AuthService
from services.director_general_service import  DirectorGeneralService


director_general_bp = Blueprint('director_general', __name__)

@director_general_bp.route('/dg-pending-licenses', methods=['GET'])
@check_token
@role_required(['DG'])
def get_dg_pending_licenses():
    try:
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization header is missing"}), 401
            
        # Split the header to get the token part (handle both "Bearer token" and just "token")
        parts = auth_header.split()
        token = parts[1] if len(parts) == 2 else auth_header
        
        # Fetch Mining Licenses from the service
        mining_licenses, error = DirectorGeneralService.get_dg_pending_licenses(token)
        
        if error:
            return jsonify({"error": error}), 500 if "Server error" in error else 400
            
        return jsonify({"success": True, "data": mining_licenses}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500