from flask import Blueprint, jsonify
from middleware.auth_middleware import role_required

general_public_bp = Blueprint('general_public', __name__)

@general_public_bp.route('/mining', methods=['GET'])
@role_required(['mining_owner'])
def admin_access():
    return jsonify({"message": "Admin access granted for Mining Owner!"})
