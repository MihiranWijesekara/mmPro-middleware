import jwt
from config import Config
import datetime

def create_jwt_token(role):
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    
    payload = {
        'role': role,
        'exp': expiration_time
    }

    token = jwt.encode(payload, Config.SECRET_KEY, algorithm=Config.JWT_ALGORITHM)
    return token
