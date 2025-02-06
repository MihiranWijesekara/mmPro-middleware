from flask import Blueprint, jsonify
from middleware.auth_middleware import role_required
from services.gsmb_officer_service import GsmbOfficerService

gsmb_officer_bp = Blueprint('gsmb_officer', __name__)

@gsmb_officer_bp.route('/mining-licenses', methods=['GET'])
@role_required(['GSMBOfficer'])
def get_mining_licenses():
    issues, error = GsmbOfficerService.get_mining_licenses()
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"mining_licenses": issues})
