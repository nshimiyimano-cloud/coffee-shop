import json
from jose import jwt
from flask import jsonify
from flask import request, _request_ctx_stack
from functools import wraps


from urllib.request import urlopen



AUTH0_DOMAIN = 'nshimiye-dev-biond.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'https://coshop-app'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header

'''
@TODO implement get_token_auth_header() method
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
'''
def get_token_auth_header():
    
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":"Authorization header is expected"}, 401)

    #eg authorization header composed with 2(bearer and token) must look "Authorization,"Bearer token653hdgdhdjdjjkdkkd"

   # so we use split method to cut into array with two element first for bearer , second for token
    parts = auth.split()    

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token

   

'''
@TODO implement check_permissions(permission, payload) method
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
'''
#def check_permissions(permission, payload):
        
    #if 'permissions' not in payload:
                        #raise AuthError({
                           # 'code': 'invalid_claims',
                            #'description': 'Permissions not included in JWT.'
                       # }, 400)

    #if permission not in payload['permissions']:
        #raise AuthError({
           # 'code': 'unauthorized',
         #   'description': 'Permission not found.'
       # }, 403)
   # return True

def authorize(permission, payload):
    def authorize_decorator(funct):
               
        @wraps(funct)
        def wrapper(*args, **kwargs):
            if 'permissions' not in payload:
                raise AuthError({
                    'code': 'invalid_claims',
                    'description': 'Permissions not included in JWT.'
                 }, 400)


            if permission not in payload['permissions']:
                raise AuthError({
                    'code': 'unauthorized',
                    'description': 'Permission not found.'
                 }, 403)

            print(permission)
            #return funct(*args, **kwargs)
            
        return wrapper
            
    return authorize_decorator
    
    

'''
@TODO implement verify_decode_jwt(token) method
    @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
'''
# Format error response and append status code
def get_token_auth_header():      #this work as expected
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.headers.get("Authorization", None)
    if not auth:
        raise AuthError({"code": "authorization_header_missing",
                        "description":
                            "Authorization header is expected"}, 401)

    parts = auth.split()

    if parts[0].lower() != "bearer":
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must start with"
                            " Bearer"}, 401)
    elif len(parts) == 1:
        raise AuthError({"code": "invalid_header",
                        "description": "Token not found"}, 401)
    elif len(parts) > 2:
        raise AuthError({"code": "invalid_header",
                        "description":
                            "Authorization header must be"
                            " Bearer token"}, 401)

    token = parts[1]
    return token

def verify_decode_jwt():
    """Determines if the Access Token is valid
    """
    def requiresauth(function):
        @wraps(function)
        def decorated(*args, **kwargs):
            token = get_token_auth_header()
            jsonurl = urlopen("https://"+AUTH0_DOMAIN+"/.well-known/jwks.json")
            jwks = json.loads(jsonurl.read())
            unverified_header = jwt.get_unverified_header(token)
            rsa_key = {}
            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    rsa_key = {
                        "kty": key["kty"],
                        "kid": key["kid"],
                        "use": key["use"],
                        "n": key["n"],
                        "e": key["e"]
                    }
            if rsa_key:
                try:
                    payload = jwt.decode(
                        token,
                        rsa_key,
                        algorithms=ALGORITHMS,
                        audience=API_AUDIENCE,
                        issuer="https://"+AUTH0_DOMAIN+"/"
                    )
                    
                except jwt.ExpiredSignatureError:
                    raise AuthError({"code": "token_expired",
                                    "description": "token is expired"}, 401)
                except jwt.JWTClaimsError:
                    raise AuthError({"code": "invalid_claims",
                                    "description":
                                        "incorrect claims,"
                                        "please check the audience and issuer"}, 401)
                except Exception:
                    raise AuthError({"code": "invalid_header",
                                    "description":
                                        "Unable to parse authentication"
                                        " token."}, 401)

                _request_ctx_stack.top.current_user = payload
                return function(*args, **kwargs)
            raise AuthError({"code": "invalid_header",
                        "description": "Unable to find appropriate key"}, 401)
        return decorated
    return requiresauth
        
    
    



'''
@TODO implement @requires_auth(permission) decorator method
    @INPUTS
        permission: string permission (i.e. 'post:drink')

    it should use the get_token_auth_header method to get the token
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the requested permission
    return the decorator which passes the decoded payload to the decorated method
'''
def requires_auth(permission=''):
    def requires_auth_decorator(funct):
        @wraps(funct)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()        
            payload = verify_decode_jwt()
            
            ##------------------------------#check permission and payload---------
            authorize(permission=permission,payload=payload)
                
           # print(permission,payload)
            
            #return funct(*args, **kwargs)   #return payload only to check if payload got
            return (token)
            

        return wrapper
    return requires_auth_decorator
    
