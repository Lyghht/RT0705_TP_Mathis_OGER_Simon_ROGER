from flask import Blueprint, render_template, request, redirect
from utils.utils import get_current_user
from utils.utils_api import api_get, api_post, api_patch, api_delete, api_search

libraries_bp = Blueprint('libraries', __name__)

#Vue des vidéothèques
@libraries_bp.route('/libraries', methods=['GET', 'POST'])
def libraries():
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1

    try:
        library_items, pagination = api_search('libraries', '', page, 18)
        if library_items and pagination:
            # récupérer l'username du propriétaire
            for library in library_items:
                try:
                    response = api_get(f'/users/{library['owner_id']}')
                    if response.status_code == 200:
                        data_response = response.json()
                        library['owner'] = data_response.get('username', '-')
                except:
                    pass
        else:
            library_items = []
            pagination = {}
    except:
        return render_template('libraries.html', library_items=library_items, pagination=pagination, current_page=page, messages=['danger', 'Erreur avec le serveur'])
    
    if request.method == 'POST':
        current_user = get_current_user()
        if not current_user:
            return redirect('/login')
        
        name = request.form.get('name', '')
        description = request.form.get('description', '')
        visibility = request.form.get('visibility')
        
        if not name or not visibility:
            return render_template('libraries.html', library_items=library_items, pagination=pagination,current_page=page, messages=['danger', 'Le nom et la visibilité sont requis'])
        else:
            try:
                data = {'name': name, 'description': description, 'visibility': visibility}
                response = api_post('/libraries', data=data)
                if response.status_code == 201:
                    return redirect('/libraries')
                else:
                    return render_template('libraries.html', library_items=library_items, pagination=pagination,current_page=page, messages=['danger', 'Erreur lors de la création'])
            except:
                return render_template('libraries.html', library_items=library_items, pagination=pagination,current_page=page, messages=['danger', 'Erreur lors de la création'])

    return render_template('libraries.html', library_items=library_items, pagination=pagination, current_page=page)



#Vue d'une vidéothèque
@libraries_bp.route('/library/<int:library_id>', methods=['GET', 'POST'])
def library(library_id):
    current_user = get_current_user()
    library_data = None
    media_items = []
    pagination = {}
    is_owner = False
    is_admin = current_user and current_user.get('role') == 'admin'
    messages = None
    
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    
    # gestion de la delete d'un média
    if request.method == 'POST' and request.form.get('action') == 'delete_media':
        if not current_user:
            return redirect('/login')
        
        try:
            media_id = int(request.form.get('media_id'))
        except:
            media_id = None
        if media_id:
            try:
                response = api_get(f'/libraries/{library_id}')
                if response.status_code == 200:
                    library_data = response.json()
                    is_owner = current_user.get('id') == library_data.get('owner_id') or is_admin
                    
                    if is_owner:
                        response = api_delete(f'/media/{media_id}')
                        if response.status_code == 200:
                            messages = ['success', 'Média supprimé avec succès']
                        else:
                            messages = ['danger', 'Erreur lors de la suppression du média, le média n\'a pas été trouvé']

                    else:
                        messages = ['danger', 'Vous n\'avez pas les droits pour supprimer ce média']
            except Exception as e:
                messages = ['danger', 'Erreur lors de la suppression du média']
    
    # Gestion de la modification de la vidéothèque
    if request.method == 'POST' and request.form.get('action') == 'update_library':
        if not current_user:
            return redirect('/login')
        
        try:
            response = api_get(f'/libraries/{library_id}')
            if response.status_code == 200:
                library_data = response.json()
                is_owner = current_user.get('id') == library_data.get('owner_id') or is_admin
                
                if is_owner:
                    data = {}
                    if request.form.get('name'):
                        data['name'] = request.form.get('name')
                    if 'description' in request.form:
                        data['description'] = request.form.get('description') or None
                    if request.form.get('visibility'):
                        data['visibility'] = request.form.get('visibility')
                    
                    response = api_patch(f'/libraries/{library_id}', data=data)
                    if response.status_code == 200:
                        messages = ['success', 'Vidéothèque modifiée avec succès']
                    else:
                        messages = ['danger', 'Erreur lors de la modification de la vidéothèque']
                else:
                    messages = ['danger', 'Vous n\'avez pas les droits pour modifier cette vidéothèque']
        except Exception as e:
            messages = ['danger', 'Erreur lors de la modification']
    
    # Gestion de la suppression de la vidéothèque
    if request.method == 'POST' and request.form.get('action') == 'delete_library':
        if not current_user:
            return redirect('/login')
        
        try:
            response = api_get(f'/libraries/{library_id}')
            if response.status_code == 200:
                library_data = response.json()
                is_owner = current_user.get('id') == library_data.get('owner_id') or is_admin
                
                if is_owner:
                    response = api_delete(f'/libraries/{library_id}')
                    if response.status_code == 200:
                        return redirect('/libraries')
                    else:
                        messages = ['danger', 'Erreur lors de la suppression de la vidéothèque']
                else:
                    messages = ['danger', 'Vous n\'avez pas les droits pour supprimer cette vidéothèque']
        except Exception as e:
            messages = ['danger', 'Erreur lors de la suppression']
    
    # Affichage normal (GET)
    try:
        response = api_get(f'/libraries/{library_id}')
        if response.status_code == 200:
            library_data = response.json()
            is_owner = current_user and (current_user.get('id') == library_data.get('owner_id') or is_admin)
            
            # récupération proprio
            if library_data and library_data.get('owner_id'):
                owner_id = library_data.get('owner_id')
                response = api_get(f'/users/{owner_id}')
                if response.status_code == 200:
                    library_data['owner'] = response.json().get('username', '-')
            
            #récupération média
            response = api_get(f'/search/media?q=&library_id={library_id}&page={page}&per_page=10')
            if response.status_code == 200:
                data = response.json()
                media_items = data.get('data', [])
                pagination = data.get('pagination', {})
        elif response.status_code == 403:
            # Accès refusé car la vidéoothèque privée ou utilisateur n'a pas les droits
            return render_template('error.html', error_code=403, error_message="Accès refusé à cette vidéothèque"), 403
        elif response.status_code == 404:
            # Bibliothèque non trouvée
            return render_template('error.html', error_code=404, error_message="Vidéothèque non trouvée"), 404
    except:
        pass
    
    # Si library_data est None c'est quelle existe pas
    if not library_data:
        return render_template('error.html', error_code=404, error_message="Vidéothèque non trouvée"), 404
    
    return render_template('library.html', library_data=library_data, media_items=media_items, pagination=pagination, current_page=page, is_owner=is_owner, is_admin=is_admin, messages=messages)