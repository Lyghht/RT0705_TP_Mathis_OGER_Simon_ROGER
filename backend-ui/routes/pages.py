from flask import Blueprint, render_template, request
from utils.utils import get_current_user, get_generic_view
from utils.utils_api import api_get

pages_bp = Blueprint('pages', __name__)

#PAGE ACCUEIL
@pages_bp.route('/', methods=['GET'])
def home():
    library_items = []
    pagination = {}
    stats = {'media': 0, 'libraries': 0}
    current_user = get_current_user()
    media_random = None
    
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    
    try:
        # stats du site pour l'affichage de l'acceuil
        response = api_get('/search/stats')
        if response.status_code == 200:
            stats_data = response.json()
            stats['media'] = stats_data.get('media', 0)
            stats['libraries'] = stats_data.get('libraries', 0)
        
        # Récupérer les biblio de l'utilisateur avec pagination s'il est connecté
        if current_user:
            response = api_get(f'/search/libraries?owner_id={current_user.get("id")}&page={page}&per_page=12')
            if response.status_code == 200:
                data = response.json()
                library_items = data.get('data', [])
                pagination = data.get('pagination', {})

            response = api_get(f'/media/random')
            if response.status_code == 200:
                media_random = response.json()
    except:
        return render_template('error.html', error_code=404, error_message="Impossible de charger les informations"), 500
    
    return render_template('index.html', library_items=library_items, pagination=pagination, stats=stats, current_page=page, media_random=media_random)

#PAGE USERS
@pages_bp.route('/users', methods=['GET'])
def users():
    user_items, pagination, search_query, page, messages = get_generic_view(request, 'users', 20)
    return render_template('users.html', user_items=user_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)


#PAGE GENRES
@pages_bp.route('/genres', methods=['GET'])
def genres():
    genre_items, pagination, search_query, page, messages = get_generic_view(request, 'genres', 30)
    return render_template('genres.html', genre_items=genre_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)