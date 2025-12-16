from flask import Blueprint, render_template, redirect, request, session
from utils.utils import get_current_user
from utils.utils_api import api_post

auth_bp = Blueprint('auth', __name__)


#Page de connexion
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    #Si l'utilisateur est connecté on le met à l'accueil
    current_user = get_current_user()
    if current_user:
        return redirect('/')
    
    messages=None
    
    #Connexion de l'utilisateur
    if request.method == 'POST':
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            messages = ['danger', 'Email et mot de passe requis']
        else:
            try:
                response = api_post('/login',data={'email': email, 'password': password})
                if response.status_code == 200:
                    session['auth_token'] = response.json().get('token')
                    #L'utilisateur est connecté on le met à l'accueil
                    return redirect('/')
                else:
                    messages = ['danger', 'Email ou mot de passe invalide']
            except:
                messages = ['danger', 'Erreur lors de la connexion.']
    
    #Affichage de la page de connexion
    return render_template('login.html', messages=messages)


#Page d'inscription
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    #Si l'utilisateur est connecté on le met à l'accueil
    current_user = get_current_user()
    if current_user:
        return redirect('/')
    
    messages=None
    
    #Inscription de l'utilisateur
    if request.method == 'POST':
        username = request.form.get('username', '')
        email = request.form.get('email', '').lower()
        password = request.form.get('password', '')
        
        if not email or not password or not username:
            messages = ['danger', 'Username, Mail et mot de passe requis']
        else:
            try:
                response = api_post('/register', data={'username': username, 'email': email, 'password': password})
                if response.status_code == 201:
                    session['auth_token'] = response.json().get('token')
                    #L'utilisateur est inscrit on le met à l'accueil
                    return redirect('/')
                else:
                    messages = ['danger', 'Erreur lors de l\'inscription']
            except:
                messages = ['danger', 'Erreur lors de l\'inscription']
    
    #Affichage de la page d'inscription
    return render_template('register.html', messages=messages)


#Page de déconnexion
@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')

