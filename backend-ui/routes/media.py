from flask import Blueprint, render_template, request, redirect
from utils.utils import api_get, get_current_user, api_patch, get_url_embed_youtube, upload_cover_image, get_persons_post_data

media_bp = Blueprint('media', __name__)

@media_bp.route('/', methods=['GET'])
def media():
    search_query = request.args.get('q', '')

    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1

    try:
        franchise_id = int(request.args.get('franchise_id'))
    except:
        franchise_id = None

    try:
        genre_id = int(request.args.get('genre_id'))
    except:
        genre_id = None


    media_items = []
    pagination = {}
    
    try:
        response = api_get(f'/search/media?q={search_query}&page={page}&per_page=24&franchise_id={franchise_id}&genre_id={genre_id}')
        if response.status_code == 200:
            data = response.json()
            media_items = data.get('data', [])
            pagination = data.get('pagination', {})
    except:
        pass
    
    return render_template('media.html', media_items=media_items, pagination=pagination, search_query=search_query, current_page=page, franchise_id=franchise_id, genre_id=genre_id)

@media_bp.route('/<int:media_id>', methods=['GET'])
def media_details(media_id):
    current_user = get_current_user()
    media_data = None
    persons = []
    library_data = None
    franchise_data = None

    try:
        response = api_get(f'/media/{media_id}')
        if response.status_code == 200:
            media_data = response.json()
            
            # Récupérer les informations de la vidéothèque
            if media_data and media_data.get('library_id'):
                lib_id = media_data.get('library_id')
                response = api_get(f'/libraries/{lib_id}')
                if response.status_code == 200:
                    library_data = response.json()
            
            # Récupérer les informations de la franchise si elle existe
            if media_data and media_data.get('franchise_id'):
                franchise_id = media_data.get('franchise_id')
                response = api_get(f'/franchises/{franchise_id}')
                if response.status_code == 200:
                    franchise_data = response.json()
            
            # Récupérer les personnes associées
            response = api_get(f'/media/{media_id}/persons')
            if response.status_code == 200:
                persons = response.json()

    except Exception as e:
        # En cas d'erreur, rediriger vers la page d'erreur ou la liste des médias
        pass

    # Vérifier si l'utilisateur est propriétaire ou admin
    is_owner = False
    if current_user and library_data:
        is_owner = current_user.get("id") == library_data.get("owner_id") or current_user.get("role") == "admin"

    if not media_data:
        # Si le média n'existe pas ou n'est pas accessible, rediriger
        return redirect('/media')

    return render_template('display-media.html', media=media_data, persons=persons, library=library_data, franchise=franchise_data,is_owner=is_owner)

@media_bp.route('/<int:media_id>/edit', methods=['GET'])
def edit_media(media_id):
    current_user = get_current_user()
    if not current_user:
        return redirect('/login')
        
    media = None
    library = None
    genres = []
    franchises = []
    all_persons = []
    current_persons = []
    current_genre_ids = []
    
    try:
        response = api_get(f'/media/{media_id}')
        if response.status_code == 200:
            media = response.json()
        else:
            return redirect(f'/media/{media_id}')
            
        lib_id = media.get('library_id')
        response = api_get(f'/libraries/{lib_id}')
        if response.status_code == 200:
            library = response.json()
            
        is_owner = current_user['id'] == library['owner_id'] or current_user['role'] == 'admin'
        if not is_owner:
            return redirect(f'/media/{media_id}')


        response = api_get('/search/genres?q=&page=1&per_page=100')
        if response.status_code == 200:
            genres_data = response.json()
            genres = genres_data.get('data', [])
            
        response = api_get('/search/franchises?q=&page=1&per_page=100')
        if response.status_code == 200:
            franchises_data = response.json()
            franchises = franchises_data.get('data', [])
            
        response = api_get('/search/persons?q=&page=1&per_page=100')
        if response.status_code == 200:
            persons_data = response.json()
            all_persons = persons_data.get('data', [])
            
        response = api_get(f'/media/{media_id}/persons')
        if response.status_code == 200:
            current_persons = response.json()
            
        try:
            if media.get('genres'):
                current_genre_ids = [int(g['id']) for g in media['genres']]
        except:
            current_genre_ids = []
            
    except Exception as e:
        return redirect(f'/media/{media_id}')
        
    return render_template('edit-media.html', media=media, genres=genres, franchises=franchises, all_persons=all_persons,current_persons=current_persons,current_genre_ids=current_genre_ids)

@media_bp.route('/<int:media_id>/edit', methods=['POST'])
def edit_media_post(media_id):
    current_user = get_current_user()
    if not current_user:
        return redirect('/login')
    
    # Récupérer les genres, franchises et personnes pour le template en cas d'erreur
    genres = []
    franchises = []
    all_persons = []
    current_persons = []
    
    try:
        response = api_get('/search/genres?q=&page=1&per_page=100')
        if response.status_code == 200:
            genres_data = response.json()
            genres = genres_data.get('data', [])
    
        response = api_get('/search/franchises?q=&page=1&per_page=100')
        if response.status_code == 200:
            franchises_data = response.json()
            franchises = franchises_data.get('data', [])

        response = api_get('/search/persons?q=&page=1&per_page=100')
        if response.status_code == 200:
            persons_data = response.json()
            all_persons = persons_data.get('data', [])
            
        response = api_get(f'/media/{media_id}/persons')
        if response.status_code == 200:
            current_persons = response.json()
    except:
        pass
    
    title = request.form.get('title') or None
    media_type = request.form.get('type') or None
    visibility = request.form.get('visibility') or None
    try:
        release_year = int(request.form.get('year')) or None
    except:
        release_year = None
    synopsis = request.form.get('synopsis') or None
    trailer_url = request.form.get('trailer_url') or None
    try:
        franchise_id = int(request.form.get('franchise')) or None
    except:
        franchise_id = None

    try:
        franchise_order = int(request.form.get('franchise_order')) or None
    except:
        franchise_order = None
    genres_selected = request.form.getlist('genres') or []
    try:
        duration = int(request.form.get('duration')) or None
    except:
        duration = None

    # fonction pour construire l'objet si erreur
    def build_media_if_error(cover_img_url=None, genre_ids_list=None):
        if cover_img_url is None:
            cover_img_url = request.form.get('current_cover_url', None)
        if genre_ids_list is None:
            try:
                genre_ids_list = [int(g) for g in genres_selected if g]
            except:
                genre_ids_list = []
        return {
            'id': media_id,
            'title': title,
            'type': media_type,
            'visibility': visibility,
            'release_year': release_year,
            'duration': duration,
            'synopsis': synopsis,
            'cover_image_url': cover_img_url,
            'trailer_url': trailer_url,
            'franchise_id': int(franchise_id) if franchise_id else None,
            'franchise_order': franchise_order,
        }, genre_ids_list

    if not title or not media_type or not visibility:
        media_obj, current_genre_ids = build_media_if_error()
        return render_template('edit-media.html', media=media_obj, genres=genres, franchises=franchises, all_persons=all_persons, current_persons=current_persons, current_genre_ids=current_genre_ids, messages=['danger', 'Tous les champs obligatoires doivent être remplis'])
    
    # Validation de l'URL YouTube
    if trailer_url:
        trailer_url = get_url_embed_youtube(trailer_url)
        if not trailer_url:
            media_obj, current_genre_ids = build_media_if_error()
            return render_template('edit-media.html', media=media_obj, genres=genres, franchises=franchises, all_persons=all_persons, current_persons=current_persons, current_genre_ids=current_genre_ids, messages=['danger', 'L\'URL de la bande-annonce doit être un lien YouTube valide (https://youtube.com/ ou https://www.youtube.com/)'])
    
    file = request.files.get('cover_image') or None
    current_cover_url = request.form.get('current_cover_url') or None
    cover_image_url = None

    #Traitement de l'image
    if file and file.filename:
        cover_image_url = upload_cover_image(file)
        if not cover_image_url:
            media_obj, current_genre_ids = build_media_if_error(cover_img_url=current_cover_url)
            return render_template('edit-media.html', media=media_obj, genres=genres, franchises=franchises, all_persons=all_persons, current_persons=current_persons, current_genre_ids=current_genre_ids, messages=['danger', 'Type de fichier non autorisé ou erreur lors de l\'upload de l\'image'])
    elif current_cover_url:
        cover_image_url = current_cover_url
    
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
            'visibility': visibility,
            'release_year': int(release_year) if release_year else None,
            'duration': int(duration) if duration else None,
            'synopsis': synopsis,
            'cover_image_url': cover_image_url,
            'trailer_url': trailer_url,
            'franchise_id': int(franchise_id) if franchise_id else None,
            'franchise_order': int(franchise_order) if franchise_order else None,
            'genres': genre_ids,
            'persons': persons_list
        }
        response = api_patch(f'/media/{media_id}', data=data)
        
        if response.status_code == 200:
            return redirect(f'/media/{media_id}')
        else:
            media_obj, current_genre_ids = build_media_if_error(cover_img_url=cover_image_url, genre_ids_list=genre_ids)
            return render_template('edit-media.html', media=media_obj, genres=genres, franchises=franchises, all_persons=all_persons, current_persons=current_persons, current_genre_ids=current_genre_ids, messages=['danger', 'Erreur lors de la modification'])
    except Exception as e:
        media_obj, current_genre_ids = build_media_if_error(cover_img_url=cover_image_url)
        return render_template('edit-media.html', media=media_obj, genres=genres, franchises=franchises, all_persons=all_persons, current_persons=current_persons, current_genre_ids=current_genre_ids, messages=['danger', f'Erreur lors de la modification: {str(e)}'])
