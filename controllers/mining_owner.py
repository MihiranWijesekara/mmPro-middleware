from flask import Blueprint, jsonify
from middleware.auth_middleware import role_required
from services.mining_owner_service import MLOwnerService
mining_owner_bp = Blueprint('mining_owner', __name__)

@mining_owner_bp.route('/mining-licenses', methods=['GET'])
@role_required(['MLOwner'])
def get_mining_licenses():
    issues, error = MLOwnerService.mining_licenses()
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"mining_licenses": issues})

