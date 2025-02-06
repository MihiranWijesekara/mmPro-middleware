import jwt
from config import Config
import datetime

def create_jwt_token(user_id, role):
    # Use timezone-aware UTC datetime for expiration
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': expiration_time
    }

    token = jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token
