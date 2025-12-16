from flask import Blueprint, render_template, redirect, request, session
from utils.utils import get_current_user
from utils.utils_api import api_get, api_post, api_delete, api_patch

profile_bp = Blueprint('profile', __name__)

#PAGE PROFIL de l'utilisateur connecté ou d'un utilisateur spécifique
@profile_bp.route('/', methods=['GET', 'POST'])
@profile_bp.route('/<int:user_id>', methods=['GET', 'POST'])
def profile(user_id=None):
    current_user = get_current_user()
    
    if user_id or current_user:
        requested_user_id = user_id if user_id else current_user['id']
    else:
        return redirect('/login')
    is_own_profile = current_user['id'] == requested_user_id if current_user else False
    
    profile_user = None
    libraries = []
    pagination = {}
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1

    messages = session.pop('messages', None)

    if request.method == 'POST':
        if is_own_profile:
            # Modification du profil utilisateur
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password') or None
            bio = request.form.get('bio') or None
            
            if username and email:
                data = {}
                data['username'] = username
                data['email'] = email
                if password:
                    data['password'] = password
                data['bio'] = bio
                
                try:
                    response = api_patch(f'/users/{current_user['id']}', data=data)
                    if response.status_code == 200:
                        messages = ['success', 'Profil modifié avec succès']
                    else:
                        messages = ['danger', 'Erreur lors de la modification']
                except Exception as e:
                    messages = ['danger', f'Erreur lors de la modification: {str(e)}']
            else:
                messages = ['danger', 'Il manque un username et/ou un email']
        
    try:
        response = api_get(f'/users/{requested_user_id}')
        if response.status_code == 200:
            profile_user = response.json()
        
        response = api_get(f'/search/libraries?q=&owner_id={requested_user_id}&page={page}&per_page=10')
        if response.status_code == 200:
            data = response.json()
            libraries = data.get('data', [])
            pagination = data.get('pagination', {})
            
            # récupérer l'username du propriétaire
            for library in libraries:
                try:
                    response = api_get(f'/users/{library['owner_id']}')
                    if response.status_code == 200:
                        data_response = response.json()
                        library['owner'] = data_response.get('username', '-')
                except:
                    pass
    except:
        pass
    
    return render_template('profile.html', profile_user=profile_user, libraries=libraries, pagination=pagination, current_page=page, is_own_profile=is_own_profile, messages=messages)


#GESTION DES VIDÉOTHÈQUES
@profile_bp.route('/libraries', methods=['POST'])
def profile_libraries():
    current_user = get_current_user()
    if not current_user:
        return redirect('/login')
    
    try:
        library_id = int(request.form.get('library_id'))
    except:
        library_id = None

    name = request.form.get('name', '')
    description = request.form.get('description', '')
    visibility = request.form.get('visibility', '')
    action = request.form.get('action', '')
    
    if action not in ['delete', 'update', 'add']:
        session['messages'] = ['danger', 'Action non valide']
        return redirect('/profile')
    
    #SUPPRESSION d'une VIDÉOTHÈQUE
    if action == 'delete':
        if library_id:
            try:
                response = api_delete(f'/libraries/{library_id}')
                if response.status_code == 200:
                    session['messages'] = ['success', 'Bibliothèque supprimée avec succès'] 
                else:
                    session['messages'] = ['danger', 'Erreur lors de la suppression de la bibliothèque']
            except:
                session['messages'] = ['danger', 'Erreur lors de la suppression de la bibliothèque']
        else:
            session['messages'] = ['danger', 'La bibliothèque n\'a pas été trouvée']

    #Ajout ou mise à jour
    else:

        try:
            data = {'name': name, 'description': description, 'visibility': visibility}
            #Mise à jours
            if action == 'update' and library_id:
                response = api_patch(f'/libraries/{library_id}', data=data)
            #Ajout
            elif action == 'add' and name and visibility:
                response = api_post('/libraries', data=data)
            
            if response and response.status_code in [200, 201]:
                session['messages'] = ['success', 'Bibliothèque modifiée avec succès'] 
            else:
                session['messages'] = ['danger', 'Erreur lors de la modification / ajout de la bibliothèque']
        except:
            session['messages'] = ['danger', 'Erreur lors de la modification / ajout de la bibliothèque']
        
    return redirect('/profile')