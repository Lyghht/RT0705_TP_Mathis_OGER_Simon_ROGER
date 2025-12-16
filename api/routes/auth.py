from flask import Blueprint, jsonify, request
from argon2 import PasswordHasher
from extensions import db
from models.users import User
from jwt_utils import generate_token
from decorators import require_auth
from error_handler import (
    missing_fields_error, already_exists_error, authentication_error,
    handle_api_error, handle_exception
)

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return handle_api_error(missing_fields_error(['email', 'password']))
        
        email = data['email'].lower()
        
        if User.query.filter_by(email=email).first():
            return handle_api_error(already_exists_error("utilisateur", "email", email))
        argon2_hash = PasswordHasher()

        user = User(
            username=data.get('username'),
            email=email,
            password=argon2_hash.hash(data['password']),
            bio=data.get('bio'),
            role='user'  # Rôle par défaut
        )
        
        db.session.add(user)
        db.session.commit()
        
        token = generate_token(user)
        
        response = jsonify({
            'token': token,
            'message': 'Inscription réussie'
        })
        response.status_code = 201
        response.headers['Location'] = f"/api/users/{user.id}"
        return response
    except Exception as e:
        return handle_exception(e)

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return handle_api_error(missing_fields_error(['email', 'password']))
        
        email = data['email'].lower()
        user = User.query.filter_by(email=email).first()
        
        argon2_hash = PasswordHasher()
        if not user or not argon2_hash.verify(user.password, data['password']):
            return handle_api_error(authentication_error("Email ou mot de passe incorrect"))
        
        token = generate_token(user)
        
        response = jsonify({
            'token': token,
            'message': 'Connexion réussie'
        })
        return response
    except Exception as e:
        return handle_exception(e)

@auth_bp.route('/me', methods=['GET'])
@require_auth
def get_current_user_info():
    try:
        user = request.current_user
        return jsonify(user.to_dict()), 200
    except Exception as e:
        return handle_exception(e)