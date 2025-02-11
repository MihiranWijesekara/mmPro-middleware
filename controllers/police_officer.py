from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required
from services.police_officer_service import PoliceOfficerService


police_officer_bp = Blueprint('police_officer', __name__)

@police_officer_bp.route('/check-lorry-number', methods=['GET'])
@role_required(['PoliceOfficer'])
def get_tpl_licenses():
    lorry_number = request.args.get("lorry_number")  # Get lorry number from query params

    if not lorry_number:
        return jsonify({"error": "Lorry number is required"}), 400

    issues, error = PoliceOfficerService.check_lorry_number(lorry_number)

    if error:
        if "No TPL with this lorry number" in error:
            return jsonify({"error": error}), 200   
        else:
            return jsonify({"error": error}), 500

    return jsonify({"tpl_licenses": issues})
