from flask import Blueprint, render_template, request
from utils.utils import api_get

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
    
    try:
        response = api_get(f'/search/persons?q={search_query}&page={page}&per_page=25')
        if response.status_code == 200:
            data = response.json()
            person_items = data.get('data', [])
            pagination = data.get('pagination', {})
    except:
        pass
    
    return render_template('persons.html', person_items=person_items, pagination=pagination, search_query=search_query, current_page=page)


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