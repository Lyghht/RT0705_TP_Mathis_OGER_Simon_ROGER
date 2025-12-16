from flask import Blueprint, jsonify, request
from extensions import db
from models.libraries import Library
from decorators import require_auth, require_owner_or_admin, can_view_library
from jwt_utils import get_current_user
from decorators import can_view_media
from models.media import Media
from error_handler import (
    missing_field_error, authorization_error, handle_api_error, handle_exception
)

libraries_bp = Blueprint('libraries', __name__)


@libraries_bp.route('/<int:library_id>/media', methods=['GET'])
def get_library_media(library_id):
    """Récupère la liste des médias d'une vidéothèque avec filtrage par permissions."""
    try:
        library = Library.query.get_or_404(library_id)
        user = get_current_user()
        
        if not can_view_library(user, library):
            return handle_api_error(authorization_error("Accès refusé à cette vidéothèque"))
        
        all_medias = Media.query.filter_by(library_id=library_id).all()
        
        # Filtrage selon les permissions
        visible_medias = [media for media in all_medias if can_view_media(user, media)]
        
        return jsonify([media.to_dict_summary() for media in visible_medias]), 200
    except Exception as e:
        return handle_exception(e)

@libraries_bp.route('/<int:library_id>', methods=['GET'])
def get_library_by_id(library_id):
    try:
        library = Library.query.get_or_404(library_id)
        user = get_current_user()
        
        if not can_view_library(user, library):
            return handle_api_error(authorization_error("Accès refusé à cette vidéothèque"))
        
        return jsonify(library.to_dict()), 200
    except Exception as e:
        return handle_exception(e)

@libraries_bp.route('', methods=['POST'])
@require_auth
def create_library():
    try:
        user = request.current_user
        data = request.json
        
        if not data.get('name'):
            return handle_api_error(missing_field_error('name'))
        
        # L'owner_id est automatiquement défini à l'utilisateur connecté (sauf si admin car il peut créer pour les autes)
        owner_id = user.id
        if user.role == 'admin' and data.get('owner_id'):
            owner_id = data['owner_id']
        
        library = Library(
            name=data['name'],
            description=data.get('description'),
            owner_id=owner_id,
            visibility=data.get('visibility', 'private')
        )
        
        db.session.add(library)
        db.session.commit()
        
        response = jsonify({
            'id': library.id,
            'name': library.name,
            'message': 'Vidéothèque créée avec succès'
        })
        response.status_code = 201
        response.headers['Location'] = f"/api/libraries/{library.id}"
        return response
    except Exception as e:
        return handle_exception(e)

@libraries_bp.route('/<int:library_id>', methods=['PATCH'])
@require_owner_or_admin
def update_library(library_id):
    try:
        library = Library.query.get_or_404(library_id)
        user = request.current_user
        data = request.json
        
        if 'name' in data:
            library.name = data['name']
        if 'description' in data:
            library.description = data['description']
        if 'owner_id' in data:
            # Seul un admin peut changer le propriétaire
            if user.role == 'admin':
                library.owner_id = data['owner_id']
            else:
                return handle_api_error(authorization_error("Seul un admin peut changer le propriétaire"))
        if 'visibility' in data:
            library.visibility = data['visibility']
        
        db.session.commit()
        
        return jsonify({
            'id': library.id,
            'name': library.name,
            'message': 'Vidéothèque modifiée avec succès'
        }), 200
    except Exception as e:
        return handle_exception(e)

@libraries_bp.route('/<int:library_id>', methods=['DELETE'])
@require_owner_or_admin
def delete_library(library_id):
    try:
        library = Library.query.get_or_404(library_id)
        db.session.delete(library)
        db.session.commit()
        
        return jsonify({"message": "Vidéothèque supprimée avec succès"}), 200
    except Exception as e:
        return handle_exception(e)

