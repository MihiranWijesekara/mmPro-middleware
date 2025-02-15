import jwt
from flask import request, jsonify
from functools import wraps
from config import Config

def role_required(allowed_roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization')
            if not token:
                return jsonify({"message": "Token is missing"}), 403

            try:      
                token = token.split(" ")[1]    
                payload = jwt.decode(token, Config.SECRET_KEY, algorithms=[Config.JWT_ALGORITHM])
                user_role = payload.get("role")

                if user_role not in allowed_roles:
                    return jsonify({"message": "Access Denied: Insufficient permissions"}), 403

            except jwt.ExpiredSignatureError:
                return jsonify({"message": "Token has expired"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"message": "Invalid token"}), 401

            return f(*args, **kwargs)
        
        return decorated_function
    return wrapper
