import json
from functools import wraps
from urllib.request import urlopen

from flask import request
from jose import jwt

from ..constants import StatusCode, ErrorMessage

# 'https://dev-fsnd-luqman.auth0.com/authorize?response_type=token&client_id=rNjPqKWAB92MleZ65442GuWg3vkJKBFN&redirect_uri=http://localhost:8080/login-results&audience=cafe'
AUTH0_DOMAIN = 'dev-fsnd-luqman.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'cafe'


class AuthError(Exception):
    """A standardized way to communicate auth failure modes."""

    def __init__(self, error, status_code):
        """
        Init method of class.
        :param error:
        :param status_code:
        """
        self.error = error
        self.status_code = status_code


def raise_auth_error(error, status_code=StatusCode.HTTP_401_UNAUTHORIZED.value):
    """
    Raise auth error with given message.
    :param error:
    :param status_code:
    :return:
    """
    raise AuthError({
        'success': False,
        'message': error,
        'error': status_code
    }, status_code)


def get_token_auth_header():
    """
    Get token from authorization header and raise error is header is incorrect.
    :return:
    """

    authorization = request.headers.get('Authorization')
    if not authorization:
        raise_auth_error(ErrorMessage.MISSING_AUTHORIZATION.value)

    authorization_parts = authorization.split(' ')
    if authorization_parts[0].lower() != 'bearer':
        raise_auth_error(ErrorMessage.MISSING_BEARER.value)

    elif len(authorization_parts) == 1:
        raise_auth_error(ErrorMessage.MISSING_TOKEN.value)

    elif len(authorization_parts) > 2:
        raise_auth_error(ErrorMessage.MISSING_BEARER_TOKEN.value)

    token = authorization_parts[1]
    return token


def check_permissions(permission, payload):
    """
    Check permission against a payload.
    :param permission:
    :param payload:
    :return:
    """
    if 'permissions' in payload and permission in payload['permissions']:
        return True

    raise_auth_error(StatusCode.HTTP_401_UNAUTHORIZED.value)

def verify_decode_jwt(token):
    """
    Verify if jwt can be decoded properly and is not tempered.
    :param token:
    :return:
    """
    unverified_header = jwt.get_unverified_header(token)
    if 'kid' not in unverified_header:
        raise_auth_error(ErrorMessage.AUTHORIZATION_MALFORMED.value)

    json_url = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(json_url.read())
    rsa_key = {}

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if not rsa_key:
        raise_auth_error(ErrorMessage.INVALID_KEY.value, StatusCode.HTTP_401_UNAUTHORIZED.value)

    try:
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=ALGORITHMS,
            audience=API_AUDIENCE,
            issuer='https://' + AUTH0_DOMAIN + '/'
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise_auth_error(ErrorMessage.TOKEN_EXPIRED.value)
    except jwt.JWTClaimsError:
        raise_auth_error(ErrorMessage.INVALID_CLAIMS.value)
    except Exception:
        raise_auth_error(ErrorMessage.UNABLE_TO_PARSE.value, StatusCode.HTTP_400_BAD_REQUEST.value)


def requires_auth(permission=''):
    """
    Require Auth method.
    :param permission:
    :return:
    """

    def requires_auth_decorator(function):
        """
        Require Auth decorator.
        :param function:
        :return:
        """

        @wraps(function)
        def wrapper(*args, **kwargs):
            """
            Decorate wrapper method.
            :param args:
            :param kwargs:
            :return:
            """
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return function(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
