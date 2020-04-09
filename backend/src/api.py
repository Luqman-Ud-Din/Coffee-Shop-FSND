import json

from flask import Flask, request, jsonify, abort
from flask_cors import CORS

from backend.src.constants import StatusCode
from .auth.auth import AuthError, requires_auth
from .database.models import setup_db, Drink, db_drop_and_create_all

app = Flask(__name__)
setup_db(app)
CORS(app)


@app.after_request
def after_request(response):
    """
    Handler for after a request has been made.
    :param response:
    """
    response.headers.add(
        'Access-Control-Allow-Headers',
        'Content-Type, Authorization'
    )
    response.headers.add(
        'Access-Control-Allow-Methods',
        'GET, POST, PUT, PATCH, DELETE, OPTIONS'
    )
    return response


'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''


db_drop_and_create_all()


## ROUTES

@app.route('/drinks')
def list_drinks():
    """
    Get drinks api with short detail.
    :return:
    """

    return jsonify({
        'success': True,
        'drinks': [d.short() for d in Drink.query.all()]
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(token):
    """
    Get drinks api with long detail.
    :param token:
    :return:
    """

    return jsonify({
        'success': True,
        'drinks': [d.long() for d in Drink.query.all()]
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token):
    """
    Add new drink in the table.
    :param token:
    :return:
    """
    drink_data = request.get_json()
    drink_data['recipe'] = json.dumps(drink_data.get('recipe'))
    drink_data.pop('id', None)

    drink = Drink(**drink_data)
    drink.insert()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(token, drink_id):
    """
    Update drink by given drink id.
    :param token:
    :param drink_id:
    :return:
    """
    drink = Drink.query.filter_by(id=drink_id).first()
    if not drink:
        abort(StatusCode.HTTP_404_NOT_FOUND.value)

    drink_data = request.get_json()
    drink_data['recipe'] = json.dumps(drink_data.get('recipe'))

    drink.title = drink_data.get('title')
    drink.recipe = drink_data.get('recipe') or '{}'
    drink.update()

    return jsonify({
        'success': True,
        'drinks': [drink.long()]
    })


@app.route('/drinks/<drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(token, drink_id):
    """
    Delete drink by given drink id.
    :param token:
    :param drink_id:
    :return:
    """

    drink = Drink.query.filter_by(id=drink_id).first()
    if not drink:
        abort(StatusCode.HTTP_404_NOT_FOUND)

    drink.delete()

    return jsonify({
        'success': True,
        'delete': drink_id
    })


@app.errorhandler(StatusCode.HTTP_400_BAD_REQUEST.value)
def bad_request(error):
    """
    Error handler for bad request with status code 400.
    :param: error
    :return:
    """
    return jsonify({
        'success': False,
        'error': StatusCode.HTTP_400_BAD_REQUEST.value,
        'message': StatusCode.HTTP_400_BAD_REQUEST.name
    }), StatusCode.HTTP_400_BAD_REQUEST.value


@app.errorhandler(StatusCode.HTTP_401_UNAUTHORIZED.value)
def unauthorized(error):
    """
    Error handler for unauthorized with status code 401.
    :param: error
    :return:
    """
    return jsonify({
        'success': False,
        'error': StatusCode.HTTP_401_UNAUTHORIZED.value,
        'message': StatusCode.HTTP_401_UNAUTHORIZED.name
    }), StatusCode.HTTP_401_UNAUTHORIZED.value


@app.errorhandler(StatusCode.HTTP_403_FORBIDDEN.value)
def forbidden(error):
    """
    Error handler for forbidden with status code 403.
    :param: error
    :return:
    """
    return jsonify({
        'success': False,
        'error': StatusCode.HTTP_403_FORBIDDEN.value,
        'message': StatusCode.HTTP_403_FORBIDDEN.name
    }), StatusCode.HTTP_403_FORBIDDEN.value


@app.errorhandler(StatusCode.HTTP_404_NOT_FOUND.value)
def not_found(error):
    """
    Error handler for not found with status code 404.
    :param: error
    :return:
    """
    return jsonify({
        'success': False,
        'error': StatusCode.HTTP_404_NOT_FOUND.value,
        'message': StatusCode.HTTP_404_NOT_FOUND.name
    }), StatusCode.HTTP_404_NOT_FOUND.value


@app.errorhandler(StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value)
def method_not_allowed(error):
    """
    Error handler for method not allowed with status code 405.
    :param: error
    :return:
    """
    return jsonify({
        'success': False,
        'error': StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value,
        'message': StatusCode.HTTP_405_METHOD_NOT_ALLOWED.name
    }), StatusCode.HTTP_405_METHOD_NOT_ALLOWED.value


@app.errorhandler(StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value)
def unprocessable_entity(error):
    """
    Error handler for unprocessable entity with status code 422.
    :param: error
    :return:
    """
    return jsonify({
        'success': False,
        'error': StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value,
        'message': StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.name
    }), StatusCode.HTTP_422_UNPROCESSABLE_ENTITY.value


@app.errorhandler(StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value)
def internal_server_error(error):
    """
    Error handler for internal server error with status code 500.
    :param: error
    :return:
    """
    return jsonify({
        'success': False,
        'error': StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value,
        'message': StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.name
    }), StatusCode.HTTP_500_INTERNAL_SERVER_ERROR.value


@app.errorhandler(AuthError)
def auth_error(error):
    """
    Error handling for our custom auth error class.
    :param error:
    :return:
    """
    return jsonify(error.error), error.status_code
