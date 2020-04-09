from enum import Enum


class StatusCode(Enum):
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_204_NO_CONTENT = 204
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_403_FORBIDDEN = 403
    HTTP_404_NOT_FOUND = 404
    HTTP_405_METHOD_NOT_ALLOWED = 405
    HTTP_422_UNPROCESSABLE_ENTITY = 422
    HTTP_500_INTERNAL_SERVER_ERROR = 500


class ErrorMessage(Enum):
    MISSING_AUTHORIZATION = 'Authorization header in request headers is mandatory.'
    MISSING_BEARER = 'Authorization header must start with "Bearer".'
    MISSING_TOKEN = 'Authorization header must have token.'
    MISSING_BEARER_TOKEN = 'Authorization header must be a Bearer token.'
    AUTHORIZATION_MALFORMED = 'Authorization malformed.'
    TOKEN_EXPIRED = 'Token Expired.'
    INVALID_CLAIMS = 'Ivalid claims. Please, check the audience and issuer.'
    UNABLE_TO_PARSE = 'Unable to parse authentication token.'
    INVALID_KEY = 'Unable to find the appropriate key.'
