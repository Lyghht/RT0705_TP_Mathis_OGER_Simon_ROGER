from flask import Blueprint, jsonify, request
from extensions import db
from models.media import Genre
from decorators import require_trusted_or_admin
from error_handler import (
    missing_field_error, already_exists_error, handle_api_error, handle_exception
)

genres_bp = Blueprint('genres', __name__)

@genres_bp.route('/<int:genre_id>', methods=['GET'])
def get_genre_by_id(genre_id):
    try:
        genre = Genre.query.get_or_404(genre_id)
        return jsonify(genre.to_dict()), 200
    except Exception as e:
        return handle_exception(e)

@genres_bp.route('', methods=['POST'])
@require_trusted_or_admin
def create_genre():
    try:
        data = request.json
        
        if not data.get('name'):
            return handle_api_error(missing_field_error('name'))
        
        if Genre.query.filter_by(name=data['name']).first():
            return handle_api_error(already_exists_error("genre", "name", data['name']))
        
        genre = Genre(name=data['name'])
        
        db.session.add(genre)
        db.session.commit()
        
        response = jsonify({
            'id': genre.id,
            'name': genre.name,
            'message': 'Genre créé avec succès'
        })
        response.status_code = 201
        response.headers['Location'] = f"/api/genres/{genre.id}"
        return response
    except Exception as e:
        return handle_exception(e)

@genres_bp.route('/<int:genre_id>', methods=['PATCH'])
@require_trusted_or_admin
def update_genre(genre_id):
    try:
        genre = Genre.query.get_or_404(genre_id)
        data = request.json
        
        if 'name' in data:
            existing_genre = Genre.query.filter_by(name=data['name']).first()
            if existing_genre and existing_genre.id != genre_id:
                return handle_api_error(already_exists_error("genre", "name", data['name']))
            genre.name = data['name']
        
        db.session.commit()
        
        return jsonify({
            'id': genre.id,
            'name': genre.name,
            'message': 'Genre modifié avec succès'
        }), 200
    except Exception as e:
        return handle_exception(e)

@genres_bp.route('/<int:genre_id>', methods=['DELETE'])
@require_trusted_or_admin
def delete_genre(genre_id):
    try:
        genre = Genre.query.get_or_404(genre_id)
        db.session.delete(genre)
        db.session.commit()
        
        return jsonify({"message": "Genre supprimé avec succès"}), 200
    except Exception as e:
        return handle_exception(e)

