from flask import Blueprint, render_template, request
from utils.utils_api import api_get, api_search

persons_bp = Blueprint('persons', __name__)

#PAGE PERSONNES
@persons_bp.route('/', methods=['GET'])
def persons():
    search_query = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    
    person_items = []
    pagination = {}
    messages=None
    
    person_items, pagination = api_search('persons', search_query, page, 25)
    if not person_items and not pagination:
        messages = ['danger', 'Erreur lors du chargement des personnes']
    
    return render_template('persons.html', person_items=person_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)


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
        pass
    
    return render_template('person.html', person_data=person_data, media_items=media_items)