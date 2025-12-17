from flask import Blueprint, render_template, request
from utils.utils_api import api_get
from utils.utils import get_generic_view

persons_bp = Blueprint('persons', __name__)

#PAGE PERSONNES
@persons_bp.route('/', methods=['GET'])
def persons():
    person_items, pagination, search_query, page, messages = get_generic_view(request, 'persons', 25)
    return render_template('persons/persons.html', person_items=person_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)


#PAGE PERSONNE DETAILLEE
@persons_bp.route('/<int:person_id>', methods=['GET'])
def person(person_id):
    person_data = None
    media_items = []
    
    try:
        response = api_get(f'/persons/{person_id}')
        if response.status_code == 200:
            person_data = response.json()
        
        response = api_get(f'/persons/{person_id}/media')
        if response.status_code == 200:
            media_items = response.json()
    except:
        return render_template('error.html', error_code=404, error_message="Impossible de charger les informations"), 500
    
    return render_template('persons/person.html', person_data=person_data, media_items=media_items)