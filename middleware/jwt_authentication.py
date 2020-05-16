import jwt

from conf.config import LOG, API_SECRET_KEY
from utils.errors import generic_error_handler

def validate_token(req, resp, resource, params):
    LOG.debug('JWT Validation')
    token = req.get_header('Authorization')

    if token is None:
        error = {
            "description": "Please provide JWT token as part of the request."
        }
        raise generic_error_handler(401, error_override=error)

    try:
        token_is_valid(req, token)
    except Exception as ex: 
        error = {
            "description": "invalid token, try again",
            "details": str(ex)
        }
        raise generic_error_handler(401, error_override=error)

def token_is_valid(req, token):
    if token.startswith("JWT "):
        token_type = "JWT"
    else:
        LOG.error("Token validation failed")
        raise Exception("Invalid token type -> Only 'JWT' allowed")
    
    req.jwt_token = token
    token = token.split(f"{token_type} ")[1]

    try:
        jwt_body = jwt.decode(token, API_SECRET_KEY, verify=True, algorithms=['HS256'])
        if 'username' in jwt_body:
            req.username = jwt_body['username']
    except Exception as ex:
        LOG.error(f"There was an error : {ex}")
        raise Exception(f"{ex}")
