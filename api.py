import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink, Cake
from .auth.auth import AuthError, requires_auth


def create_app(test=False):
    app = Flask(__name__)
    # app.config.from_object('config')
    setup_db(app)
    # if not test:
    #     setup_db(app)

    CORS(app, resources={r"api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Headers', 'GET, POST, PATCH, DELETE, OPTIONS')
        return response

    # ROUTES
    '''
    Sample Endpoint: To test if the app is up and running
    '''

    @app.route('/', methods=['GET'])
    def get_init():
        return jsonify({
            'success': True,
            'SampleTest': 'The app is runing'
        })

    @app.route('/drinks', methods=['GET'])
    def get_drinks(payload=None):
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify ({
            "success": True,
            "drinks": [drink.short() for drink in drinks],
        }), 200

    @app.route('/drinks-detail', methods=['GET'])
    @requires_auth(permission='get:drinks-detail')
    def get_drinks_detail(payload=None):
        drinks = Drink.query.order_by(Drink.id).all()

        return jsonify({
            'success': True,
            'drinks': [drink.long() for drink in drinks],
        }), 200

    @app.route('/drinks',methods=['POST'])
    @requires_auth(permission='post:drinks')
    def create_drink(payload):
        body = request.get_json()

        try:
            recipe = body['recipe']
            if isinstance(recipe, dict):
                recipe = [recipe]

            drink = Drink()
            drink.title = body['title']
            drink.recipe = json.dumps(recipe)
            drink.insert()
            return jsonify({
                "success": True,
                "drink": [drink.long()]
            }), 200
        
        except Exception as ex:
            print(ex)
            abort(400)

    @app.route('/drinks/<int:drink_id>',methods=['PATCH'])
    @requires_auth(permission='patch:drinks')
    def update_drink(payload,drink_id):
        body = request.get_json()
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
        print(body)
        if drink is None:
            abort(404)
        try: 

            if 'title' in body:
                drink.title = body['title']

            if 'recipe' in body:
                drink.recipe = json.dumps(body['recipe'])
            
            drink.update()

            return jsonify({
                "success": True,
                "drinks": [drink.long()]
            }), 200
        
        except Exception as ex:
            print(ex)
            abort(400)
        
    @app.route('/drinks/<int:drink_id>', methods=['DELETE'])
    @requires_auth('delete:drinks')
    def delete_drink(payload,drink_id):
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)
        try:
            drink.delete()

            return jsonify({
                "success": True,
                "deleted": drink_id
            })
        except Exception as ex:
            print(ex)
            abort(400)

    @app.route('/cakes', methods=['GET'])
    @requires_auth(permission="get:cakes")
    def get_cakes(payload=None):
        cakes = Cake.query.order_by(Cake.id).all()

        return jsonify ({
            "success": True,
            "cakes": [cake.format() for cake in cakes],
        }), 200

    @app.route('/cakes',methods=['POST'])
    @requires_auth(permission='post:cakes')
    def create_cake(payload):
        body = request.get_json()

        try:
            cake = Cake()
            cake.name = body['name']
            cake.description = body['description']
            cake.insert()
            return jsonify({
                "success": True,
                "cake": [cake.long()]
            }), 200
        
        except Exception as ex:
            print(ex)
            abort(400)

    @app.route('/cakes/<int:cake_id>',methods=['PATCH'])
    @requires_auth(permission='patch:cakes')
    def update_cake(payload,cake_id):
        body = request.get_json()
        cake = Cake.query.filter(Cake.id == cake_id).one_or_none()
        print(body)
        if cake is None:
            abort(404)
        try: 

            if 'name' in body:
                cake.name = body['name']

            if 'description' in body:
                cake.description = body['description']
            
            cake.update()

            return jsonify({
                "success": True,
                "cakes": [cake.format()]
            }), 200
        
        except Exception as ex:
            print(ex)
            abort(400)
        
    @app.route('/cakes/<int:cake_id>', methods=['DELETE'])
    @requires_auth('delete:cakes')
    def delete_cake(payload,cake_id):
        cake = Cake.query.filter(Cake.id == cake_id).one_or_none()

        if cake is None:
            abort(404)
        try:
            cake.delete()

            return jsonify({
                "success": True,
                "deleted": cake_id
            })
        except Exception as ex:
            print(ex)
            abort(400)

    # Error Handling

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422



    @app.errorhandler(404)
    def notfound(error):
        return jsonify({
            "success": False,
            "message": "resource not found",
            "error": 404
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": error.error
        }), 400

    @app.errorhandler(AuthError)
    def auth_error(error):
        return jsonify({
            "success": False,
            "error": error.status_code,
            "message": error.error
        }), error.status_code
    
    return app
    
app = create_app()

with app.app_context():
    db_drop_and_create_all()

if __name__ == '__main__':
    app.run(debug=True)