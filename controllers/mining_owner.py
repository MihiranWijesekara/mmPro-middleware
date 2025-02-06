from flask import Blueprint, jsonify
from middleware.auth_middleware import role_required

mining_owner_bp = Blueprint('mining_owner', __name__)

@mining_owner_bp.route('/mining', methods=['GET'])
@role_required(['mining_owner'])
def admin_access():
    return jsonify({"message": "Admin access granted for Mining Owner!"})

