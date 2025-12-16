from flask import Blueprint, jsonify, request
from extensions import db
from models.media import Media, Genre
from models.persons import Person, MediaPerson
from models.libraries import Library
from decorators import require_auth, require_owner_or_admin, can_view_media
from jwt_utils import get_current_user
from error_handler import (
    missing_fields_error, not_found_error, authorization_error,
    conflict_error, handle_api_error, handle_exception, APIError, ERROR_CODES
)
from random import choice

media_bp = Blueprint('media', __name__)


@media_bp.route('/<int:media_id>', methods=['GET'])
def get_media_by_id(media_id):
    try:
        media = Media.query.get_or_404(media_id)
        user = get_current_user()
        
        if not can_view_media(user, media):
            return handle_api_error(authorization_error("Accès refusé à ce média"))
        
        return jsonify(media.to_dict()), 200
    except Exception as e:
        return handle_exception(e)

@media_bp.route('', methods=['POST'])
@require_auth
def create_media():
    try:
        user = request.current_user
        data = request.json
        
        if not data.get('title') or not data.get('type') or not data.get('library_id') or not data.get('visibility'):
            return handle_api_error(missing_fields_error(['title', 'type', 'library_id', 'visibility']))
        
        library = Library.query.get_or_404(data['library_id'])
        
        if user.role != 'admin' and library.owner_id != user.id:
            return handle_api_error(authorization_error("Vous ne pouvez créer des médias que dans vos propres vidéothèques"))
        
        media = Media(
            title=data['title'],
            type=data['type'],
            release_year=data.get('release_year'),
            duration=data.get('duration'),
            synopsis=data.get('synopsis'),
            cover_image_url=data.get('cover_image_url'),
            trailer_url=data.get('trailer_url'),
            library_id=data['library_id'],
            franchise_id=data.get('franchise_id'),
            franchise_order=data.get('franchise_order'),
            visibility=data['visibility']
        )
        
        db.session.add(media)
        db.session.flush()
        
        if data.get('genres'):
            genre_ids = [int(g) for g in data['genres'] if g]
            genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
            media.genres = genres
        
        if data.get('persons'):
            for person_data in data['persons']:
                if person_data.get('person_id') and person_data.get('role'):
                    media_person = MediaPerson(
                        media_id=media.id,
                        person_id=person_data['person_id'],
                        role=person_data['role'],
                        character_name=person_data.get('character_name')
                    )
                    db.session.add(media_person)
        
        db.session.commit()
        
        response = jsonify({
            'id': media.id,
            'title': media.title,
            'message': 'Média créé avec succès'
        })
        response.status_code = 201
        response.headers['Location'] = f"/api/media/{media.id}"
        return response
    except Exception as e:
        return handle_exception(e)

@media_bp.route('/<int:media_id>', methods=['PATCH'])
@require_owner_or_admin
def update_media(media_id):
    try:
        media = Media.query.get_or_404(media_id)
        data = request.json
        
        # Validation des champs obligatoires si présents
        if 'title' in data and not data['title']:
            return handle_api_error(missing_fields_error(['title']))
        if 'type' in data and data['type'] not in ['film', 'serie']:
            return handle_api_error(APIError(
                code=ERROR_CODES['RESOURCE_CONFLICT'],
                message='Le type doit être "film" ou "serie"',
                status_code=400
            ))
        if 'visibility' in data and data['visibility'] not in ['public', 'private']:
            return handle_api_error(APIError(
                code=ERROR_CODES['RESOURCE_CONFLICT'],
                message='La visibilité doit être "public" ou "private"',
                status_code=400
            ))
        
        # Mise à jour des champs simples
        if 'title' in data:
            media.title = data['title']
        if 'type' in data:
            media.type = data['type']
        if 'release_year' in data:
            if data['release_year']:
                try:
                    media.release_year = int(data['release_year'])
                except (ValueError, TypeError):
                    return handle_api_error(APIError(
                        code=ERROR_CODES['RESOURCE_CONFLICT'],
                        message='release_year doit être un nombre entier',
                        status_code=400
                    ))
            else:
                media.release_year = None
        if 'duration' in data:
            # Duration peut être un entier (minutes) ou None
            if data['duration']:
                try:
                    media.duration = int(data['duration'])
                except (ValueError, TypeError):
                    return handle_api_error(APIError(
                        code=ERROR_CODES['RESOURCE_CONFLICT'],
                        message='duration doit être un nombre entier',
                        status_code=400
                    ))
            else:
                media.duration = None
        if 'synopsis' in data:
            media.synopsis = data['synopsis'] if data['synopsis'] else None
        if 'cover_image_url' in data:
            media.cover_image_url = data['cover_image_url'] if data['cover_image_url'] else None
        if 'trailer_url' in data:
            media.trailer_url = data['trailer_url'] if data['trailer_url'] else None
        if 'franchise_id' in data:
            if data['franchise_id']:
                try:
                    media.franchise_id = int(data['franchise_id'])
                except (ValueError, TypeError):
                    return handle_api_error(APIError(
                        code=ERROR_CODES['RESOURCE_CONFLICT'],
                        message='franchise_id doit être un nombre entier',
                        status_code=400
                    ))
            else:
                media.franchise_id = None
        if 'franchise_order' in data:
            if data['franchise_order']:
                try:
                    media.franchise_order = int(data['franchise_order'])
                except (ValueError, TypeError):
                    return handle_api_error(APIError(
                        code=ERROR_CODES['RESOURCE_CONFLICT'],
                        message='franchise_order doit être un nombre entier',
                        status_code=400
                    ))
            else:
                media.franchise_order = None
        if 'visibility' in data:
            media.visibility = data['visibility']
        
        # Mise à jour des genres avec validation
        if 'genres' in data:
            try:
                genre_ids = [int(genre_id) for genre_id in data['genres'] if genre_id]
            except (ValueError, TypeError) as e:
                db.session.rollback()
                return handle_api_error(APIError(
                    code=ERROR_CODES['RESOURCE_CONFLICT'],
                    message='Les IDs de genres doivent être des nombres entiers',
                    status_code=400
                ))
            
            if genre_ids:
                genres = Genre.query.filter(Genre.id.in_(genre_ids)).all()
                # Vérifier que tous les genres demandés existent
                found_ids = {g.id for g in genres}
                missing_ids = []

                for g_id in genre_ids:
                    if g_id not in found_ids:
                        missing_ids.append(g_id)

                if missing_ids:
                    db.session.rollback()
                    return handle_api_error(not_found_error("genre", missing_ids[0]))
                media.genres = genres
            else:
                # Liste vide = supprimer tous les genres
                media.genres = []
        
        # Mise à jour des personnes
        if 'persons' in data:
            # Supprimer les relations existantes de manière sécurisée
            existing_persons = MediaPerson.query.filter_by(media_id=media_id).all()
            for existing in existing_persons:
                db.session.delete(existing)
            
            # Ajouter les nouvelles relations
            for person_data in data['persons']:
                person_id = person_data.get('person_id')
                role = person_data.get('role')
                
                # Validation: person_id et role sont obligatoires
                if not person_id or not role:
                    continue
                
                # Convertir person_id en int de manière sécurisée
                try:
                    person_id = int(person_id)
                except (ValueError, TypeError):
                    db.session.rollback()
                    return handle_api_error(APIError(
                        code=ERROR_CODES['RESOURCE_CONFLICT'],
                        message='person_id doit être un nombre entier',
                        status_code=400
                    ))
                
                # Vérifier que la personne existe
                person = Person.query.get(person_id)
                if not person:
                    db.session.rollback()
                    return handle_api_error(not_found_error("person", person_id))
                
                # Nettoyer role (supprimer les espaces)
                role = role.strip() if role else None
                if not role:
                    continue
                
                # Nettoyer character_name (None si vide)
                character_name = person_data.get('character_name')
                if character_name and character_name.strip():
                    character_name = character_name.strip()
                else:
                    character_name = None
                
                media_person = MediaPerson(
                    media_id=media_id,
                    person_id=person_id,
                    role=role,
                    character_name=character_name
                )
                db.session.add(media_person)
        
        db.session.commit()
        
        return jsonify({
            'id': media.id,
            'title': media.title,
            'message': 'Média modifié avec succès'
        }), 200
    except ValueError as e:
        db.session.rollback()
        return handle_api_error({'error': f'Erreur de validation: {str(e)}'})
    except Exception as e:
        db.session.rollback()
        return handle_exception(e)

@media_bp.route('/<int:media_id>', methods=['DELETE'])
@require_owner_or_admin
def delete_media(media_id):
    try:
        media = Media.query.get_or_404(media_id)
        db.session.delete(media)
        db.session.commit()
        
        return jsonify({"message": "Média supprimé avec succès"}), 200
    except Exception as e:
        return handle_exception(e)


@media_bp.route('/<int:media_id>/persons', methods=['GET'])
def get_media_persons(media_id):
    """Récupère la liste des personnes associées à un média."""
    try:
        media = Media.query.get_or_404(media_id)
        user = get_current_user()
        
        if not can_view_media(user, media):
            return handle_api_error(authorization_error("Accès refusé à ce média"))
        
        return jsonify([mp.to_dict() for mp in media.cast]), 200
    except Exception as e:
        return handle_exception(e)

@media_bp.route('/<int:media_id>/persons', methods=['POST'])
@require_owner_or_admin
def add_media_person(media_id):
    try:
        data = request.json
        
        if not data.get('person_id') or not data.get('role'):
            return handle_api_error(missing_fields_error(['person_id', 'role']))
        
        person = Person.query.get_or_404(data['person_id'])
        
        existing = MediaPerson.query.filter_by(
            media_id=media_id,
            person_id=data['person_id'],
            role=data['role']
        ).first()
        
        if existing:
            return handle_api_error(conflict_error("Cette personne avec ce rôle est déjà associée à ce média", "media_person"))
        
        media_person = MediaPerson(
            media_id=media_id,
            person_id=data['person_id'],
            role=data['role'],
            character_name=data.get('character_name')
        )
        
        db.session.add(media_person)
        db.session.commit()
        
        response = jsonify({
            'person_id': media_person.person_id,
            'person_name': person.name,
            'role': media_person.role,
            'message': 'Personne ajoutée avec succès'
        })
        response.status_code = 201
        response.headers['Location'] = f"/api/media/{media_id}/persons/{media_person.person_id}/{media_person.role}"
        return response
    except Exception as e:
        return handle_exception(e)

@media_bp.route('/<int:media_id>/persons/<int:person_id>/<role>', methods=['DELETE'])
@require_owner_or_admin
def remove_media_person(media_id, person_id, role):
    try:
        media_person = MediaPerson.query.filter_by(
            media_id=media_id,
            person_id=person_id,
            role=role
        ).first_or_404()
        
        db.session.delete(media_person)
        db.session.commit()
        
        return jsonify({"message": "Personne retirée avec succès"}), 200
    except Exception as e:
        return handle_exception(e)    

@media_bp.route('/random', methods=['GET'])
def get_random_movie():
    try:
        user = get_current_user()

        user_media = Media.query.join(Library).filter(Library.owner_id == user.id).all()

        if not user_media:
            return handle_api_error(not_found_error("media", "Aucun média trouvé"))

        return jsonify(choice(user_media).to_dict()), 200
    except Exception as e:
        return handle_exception(e)