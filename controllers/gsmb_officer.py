from flask import Blueprint, jsonify
from middleware.auth_middleware import role_required
from services.gsmb_officer_service import GsmbOfficerService

# Define the Blueprint for gsmb_officer
gsmb_officer_bp = Blueprint('gsmb_officer', __name__)

@gsmb_officer_bp.route('/gsmb-officer', methods=['GET'])
# @role_required(['GSMBOfficer'])
@role_required(['GSMBOfficer'])
def get_mining_licenses():
    issues, error = GsmbOfficerService.get_Issues_Data()
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"mining_licenses": issues})
