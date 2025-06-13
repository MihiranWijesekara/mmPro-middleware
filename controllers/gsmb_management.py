from flask import Blueprint, current_app, jsonify, request
from middleware.auth_middleware import role_required,check_token
from services.gsmb_managemnt_service import GsmbManagmentService


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

#(Done)
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

#(Done)
@gsmb_management_bp.route('/fetch-royalty-counts', methods=['GET'])
@check_token                 
@role_required(['GSMBManagement'])
def fetch_royalty_counts():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    # Call the service method
    response, error = GsmbManagmentService.fetch_royalty_counts(token)
    
    if error:
        return jsonify({"error": error}), 500

    # Return the response from the service method
    return response   

#(Done)
@gsmb_management_bp.route('/monthly-mining-license-count', methods=['GET'])  
@check_token                 
@role_required(['GSMBManagement'])         
def monthly_mining_license_count():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    issues, error = GsmbManagmentService.monthly_mining_license_count(token)
    
    if error:
        return jsonify({"error": error}), 500

    return jsonify({"issues": issues})

# Fetch transport license data by location (DONE)
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


#Fetch mining license data by location (DONE)
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


#fetchRoleCounts (Done)
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


#fetchMiningLicenseCounts (Done)
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


@gsmb_management_bp.route('/unactive-gsmb-officers', methods=['GET'])
@check_token
@role_required(['GSMBManagement'])
def unactive_gsmb_officers():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    # Corrected spelling to GsmbManagementService
    officers, error = GsmbManagmentService.unactive_gsmb_officers(token)
    
    if error:
        # Include more detailed error logging
        current_app.logger.error(f"Error fetching GSMB officers: {error}")
        return jsonify({"error": error}), 500

    return jsonify({
        "officers": officers,
        "count": len(officers) if officers else 0
    }), 200
    

@gsmb_management_bp.route('/active-gsmb-officers/<int:id>', methods=['PUT'])
@check_token
@role_required(['GSMBManagement'])
def active_gsmb_officers(id):  # Parameter name should match the route parameter 'id'
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Authorization token is required"}), 401

    try:
        # Activate the officer by changing status from 3 to 1
        success, error = GsmbManagmentService.activate_gsmb_officer(token, id, {"status": 1})
        
        if error:
            current_app.logger.error(f"Error activating GSMB officer {id}: {error}")
            return jsonify({"error": error}), 500

        return jsonify({
            "success": True,
            "message": f"Officer {id} activated successfully",
            "id": id,
            "new_status": 1
        }), 200

    except Exception as e:
        current_app.logger.error(f"Unexpected error in active_gsmb_officers: {str(e)}")
        return jsonify({"error": "An unexpected error occurred"}), 500

