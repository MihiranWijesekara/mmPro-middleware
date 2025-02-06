from flask import Blueprint, jsonify
from middleware.auth_middleware import role_required

police_officer_bp = Blueprint('police_officer', __name__)

@police_officer_bp.route('/mining', methods=['GET'])
@role_required(['mining_owner'])
def admin_access():
    return jsonify({"message": "Admin access granted for Mining Owner!"})
