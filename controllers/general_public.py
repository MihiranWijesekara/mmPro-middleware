from flask import Blueprint, jsonify, request
from services.general_public_service import GeneralPublicService
from middleware.auth_middleware import role_required
from utils.jwt_utils import JWTUtils

general_public_bp = Blueprint('general_public', __name__)

@general_public_bp.route('/validate-lorry-number', methods=['GET'])
@role_required(['GeneralPublic'])
def validate_lorry_number():
    lorry_number = request.args.get("lorry_number")  # Get lorry number from query params
    token = request.headers.get("Authorization")

    if not lorry_number:
        return jsonify({"error": "Lorry number is required"}), 400  # 400 Bad Request

    tpl_license_exists, error = GeneralPublicService.is_lorry_number_valid(lorry_number,token)

    if error:
        if "No TPL with this lorry number" in error:
            return jsonify({"valid": False}), 200  # Return False if not found
        else:
            return jsonify({"error": "Internal Server Error"}), 500  # Hide technical errors

    return jsonify({"valid": tpl_license_exists}), 200  # Return True if valid

@general_public_bp.route('/send-verification', methods=['POST'])
@role_required(['GeneralPublic'])
def send_verification():
    data = request.json
    phone = data['phone']

    success, result = GeneralPublicService.send_verification_code(phone)

    if success:
        return jsonify({'success': True, 'verification_id': result})
    else:
        return jsonify({'success': False, 'error': result}), 400

# Route for verifying the code
@general_public_bp.route('/verify-code', methods=['POST'])
@role_required(['GeneralPublic'])
def verify_code():
    data = request.json
    phone = data['phone']
    code = data['code']

    success, result = GeneralPublicService.verify_code(phone, code)

    if success:
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result}), 401

# Route for creating a complaint
@general_public_bp.route('/create-complaint', methods=['POST'])
@role_required(['GeneralPublic'])
def create_complaint():
    data = request.json
    token = request.headers.get("Authorization")
    success, result = GeneralPublicService.create_complaint(data['phoneNumber'], data['vehicleNumber'], token)

    if success:
        return jsonify({'success': True, 'complaint_id': result})
    else:
        return jsonify({'success': False, 'error': result}), 500
    

@general_public_bp.route('/get-api', methods=['GET'])
@role_required(['GeneralPublic'])
def get_api():
    token = request.headers.get('Authorization')

    if not token or not token.startswith('Bearer '):
        return jsonify({'message': 'Authorization token is missing or malformed'}), 400

    # Extract the token without the "Bearer " prefix
    token = token[len('Bearer '):]

    # Decode JWT and decrypt the API key
    api_key = JWTUtils.decode_jwt_and_decrypt_api_key(token)

    if 'message' in api_key:
        # If there's an error message in the response, return the error
        return jsonify({'error': api_key['message']}), 401  # Token error handling

    # If no error, return the decrypted payload
    return jsonify(api_key)
