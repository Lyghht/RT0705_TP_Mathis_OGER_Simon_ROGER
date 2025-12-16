from flask import Blueprint, jsonify, request
from extensions import db
from models.media import Franchise
from decorators import require_trusted_or_admin
from error_handler import missing_field_error, handle_api_error, handle_exception

franchises_bp = Blueprint('franchises', __name__)


@franchises_bp.route('/<int:franchise_id>', methods=['GET'])
def get_franchise_by_id(franchise_id):
    try:
        franchise = Franchise.query.get_or_404(franchise_id)
        return jsonify(franchise.to_dict()), 200
    except Exception as e:
        return handle_exception(e)

@franchises_bp.route('', methods=['POST'])
@require_trusted_or_admin
def create_franchise():
    try:
        data = request.json
        
        if not data.get('name'):
            return handle_api_error(missing_field_error('name'))
        
        franchise = Franchise(
            name=data['name'],
            description=data.get('description')
        )
        
        db.session.add(franchise)
        db.session.commit()
        
        response = jsonify({
            'id': franchise.id,
            'name': franchise.name,
            'message': 'Franchise créée avec succès'
        })
        response.status_code = 201
        response.headers['Location'] = f"/api/franchises/{franchise.id}"
        return response
    except Exception as e:
        return handle_exception(e)

@franchises_bp.route('/<int:franchise_id>', methods=['PATCH'])
@require_trusted_or_admin
def update_franchise(franchise_id):
    try:
        franchise = Franchise.query.get_or_404(franchise_id)
        data = request.json
        
        if 'name' in data:
            franchise.name = data['name']
        if 'description' in data:
            franchise.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'id': franchise.id,
            'name': franchise.name,
            'message': 'Franchise modifiée avec succès'
        }), 200
    except Exception as e:
        return handle_exception(e)

@franchises_bp.route('/<int:franchise_id>', methods=['DELETE'])
@require_trusted_or_admin
def delete_franchise(franchise_id):
    try:
        franchise = Franchise.query.get_or_404(franchise_id)
        db.session.delete(franchise)
        db.session.commit()
        
        return jsonify({"message": "Franchise supprimée avec succès"}), 200
    except Exception as e:
        return handle_exception(e)

