from flask import Blueprint, render_template, request, redirect
from utils.utils import get_current_user, get_url_embed_youtube, upload_cover_image, get_persons_post_data, get_data_for_media, get_int_or_default
from utils.utils_api import api_get, api_post, api_search
from utils.tmdb_api import api_tmdb_search_film, api_tmdb_get_film, api_tmdb_search_series, api_tmdb_get_series

add_media_bp = Blueprint('add_media', __name__)

#Page d'ajout média
@add_media_bp.route('/', methods=['GET'])
def add_media():
    current_user = get_current_user()
    if not current_user:
        return redirect('/login')

    search_query = request.args.get('q', '')
    table_type = request.args.get('table', '')
    search_results = []
    pagination = {}
    page = get_int_or_default(request.args.get('page', 1), 1)

    try:
        if search_query and (table_type in ["externe_film", "externe_series", "interne"]):
            if table_type == 'externe_film':
                response = api_tmdb_search_film(search_query, page)
                if response:
                    search_results = response['data']
                    pagination = response['pagination']
            elif table_type == 'externe_series':
                response = api_tmdb_search_series(search_query, page)
                if response:
                    search_results = response['data']
                    pagination = response['pagination']
            else:
                search_results, pagination = api_search('media', search_query, page, 20)
    except:
        return render_template('error.html', error_code=500, error_message="Impossible de charger les informations"), 500
    
    return render_template('add-media/add-media.html', search_results=search_results, pagination=pagination, search_query=search_query, table_type=table_type)

#PAGE de preview avant ajout média
#Le post ici sert à si on add un média depuis une base interne ou externe
@add_media_bp.route('/preview', methods=['GET', 'POST'])
def add_media_preview():
    current_user = get_current_user()
    if not current_user:
        return redirect('/login')

    data = {}
    
    # Récupére les données   
    try:
        response = api_get(f'/users/{current_user["id"]}/libraries')
        if response.status_code == 200:
            libraries = response.json()
        else:
            libraries = []
    except Exception:
        libraries = []

    genres, franchises, persons = get_data_for_media()

    #SI on veux la preview d'un média externe ou interne
    if request.method == 'POST':
        base = request.form.get('base') or None
        media_id = get_int_or_default(request.form.get('media_id'))

        if base == 'externe_film':
            response = api_tmdb_get_film(media_id)
            if response:
                data = response
        elif base == 'externe_series':
            response = api_tmdb_get_series(media_id)
            if response:
                data = response
        elif base == 'interne':
            response = api_get(f'/media/{media_id}')
            if response.status_code == 200:
                data = response.json()
                try:
                    data['genres'] = [int(g['id']) for g in data['genres']]
                except:
                    data['genres'] = []
                
    
    return render_template('add-media/add-media-preview.html', libraries=libraries, data=data, genres=genres, franchises=franchises, persons=persons)

#AJOUT d'un MEDIA
@add_media_bp.route('/preview/add', methods=['POST'])
def add_media_preview_add():
    current_user = get_current_user()
    if not current_user:
        return redirect('/login')
    
    # Récupérer les données nécessaires
    try:
        response = api_get(f'/users/{current_user["id"]}/libraries')
        if response.status_code == 200:
            libraries = response.json() or []
        else:
            libraries = []
    except Exception:
        libraries = []

    genres, franchises, persons = get_data_for_media()


    title = request.form.get('title') or None
    media_type = request.form.get('type') or None
    library_id = get_int_or_default(request.form.get('library'))
    visibility = request.form.get('visibility') or None
    release_year = get_int_or_default(request.form.get('year'))
    synopsis = request.form.get('synopsis') or None
    trailer_url = request.form.get('trailer_url') or None
    franchise_id = get_int_or_default(request.form.get('franchise'))
    franchise_order = get_int_or_default(request.form.get('franchise_order'))
    genres_selected = request.form.getlist('genres') or []
    duration = get_int_or_default(request.form.get('duration'))

    #Champ obligatoires
    if not title or not media_type or not library_id or not visibility:
        return render_template('add-media/add-media-preview.html', libraries=libraries, genres=genres, franchises=franchises, persons=persons, messages=['danger', 'Tous les champs obligatoires doivent être remplis'])
    
    # Validation de l'URL YouTube
    if trailer_url:
        trailer_url = get_url_embed_youtube(trailer_url)
        if not trailer_url:
            return render_template('add-media/add-media-preview.html', libraries=libraries, genres=genres, franchises=franchises, persons=persons, messages=['danger', 'L\'URL de la bande-annonce doit être un lien YouTube valide (https://youtube.com/ ou https://www.youtube.com/)'])

    file = request.files.get('cover_image') or None
    current_cover_url = request.form.get('current_cover_url') or None
    cover_image_url = None

    #Traitement de l'image
    if current_cover_url:
        if current_cover_url.startswith('https://image.tmdb.org/t/p/original/'):
            cover_image_url = upload_cover_image(current_cover_url, True)
        else:
            cover_image_url = current_cover_url
    elif file and file.filename:
        cover_image_url = upload_cover_image(file)
        if not cover_image_url:
            return render_template('add-media/add-media-preview.html', libraries=libraries, genres=genres, franchises=franchises, persons=persons, messages=['danger', 'Type de fichier non autorisé ou erreur lors de l\'upload de l\'image'])
    
    try:
        # Convertir les genres en liste d'entiers
        try:
            genre_ids = [int(g) for g in genres_selected if g]
        except:
            genre_ids = []
        
        #TRAITEMENT DES PERSONNES (acteur, ou autre rôle)
        persons_list = get_persons_post_data(request.form)
        
        data = {
            'title': title,
            'type': media_type,
            'library_id': library_id,
            'visibility': visibility,
            'release_year': release_year,
            'duration': duration,
            'synopsis': synopsis,
            'cover_image_url': cover_image_url,
            'trailer_url': trailer_url,
            'franchise_id': franchise_id,
            'franchise_order': franchise_order,
            'genres': genre_ids,
            'persons': persons_list
        }
        response = api_post('/media', data=data)
        
        if response.status_code == 201:
            return redirect(f'/library/{library_id}')
        else:
            return render_template('add-media/add-media-preview.html', libraries=libraries, genres=genres, franchises=franchises, persons=persons, messages=['danger', 'Erreur lors de l\'ajout'])
    except Exception as e:
        return render_template('add-media/add-media-preview.html', libraries=libraries, genres=genres, franchises=franchises, persons=persons, messages=['danger', f'Erreur lors de l\'ajout: {str(e)}'])