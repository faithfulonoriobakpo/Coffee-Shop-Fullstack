import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)


# db_drop_and_create_all()

# Get drinks endpoint
@app.route('/drinks')
def get_drinks():
    try:
        drinks_record = Drink.query.all()
        drinks = [drink.short() for drink in drinks_record]

        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)
        
# Get drinks detail endpoint
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(jwt):
    try:
        drinks_record = Drink.query.all()
        drinks = [drink.long() for drink in drinks_record]

        return jsonify({
            'success': True,
            'drinks': drinks
        })
    except:
        abort(404)

# Add drinks endpoint
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    body = request.get_json()

    try:
        title = body.get('title')
        recipe = body.get('recipe')

        drink = Drink(title=title, recipe=json.dumps([recipe]))
        drink.insert()

        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except:
        abort(422)


# Edit drink endpoint
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, id):

    drink = Drink.query.get(id)

    if drink is not None:
        try:
            body = request.get_json()
            title = body.get('title')
            recipe = body.get('recipe')

            drink.title = title
            drink.recipe = recipe if type(recipe) == str else json.dumps(recipe)

            drink.update()

            return jsonify({
                'success': True,
                'drinks': [drink.long()]
            })
        except:
            abort(422)
    else:
        abort(404)


# Delete drink endpoint
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, id):

    drink = Drink.query.get(id)

    if drink is not None:
        try:
            drink.delete()

            return jsonify({
                'success': True,
                'delete': drink.id
            })
        except:
            abort(422)
    else:
        abort(404)

# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': 'resource not found'
    }), 404


@app.errorhandler(AuthError)
def authentication_error(auth_error):
    return jsonify({
        'success': False,
        'error': auth_error.status_code,
        'message': auth_error.error
    }), auth_error.status_code
