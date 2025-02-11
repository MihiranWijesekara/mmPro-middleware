from flask import Blueprint, jsonify, request
from services.general_public_service import GeneralPublicService

general_public_bp = Blueprint('general_public', __name__)

@general_public_bp.route('/validate-lorry-number', methods=['GET'])
def validate_lorry_number():
    lorry_number = request.args.get("lorry_number")  # Get lorry number from query params

    if not lorry_number:
        return jsonify({"error": "Lorry number is required"}), 400  # 400 Bad Request

    tpl_license_exists, error = GeneralPublicService.is_lorry_number_valid(lorry_number)

    if error:
        if "No TPL with this lorry number" in error:
            return jsonify({"valid": False}), 200  # Return False if not found
        else:
            return jsonify({"error": "Internal Server Error"}), 500  # Hide technical errors

    return jsonify({"valid": tpl_license_exists}), 200  # Return True if valid
