# from flask_cors import CORS
from flask import Blueprint, jsonify, request
from middleware.auth_middleware import role_required, check_token
from services.gsmb_officer_service import GsmbOfficerService
import os
from werkzeug.utils import secure_filename
import tempfile


# Define the Blueprint for gsmb_officer
gsmb_officer_bp = Blueprint('gsmb_officer', __name__)




# @gsmb_officer_bp.route('/gsmb-issue', methods=['GET'])
# @check_token
# @role_required(['GSMBOfficer'])
# def get_mining_licenses():
#     # Get the token from the request header
#     token = request.headers.get('Authorization')

#     if not token:
#         return jsonify({"error": "Authorization token is missing"}), 400

#     # Pass the token to the service method
#     issues, error = GsmbOfficerService.get_Issues_Data(token)
    
#     if error:
#         return jsonify({"error": error}), 500

#     return jsonify({"mining_licenses": issues})



  # Allow requests from React Vite frontend

            
@gsmb_officer_bp.route('/user-detail/<int:user_id>', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def user_detail(user_id):
    try:
        # Check if the Authorization token is present in the request
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Authorization token is missing"}), 401
        
        # Check if the token starts with 'Bearer ' (you can also validate it further here if needed)
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid token format. Expected 'Bearer <token>'"}), 401
        
        # Extract the token from the header
        token = auth_header.split(' ')[1]
        
        # Now validate the token, you can add your custom token validation logic here
        # For simplicity, we will assume the token is valid if it's present
        if not token:  # You can add further validation logic here
            return jsonify({"error": "Invalid or missing token"}), 401


        # Call the create_tpl method with the provided 'data'
        # issue, error = GsmbOfficerService.create_tpl(data)
        detail, error = GsmbOfficerService.user_detail(user_id, auth_header)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"user_detail": detail})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    




           # Put route for /update-ML
@gsmb_officer_bp.route('/add-license', methods=['POST'])
@check_token
@role_required(['GSMBOfficer'])
def add_new_license():
    try:
        #Get the token from the request header
        token =request.headers.get('Authorization')

        if not token:
            return jsonify({"error":"Authorization token is missing"}), 400

        # Get the payload from the request body (expected to be a JSON)
        payload = request.json 
        print(payload) 

        #validate the payload, ensure required data is present 
        if not payload or 'issue' not in payload:
            return jsonify({"error" : "Missing required data in the request"}), 400
        
        # pass the token and payload to the service method
        new_license, error =GsmbOfficerService.add_new_license(token, payload)

        if error:
            return jsonify({"error": error}), 500
        
        return jsonify({"success": True, "data": new_license}),201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
  
  
  
  
    
    
           # Fetch a single license by ID
@gsmb_officer_bp.route('/get-license/<int:licenseId>', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def get_license_details(licenseId):
    try:
        #Get the token from the request header
        token =request.headers.get('Authorization')

        if not token:
            return jsonify({"error":"Authorization token is missing"}), 400

        # pass the token and payload to the service method
        license_details, error =GsmbOfficerService.get_license_details(token,licenseId )

        if error:
            return jsonify({"error": error}), 500
        
        return jsonify({"success": True, "data": license_details}),201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500    






           # Update a license by ID
@gsmb_officer_bp.route('/update-license/<int:licenseId>', methods=['PUT'])
@check_token
@role_required(['GSMBOfficer'])
def update_license(licenseId):
    try:
        #Get the token from the request header
        token =request.headers.get('Authorization')

        if not token:
            return jsonify({"error":"Authorization token is missing"}), 400

        # Get the payload from the request body (expected to be a JSON)
        payload = request.json 
        # print(payload) 

        #validate the payload, ensure required data is present 
        if not payload or 'issue' not in payload:
            return jsonify({"error" : "Missing required data in the request"}), 400
        
        # pass the token and payload to the service method
        update_license, error =GsmbOfficerService.update_license(token, payload ,licenseId)

        if error:
            return jsonify({"error": error}), 500
        
        return jsonify({"success": True, "data": update_license}),201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        









           # Register  ML Owner
@gsmb_officer_bp.route('/add-mlowner', methods=['POST'])
@check_token
@role_required(['GSMBOfficer'])
def add_new_mlowner():
    try:
        #Get the token from the request header
        token =request.headers.get('Authorization')

        if not token:
            return jsonify({"error":"Authorization token is missing"}), 400

        # Get the userData from the request body (expected to be a JSON)
        userData = request.json 

        #validate the userData, ensure required data is present 
        if not userData or 'user' not in userData:
            return jsonify({"error" : "Missing required data in the request"}), 400
        
        # pass the token and userData to the service method
        new_owner, error =GsmbOfficerService.add_new_mlowner(token, userData)

        if error:
            return jsonify({"error": error}), 500
        
        # After the user is created, assign them to a project
        project_id = 31  # Define the project ID here (GSMB project, for example)
        role_id = 10  # Define the role ID here (ML Owner role, for example)
        assignment_response, assignment_error = GsmbOfficerService.assign_user_to_project(new_owner['id'], project_id, role_id, token)

        if assignment_error:
            return jsonify({"error": assignment_error}), 500

        return jsonify({"success": True, "data": new_owner}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    

# Get TPL History


@gsmb_officer_bp.route('/view-tpls', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def view_tpls():
    try:
        # Get the token from the request header
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        # Fetch tpl data from service
        issues, error = GsmbOfficerService.view_tpls(token)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"view_tpls": issues})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return server error message













           # OLD CODE Get MLowners
# @gsmb_officer_bp.route('/get-mlowners', methods=['GET'])
# @check_token
# @role_required(['GSMBOfficer'])
# def get_mlowners():
#     try:
#         # Get the token from the request header
#         token = request.headers.get('Authorization')

#         if not token:
#             return jsonify({"error": "Authorization token is missing"}), 400

#         # pass the token and payload to the service method
#         mlowners_details, error = GsmbOfficerService.get_mlowners(token)

#         if error:
#             return jsonify({"error": error}), 500
        
#         # For each ML Owner, get their associated licenses
#         for owner in mlowners_details:
#             user_id = owner['id']
#             licenses, error = GsmbOfficerService.get_user_licenses(user_id, token)
#             if error:
#                 return jsonify({"error": error}), 500
#             owner['licenses'] = licenses

#         return jsonify({"success": True, "data": mlowners_details}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500       
# 
# 

@gsmb_officer_bp.route('/get-mlowners', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def get_mlowners():
    try:
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        mlowners_details, error = GsmbOfficerService.get_mlowners(token)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"success": True, "data": mlowners_details}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gsmb_officer_bp.route('/get-mlowners/individual', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def get_individual_mlowners():
    try:
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        all_mlowners, error = GsmbOfficerService.get_mlowners(token)

        if error:
            return jsonify({"error": error}), 500

        # Function to extract field value by name
        def get_field_value(custom_fields, field_name):
            for field in custom_fields:
                if field["name"] == field_name:
                    return field["value"]
            return ""

        # Filter only individuals and format response
        individual_mlowners = []
        for owner in all_mlowners:
            if any(field["id"] == 41 and field["value"] for field in owner.get("custom_fields", [])):  # Check if NIC exists
                formatted_owner = {
                    "login": owner.get("login", ""),
                    "first_name": owner.get("firstname", "").strip(),
                    "last_name": owner.get("lastname", "").strip(),
                    "email": owner.get("mail", ""),
                    "national_identity_card": get_field_value(owner.get("custom_fields", []), "National Identity Card"),
                    "address": get_field_value(owner.get("custom_fields", []), "Address"),
                    "nationality": get_field_value(owner.get("custom_fields", []), "Nationality"),
                    "mobile_number": get_field_value(owner.get("custom_fields", []), "Mobile Number"),
                    "employment_name_of_employer": get_field_value(owner.get("custom_fields", []), "Employment ,Name of employer"),
                    "place_of_business": get_field_value(owner.get("custom_fields", []), "Place of Business"),
                    "residence": get_field_value(owner.get("custom_fields", []), "Residence"),
                }
                individual_mlowners.append(formatted_owner)

        return jsonify({"success": True, "data": individual_mlowners}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@gsmb_officer_bp.route('/get-mlowners/company', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def get_company_mlowners():
    try:
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        all_mlowners, error = GsmbOfficerService.get_mlowners(token)

        if error:
            return jsonify({"error": error}), 500

        # Function to extract field value by name
        def get_field_value(custom_fields, field_name):
            for field in custom_fields:
                if field["name"] == field_name:
                    return field["value"]
            return ""

        # Filter only company owners and format response
        company_mlowners = []
        for owner in all_mlowners:
            if any(field["id"] in [47, 49] and field["value"] for field in owner.get("custom_fields", [])):  
                formatted_owner = {
                    "login": owner.get("login", ""),
                    "first_name": owner.get("firstname", "").strip(),
                    "last_name": owner.get("lastname", "").strip(),
                    "country_of_incorporation": get_field_value(owner.get("custom_fields", []), "Country of Incorporation"),
                    "head_office": get_field_value(owner.get("custom_fields", []), "Head Office"),
                    "address_of_registered_company": get_field_value(owner.get("custom_fields", []), "Address of Registered Company"),
                    "capitalization": get_field_value(owner.get("custom_fields", []), "Capitalization"),
                    "articles_of_association": get_field_value(owner.get("custom_fields", []), "Articles of Association"),
                    "annual_reports": get_field_value(owner.get("custom_fields", []), "Annual Reports"),
                    "mobile_number": get_field_value(owner.get("custom_fields", []), "Mobile Number"),
                }
                company_mlowners.append(formatted_owner)

        return jsonify({"success": True, "data": company_mlowners}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@gsmb_officer_bp.route('/register-mlowners/individual', methods=['POST'])
@check_token
@role_required(['GSMBOfficer'])
def register_individual_mlowner():
    try:
        token = request.headers.get('Authorization')
        data = request.get_json()

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        # Validate required fields
        required_fields = [
            'login', 'first_name', 'last_name', 'email', 'password',
            'national_identity_card', 'address', 'nationality', 'mobile_number'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Prepare custom fields for individual
        custom_fields = [
            {"id": 41, "value": data['national_identity_card']},  # National Identity Card
            {"id": 42, "value": data.get('address', '')},  # Address
            {"id": 43, "value": data.get('nationality', '')},  # Nationality
            {"id": 44, "value": data.get('mobile_number', '')},  # Mobile Number
            {"id": 45, "value": data.get('employment_name_of_employer', '')},  # Employment, Name of employer
            {"id": 46, "value": data.get('place_of_business', '')},  # Place of Business
            {"id": 48, "value": data.get('residence', '')}  # Residence
        ]

        # Call service to create user
        result, error = GsmbOfficerService.register_mlowner(
            login=data['login'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            custom_fields=custom_fields
        )

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"success": True, "data": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gsmb_officer_bp.route('/register-mlowners/company', methods=['POST'])
@check_token
@role_required(['GSMBOfficer'])
def register_company_mlowner():
    try:
        token = request.headers.get('Authorization')
        data = request.get_json()

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        # Validate required fields
        required_fields = [
            'login', 'first_name', 'last_name', 'email', 'password',
            'country_of_incorporation', 'head_office', 'address_of_registered_company'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Prepare custom fields for company
        custom_fields = [
            {"id": 47, "value": data['country_of_incorporation']},  # Country of Incorporation
            {"id": 48, "value": data['head_office']},  # Head Office
            {"id": 49, "value": data['address_of_registered_company']}  # Address of Registered Company
        ]

        # Handle file attachments
        file_fields = {"articles_of_association": 75, "annual_reports": 76}
        attachments = {}
        for field, custom_field_id in file_fields.items():
            if field in data:
                attachments[custom_field_id] = data[field]

        # Call service to create user
        result, error = GsmbOfficerService.register_mlowner(
            login=data['login'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            password=data['password'],
            custom_fields=custom_fields,
            attachments=attachments
        )

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"success": True, "data": result}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gsmb_officer_bp.route('/get-tpls', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def get_tpls():
    try:
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        # Fetch TPLs from the service
        tpls, error = GsmbOfficerService.get_tpls(token)

        if error:
            return jsonify({"error": error}), 500

        return jsonify({"success": True, "data": tpls}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@gsmb_officer_bp.route('/get-mining-licenses', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def get_mining_licenses():
    try:
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        # Fetch Mining Licenses from the service
        mining_licenses, error = GsmbOfficerService.get_mining_licenses(token)
        
        if error:
            return jsonify({"error": error}), 500

        return jsonify({"success": True, "data": mining_licenses}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@gsmb_officer_bp.route('/get-mining-license-counts', methods=['GET'])
@check_token
@role_required(['GSMBOfficer'])
def get_mining_license_counts():
    try:
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({"error": "Authorization token is missing"}), 400

        # Fetch mining license counts
        license_counts, error = GsmbOfficerService.get_mining_license_counts(token)
        
        if error:
            return jsonify({"error": error}), 500

        return jsonify({"success": True, "data": license_counts}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @gsmb_officer_bp.route('/get-distance', methods=['POST'])
# @check_token
# @role_required(['GSMBOfficer'])
# def calculate_distance():
#     """
#     Endpoint to calculate the distance between two cities.
#     Expects a JSON payload with 'city1' and 'city2'.
#     """
#     # Get JSON data from the request
#     data = request.json
#     # Validate input
#     city1 = data.get('city1')
#     city2 = data.get('city2')

#     if not city1 or not city2:
#         return jsonify({
#             "success": False,
#             "error": "Both 'city1' and 'city2' are required"
#         }), 400

#     # Call the service to calculate the distance
#     result = GsmbOfficerService.calculate_distance(city1, city2)

#     # Return the result
#     if result['success']:
#         return jsonify(result), 200
#     else:
#         return jsonify(result), 500

    
          