from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required
from services.gsmb_managemnt_service import GsmbManagmentService

# Define the Blueprint
gsmb_management_bp = Blueprint('gsmb_management', __name__) 

@gsmb_management_bp.route('/monthly-total-sand', methods=['GET'])                   
@role_required(['GSMBManagement'])         
def monthly_total_sand_cubes():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.monthly_total_sand_cubes(token)
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})

@gsmb_management_bp.route('/fetch-top-mining-holders', methods=['GET'])                   
@role_required(['GSMBManagement'])         
def fetch_top_mining_holders():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.fetch_top_mining_holders(token)
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})    

@gsmb_management_bp.route('/fetch-royalty-counts', methods=['GET'])                   
@role_required(['GSMBManagement'])         
def fetch_royalty_counts():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.fetch_royalty_counts(token)
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})     


    
