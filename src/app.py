"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from werkzeug.security import generate_password_hash
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)




# ---------------------Endpoints---------------------#

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.serialize() for user in users]), 200

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({
            "msg": 'user not found'
        }), 404
    return jsonify(user.serialize()), 200

@app.route('/users', methods=['POST'])
def add_user():
    email = request.json.get('email')
    username = request.json.get('username')
    password = request.json.get('password')
    if not email or not username or not password:
        return jsonify ({
            'msg': 'Email, username, and password are required'
        }), 400
    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        return jsonify({"msg": "Email or username already exists"}), 400
    hashed_password = generate_password_hash(password)
    user = User(email=email, username=username, password=hashed_password)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.serialize()), 201

@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({
            'msg': 'User not found'
        }), 404
    email = request.json.get('email', user.email)
    username = request.json.get('username', user.username)
    password = request.json.get('password')
    existing_user = User.query.filter(
        ((User.email == email) | (User.username == username)) & (User.id != user_id)
    ).first()
    if existing_user:
        return jsonify({"msg": "Email or username already exists"}), 400
    user.email = email
    user.username = username
    if password:
        user.password_hash = generate_password_hash(password)
    db.session.commit()
    return jsonify(user.serialize()), 200

@app.route('/users/<int:user_id>', methods=['DELETE'])
def remove_user(user_id):
    user = User.query.get(user_id)
    if user is None:
        return jsonify ({
            'msg': 'User not found'
        }), 404
    db.session.delete(user)
    db.session.commit()
    return jsonify({'msg': 'User deleted'}), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    favorites = Favorite.query.filter_by(user_id=user_id).all()
    return jsonify([favorite.serialize() for favorite in favorites]), 200

@app.route('/people', methods=['GET'])
def get_people():
    characters = Character.query.all()
    return jsonify([character.serialize() for character in characters]), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_person(people_id):
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({
            "msg": 'Character not found'
        }), 404
    return jsonify(character.serialize()), 200

@app.route('/people', methods=['POST'])
def add_person():
    name = request.json.get('name')
    description = request.json.get('description')
    if not name:
        return jsonify({
            "msg": 'Name is required'
        }), 400
    character = Character(name=name, description=description)
    db.session.add(character)
    db.session.commit()
    return jsonify(character.serialize()), 201

@app.route('/people/<int:people_id>', methods=['PUT'])
def update_person(people_id):
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({
            "msg": 'Character not found'
        }), 404
    character.name = request.json.get('name', character.name)
    character.description = request.json.get('description', character.description)
    db.session.commit()
    return jsonify(character.serialize()), 200

@app.route('/people/<int:people_id>', methods=['DELETE'])
def delete_person(people_id):
    character = Character.query.get(people_id)
    if character is None:
        return jsonify({
            "msg": 'Character not found'
        }), 404
    db.session.delete(character)
    db.session.commit()
    return jsonify({"msg": "Character deleted"}), 200

@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    return jsonify([planet.serialize() for planet in planets]), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({
            "msg": 'Planet not found'
        }), 404
    return jsonify(planet.serialize()), 200

@app.route('/planets', methods=['POST'])
def add_planet():
    name = request.json.get('name')
    description = request.json.get('description')
    if not name:
        return jsonify({
            "msg": 'Name is required'
        }), 400
    planet = Planet(name=name, description=description)
    db.session.add(planet)
    db.session.commit()
    return jsonify(planet.serialize()), 201

@app.route('/planets/<int:planet_id>', methods=['PUT'])
def update_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({
            "msg": 'Planet not found'
        }), 404
    planet.name = request.json.get('name', planet.name)
    planet.description = request.json.get('description', planet.description)
    db.session.commit()
    return jsonify(planet.serialize()), 200

@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        return jsonify({
            "msg": 'Planet not found'
        }), 404
    db.session.delete(planet)
    db.session.commit()
    return jsonify({"msg": "Planet deleted"}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
