from flask import Blueprint, render_template, redirect, request
from utils.utils import is_admin, is_real_admin, get_current_user
from utils.utils_api import api_get, api_post, api_patch, api_delete, api_search

admin_bp = Blueprint('admin', __name__)


#PAGE ADMIN

@admin_bp.route('/')
def admin():
    if not is_admin():
        return redirect('/')
    current_user = get_current_user()
    return render_template('admin.html', current_user=current_user)




#PAGE ADMIN PERSONS
@admin_bp.route('/persons', methods=['GET', 'POST'])
def admin_persons():
    if not is_admin():
        return redirect('/')
    
    messages = None
    
    try:
        delete_id = int(request.form.get('delete'))
    except:
        delete_id = None

    #Suppression d'une personne
    if request.method == 'POST' and delete_id:
        try:
            response = api_delete(f'/persons/{delete_id}')
            if response.status_code == 200:
                messages = ['success', 'Personne supprimée avec succès']
            else:
                messages = ['danger', 'Erreur lors de la suppression']
        except:
            messages = ['danger', 'Erreur lors de la suppression']
    #Ajout / modification d'une personne
    elif request.method == 'POST' and not delete_id:
        try:
            person_id = int(request.form.get('id'))
        except:
            person_id = None

        name = request.form.get('name', '')
        birthdate = request.form.get('birthdate', '') or None
        
        if not name:
            messages = ['danger', 'Le nom est requis']
        else:
            try:
                data = {'name': name, 'birthdate': birthdate}
                #Modification
                if person_id:
                    response = api_patch(f'/persons/{person_id}', data=data)
                #Ajout
                else:
                    response = api_post('/persons', data=data)
                
                if response.status_code in [200, 201]:
                    messages = ['success', 'Personne enregistrée avec succès']
                else:
                    messages = ['danger', 'Erreur lors de l\'enregistrement ou de la modification']
            except:
                messages = ['danger', 'Erreur lors de l\'enregistrement ou de la modification']
    
    #Requête normal GET
    search_query = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    person_items = []
    pagination = {}
    
    person_item, pagination = api_search('persons', search_query, page, 10)
    if not person_item or not pagination:
        messages = ['danger', 'Erreur lors du chargement des personnes']
    
    return render_template('admin-persons.html', person_items=person_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)


#PAGE ADMIN GENRES

@admin_bp.route('/genres', methods=['GET', 'POST'])
def admin_genres():
    if not is_admin():
        return redirect('/')
    
    try:
        delete_id = int(request.form.get('delete'))
    except:
        delete_id = None

    messages = None

    #Suppression d'un genre
    if request.method == 'POST' and delete_id:
        try:
            response = api_delete(f'/genres/{delete_id}')
            if response.status_code == 200:
                messages = ['success', 'Genre supprimé avec succès']
            else:
                messages = ['danger', 'Erreur lors de la suppression']
        except:
            messages = ['danger', 'Erreur lors de la suppression']
    #Ajout / modification d'un genre
    elif request.method == 'POST' and not delete_id:
        try:
            genre_id = int(request.form.get('id'))
        except:
            genre_id = None
        name = request.form.get('name', '')
        
        if not name:
            messages = ['danger', 'Le nom est requis']
        else:
            try:
                data = {'name': name}
                #Modification
                if genre_id:
                    response = api_patch(f'/genres/{genre_id}', data=data)
                #Ajout
                else:
                    response = api_post('/genres', data=data)
                
                if response.status_code in [200, 201]:
                    messages = ['success', 'Genre enregistré avec succès']
                else:
                    messages = ['danger', 'Erreur lors de l\'enregistrement ou de la modification']
            except:
                messages = ['danger', 'Erreur lors de l\'enregistrement ou de la modification']
    
    #Requête normal GET
    search_query = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    genre_items = []
    pagination = {}
    
    genre_items, pagination = api_search('genres', search_query, page, 10)
    if not genre_items or not pagination:
        messages = ['danger', 'Erreur lors du chargement des genres']
    
    return render_template('admin-genres.html', genre_items=genre_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)


#PAGE ADMIN FRANCHISES

@admin_bp.route('/franchises', methods=['GET', 'POST'])
def admin_franchises():
    if not is_admin():
        return redirect('/')
    
    try:
        delete_id = int(request.form.get('delete'))
    except:
        delete_id = None

    messages = None

    #Suppression d'une franchise
    if request.method == 'POST' and delete_id:
        try:
            response = api_delete(f'/franchises/{delete_id}')
            if response.status_code == 200:
                messages = ['success', 'Franchise supprimée avec succès']
            else:
                messages = ['danger', 'Erreur lors de la suppression']
        except:
            messages = ['danger', 'Erreur lors de la suppression'] 
    #Ajout / modification d'une franchise
    elif request.method == 'POST' and not delete_id:
        try:
            franchise_id = int(request.form.get('id'))
        except:
            franchise_id = None
        name = request.form.get('name', '')
        description = request.form.get('description', '') or None
        
        if not name:
            messages = ['danger', 'Le nom est requis']
        else:
            try:
                data = {'name': name, 'description': description}
                #Modification
                if franchise_id:
                    response = api_patch(f'/franchises/{franchise_id}', data=data)
                #Ajout
                else:
                    response = api_post('/franchises', data=data)
                
                if response.status_code in [200, 201]:
                    messages = ['success', 'Franchise enregistrée avec succès']
                else:
                    messages = ['danger', 'Erreur lors de l\'enregistrement ou de la modification']
            except:
                messages = ['danger', 'Erreur lors de l\'enregistrement ou de la modification']
    
    #Requête normal GET
    search_query = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    franchise_items = []
    pagination = {}
    
    franchise_items, pagination = api_search('franchises', search_query, page, 10)
    if not franchise_items or not pagination:
        messages = ['danger', 'Erreur lors du chargement des franchises']
    
    return render_template('admin-franchises.html', franchise_items=franchise_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)


#PAGE ADMIN USERS

@admin_bp.route('/users', methods=['GET', 'POST'])
def admin_users():
    if not is_real_admin():
        return redirect('/')
    
    messages = None

    try:
        delete_id = int(request.form.get('delete'))
    except:
        delete_id = None

    #Suppression d'un utilisateur
    if request.method == 'POST' and delete_id:
        try:
            response = api_delete(f'/users/{delete_id}')
            if response.status_code == 200:
                messages = ['success', 'Utilisateur supprimé avec succès']
            else:
                messages = ['danger', 'Erreur lors de la suppression']
        except Exception as e:
            messages = ['danger', 'Erreur lors de la suppression']
    elif request.method == 'POST' and not delete_id:
        try:
            user_id = int(request.form.get('id'))
        except:
            user_id = None

        username = request.form.get('username', '')
        email = request.form.get('email', '')
        bio = request.form.get('bio', '')
        role = request.form.get('role', '')
        
        if not user_id or not role or not username or not email:
            messages = ['danger', 'ID utilisateur, rôle, username et email requis']
        else:
            try:
                data = {'role': role, 'username': username, 'email': email, 'bio': bio}
                response = api_patch(f'/users/{user_id}', data=data)
                
                if response.status_code == 200:
                    messages = ['success', 'Utilisateur modifié avec succès']
                else:
                    messages = ['danger', 'Erreur lors de la modification']
            except:
                messages = ['danger', 'Erreur lors de la modification']
    

    #Requête normal GET
    search_query = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    user_items = []
    pagination = {}
    
    user_items, pagination = api_search('users', search_query, page, 10)
    if not user_items or not pagination:
        messages = ['danger', 'Erreur lors du chargement des utilisateurs']
    
    return render_template('admin-users.html', user_items=user_items, pagination=pagination, search_query=search_query, current_page=page, messages=messages)

