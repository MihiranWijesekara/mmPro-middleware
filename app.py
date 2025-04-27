from flask import Flask
from controllers import auth_bp, mining_owner_bp, gsmb_officer_bp, police_officer_bp, general_public_bp, mining_enginer_bp, gsmb_management_bp,director_general_bp
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# CORS(app, resources={r"/*": {
#     "origins": ["http://mmpro.aasait.lk:80/", "http://localhost:5173/"],  # List of allowed origins
#     "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
# }})
# CORS(app, resources={r"/*": {
#     "origins": ["http://mmpro.aasait.lk", "http://localhost:5173" , "http://124.43.163.209:5000"],  # Allowed origins (no trailing slash)
#     "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
#     "allow_headers": ["Content-Type", "Authorization"],  # Allowed headers
#     "supports_credentials": True  # Enable cookies or credentials if needed
# }})

# Load environment variables
app.config.from_pyfile('.env')

# Register Blueprints for each role-based controller
app.register_blueprint(mining_enginer_bp, url_prefix='/mining-engineer')
app.register_blueprint(mining_owner_bp, url_prefix='/mining-owner')
app.register_blueprint(gsmb_officer_bp, url_prefix='/gsmb-officer')
app.register_blueprint(police_officer_bp, url_prefix='/police-officer')
app.register_blueprint(general_public_bp, url_prefix='/general-public')
app.register_blueprint(gsmb_management_bp, url_prefix='/gsmb-management')
app.register_blueprint(director_general_bp, url_prefix='/director-general')
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    print("Server is running on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
