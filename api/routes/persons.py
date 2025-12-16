from flask import Blueprint, jsonify, request
from extensions import db
from models.persons import Person, MediaPerson
from decorators import require_trusted_or_admin, can_view_media
from jwt_utils import get_current_user
from error_handler import missing_field_error, handle_api_error, handle_exception

persons_bp = Blueprint('persons', __name__)

@persons_bp.route('/<int:person_id>', methods=['GET'])
def get_person_by_id(person_id):
    try:
        person = Person.query.get_or_404(person_id)
        return jsonify(person.to_dict()), 200
    except Exception as e:
        return handle_exception(e)

@persons_bp.route('', methods=['POST'])
@require_trusted_or_admin
def create_person():
    try:
        data = request.json
        
        if not data.get('name'):
            return handle_api_error(missing_field_error('name'))
        
        person = Person(
            name=data['name'],
            birthdate=data.get('birthdate')
        )
        
        db.session.add(person)
        db.session.commit()
        
        response = jsonify({
            'id': person.id,
            'name': person.name,
            'message': 'Personne créée avec succès'
        })
        response.status_code = 201
        response.headers['Location'] = f"/api/persons/{person.id}"
        return response
    except Exception as e:
        return handle_exception(e)

@persons_bp.route('/<int:person_id>', methods=['PATCH'])
@require_trusted_or_admin
def update_person(person_id):
    try:
        person = Person.query.get_or_404(person_id)
        data = request.json
        
        if 'name' in data:
            person.name = data['name']
        if 'birthdate' in data:
            person.birthdate = data['birthdate'] if data['birthdate'] else None
        
        db.session.commit()
        
        return jsonify({
            'id': person.id,
            'name': person.name,
            'message': 'Personne modifiée avec succès'
        }), 200
    except Exception as e:
        return handle_exception(e)

@persons_bp.route('/<int:person_id>', methods=['DELETE'])
@require_trusted_or_admin
def delete_person(person_id):
    try:
        person = Person.query.get_or_404(person_id)
        db.session.delete(person)
        db.session.commit()
        
        return jsonify({"message": "Personne supprimée avec succès"}), 200
    except Exception as e:
        return handle_exception(e)

@persons_bp.route('/<int:person_id>/media', methods=['GET'])
def get_person_media(person_id):
    try:
        # Vérifier que la personne existe
        Person.query.get_or_404(person_id)
        
        user = get_current_user()
        
        # Récupération des relations MediaPerson pour cette personne
        media_persons = MediaPerson.query.filter_by(person_id=person_id).all()
        
        # Filtrage selon les permissions et construction de la réponse
        result = []
        for mp in media_persons:
            if can_view_media(user, mp.media):
                media_data = mp.media.to_dict_summary()
                # Ajout des infos du rôle
                media_data['role'] = mp.role
                media_data['character_name'] = mp.character_name
                result.append(media_data)

        return jsonify(result), 200
    except Exception as e:
        return handle_exception(e)