from flask import Blueprint, render_template, request
from utils.utils_api import api_get
from utils.utils import get_generic_view, get_int_or_default

franchises_bp = Blueprint('franchises', __name__)

#PAGE FRANCHISES
@franchises_bp.route('/', methods=['GET'])
def franchises():
    franchise_items, pagination, search_query, page, messages = get_generic_view(request, 'franchises', 20)    
    return render_template('franchises/franchises.html', franchise_items=franchise_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)

#PAGE FRANCHISE MEDIA
@franchises_bp.route('/<int:franchise_id>/media', methods=['GET'])
def franchise_media(franchise_id):
    franchise_data = None
    media_items = []
    pagination = {}
    messages = None

    page = get_int_or_default(request.args.get('page', 1), 1)

    try:
        response = api_get(f'/franchises/{franchise_id}')
        if response.status_code == 200:
            franchise_data = response.json()
        else:
            messages = ['danger', 'Erreur lors du chargement']

        response = api_get(f'/search/media?q=&franchise_id={franchise_id}&page={page}&per_page=24')
        if response.status_code == 200:
            data = response.json()
            media_items = data.get('data', [])
            pagination = data.get('pagination', {})
        else:
            messages = ['danger', 'Erreur lors du chargement']
    except:
        messages = ['danger', 'Erreur lors du chargement']

    return render_template('franchises/franchise-media.html', franchise_data=franchise_data, media_items=media_items, pagination=pagination, current_page=page, messages=messages)