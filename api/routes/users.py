from flask import Blueprint, jsonify, request
from argon2 import PasswordHasher
from extensions import db
from models.users import User
from decorators import require_admin, require_self_or_admin, can_view_library
from models.libraries import Library
from jwt_utils import get_current_user
from error_handler import (
    missing_fields_error, already_exists_error, authorization_error,
    handle_api_error, handle_exception
)

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    try:
        user = User.query.get_or_404(user_id)
        current_user = get_current_user()
        is_admin = current_user is not None and current_user.role == "admin"
        user_data = user.to_dict(is_admin)
        return jsonify(user_data), 200
    except Exception as e:
        return handle_exception(e)

@users_bp.route('', methods=['POST'])
@require_admin
def create_user():
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
            role=data.get('role', 'user')  # Admin peut définir le rôle
        )
        
        db.session.add(user)
        db.session.commit()
        
        response = jsonify({
            'id': user.id,
            'email': user.email,
            'message': 'Utilisateur créé avec succès'
        })
        response.status_code = 201
        response.headers['Location'] = f"/api/users/{user.id}"
        return response
    except Exception as e:
        return handle_exception(e)

@users_bp.route('/<int:user_id>', methods=['PATCH'])
@require_self_or_admin
def update_user(user_id):
    try:
        user = User.query.get_or_404(user_id)
        current_user = request.current_user
        data = request.json
        
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            # converti l'email en lowercase
            email = data['email'].lower()
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and existing_user.id != user_id:
                return handle_api_error(already_exists_error("utilisateur", "email", email))
            user.email = email
        if 'password' in data and data['password']:
            argon2_hash = PasswordHasher()
            user.password = argon2_hash.hash(data['password'])
        if 'bio' in data:
            user.bio = data['bio']
        if 'role' in data:
            if current_user.role == 'admin':
                user.role = data['role']
            else:
                return handle_api_error(authorization_error("Seul un admin peut modifier le rôle"))
        
        db.session.commit()
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'message': 'Utilisateur modifié avec succès'
        }), 200
    except Exception as e:
        return handle_exception(e)

@users_bp.route('/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    try:

        # se supprimer sois même qu'elle idée ?
        if user_id == get_current_user().id:
            return jsonify({"message": "Vous ne pouvez pas vous supprimer vous-même"}), 403

        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "Utilisateur supprimé avec succès"}), 200
    except Exception as e:
        return handle_exception(e)

@users_bp.route('/<int:user_id>/libraries', methods=['GET'])
def get_user_libraries(user_id):
    try:
        User.query.get_or_404(user_id)
        current_user = get_current_user()
        libraries = Library.query.filter_by(owner_id=user_id).all()
        
        # voir uniquement les vidéothèques publiques ou celles ou on est propriétaire/admin
        filtered_libraries = [lib for lib in libraries if can_view_library(current_user, lib)]
        
        return jsonify([lib.to_dict() for lib in filtered_libraries]), 200
    except Exception as e:
        return handle_exception(e)