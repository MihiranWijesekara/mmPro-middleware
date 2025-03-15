from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required,check_token
from services.gsmb_managemnt_service import GsmbManagmentService


# Define the Blueprint
gsmb_management_bp = Blueprint('gsmb_management', __name__) 

@gsmb_management_bp.route('/monthly-total-sand', methods=['GET'])   
@check_token                
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
@check_token                
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
@check_token
@role_required(['GSMBManagement'])
def fetch_royalty_counts():
    print("fetch-royalty-counts")
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    # Call the service method
    response, error = GsmbManagmentService.fetch_royalty_counts(token)
    
    if error:
        return jsonify({"error": error}), 500

    # Return the response from the service method
    return response   

@gsmb_management_bp.route('/monthly-mining-license-count', methods=['GET'])
@check_token                   
@role_required(['GSMBManagement'])         
def monthly_mining_license_count():
    print("monthly-mining-license-count")
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.monthly_mining_license_count(token)
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})

# Fetch transport license data by location
@gsmb_management_bp.route('/transport-license-destination', methods=['GET'])
@check_token
@role_required(['GSMBManagement'])
def transport_license_destination():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.transport_license_destination(token)  # Fix method name
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})


#Fetch mining license data by location
@gsmb_management_bp.route('/total-location-ml', methods=['GET'])
@check_token
@role_required(['GSMBManagement'])
def total_location_ml():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.total_location_ml(token) 
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})    


#ComplaintCounts
@gsmb_management_bp.route('/complaint-counts', methods=['GET'])
@check_token
@role_required(['GSMBManagement'])
def complaint_counts():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.complaint_counts(token) 
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues}) 


#fetchRoleCounts
@gsmb_management_bp.route('/role-counts', methods=['GET'])
@check_token
@role_required(['GSMBManagement'])
def role_counts():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.role_counts(token) 
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})


#fetchMiningLicenseCounts
@gsmb_management_bp.route('/mining-license-count', methods=['GET'])
@check_token
@role_required(['GSMBManagement'])
def mining_license_count():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.mining_license_count(token) 
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})  


    
