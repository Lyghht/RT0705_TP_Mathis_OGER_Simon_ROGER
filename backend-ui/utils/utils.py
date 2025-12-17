import requests
from flask import session
import os
import uuid
import re
from utils.utils_api import api_search

API_BASE_URL = 'http://nginx/api'

def get_current_user():
    if 'auth_token' not in session:
        return None
    try:
        headers = {'Authorization': f"Bearer {session['auth_token']}"}
        response = requests.get(f'{API_BASE_URL}/me', headers=headers)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def is_admin():
    user = get_current_user()
    if not user:
        return False
    return user.get('role') in ['admin', 'trusted']

def is_real_admin():
    """Vérifie si l'utilisateur est vraiment admin (pas trusted)"""
    user = get_current_user()
    if not user:
        return False
    return user.get('role') == 'admin'

#Gestion generique des requêtes simple
def get_generic_view(request, base, per_page):
    search_query = request.args.get('q', '')
    try:
        page = int(request.args.get('page', 1))
    except:
        page = 1
    
    items = []
    pagination = {}
    messages = None
    
    items, pagination = api_search(base, search_query, page, per_page)
    if not items and not pagination:
        messages = ['danger', 'Erreur lors du chargement.']
    
    return items, pagination, search_query, page, messages

def upload_cover_image(file, url=False):
    """Upload une image de couverture et retourne l'URL ou None en cas d'erreur."""
    try:

        if url:
            response = requests.get(file)
            if response.status_code == 200:
                ext = os.path.splitext(file)[-1].lower()
                unique_name = f"{uuid.uuid4()}{ext}"

                with open(f"./static/images/{unique_name}", 'wb') as f:
                    f.write(response.content)
                return f'/static/images/{unique_name}'
            else:
                return None
        else:
            if not file or not file.filename:
                return None
            ext = os.path.splitext(file.filename)[-1].lower()
            if ext not in ['.png', '.jpg', '.jpeg', '.webp']:
                return None
            
            unique_name = f"{uuid.uuid4()}.{ext}"
            file_path = os.path.join('./static/images/', unique_name)
            file.save(file_path)
            return f'/static/images/{unique_name}'
    except:
        return None

def get_persons_post_data(request_form):
    persons_list = []

    for key in request_form.keys():
        if key.startswith("person_") and key.count("_") == 1:
            try:
                person_num = key.split("_")[1]

                person_id = request_form.get(f"person_{person_num}")
                person_role = request_form.get(f"person_{person_num}_role")
                person_character = request_form.get(f"person_{person_num}_character")

                # On vérifie qu'on a au moins un ID et un rôle ou un personnage
                if person_id and (person_role or person_character):
                    persons_list.append({
                        "person_id": int(person_id),
                        "role": person_role or None,
                        "character_name": person_character or None
                    })
            except:
                continue 
    return persons_list


def get_url_embed_youtube(url):
    youtube_pattern = re.compile(r'^https://(www\.)?youtube\.com/.*', re.IGNORECASE)
    if not youtube_pattern.match(url):
        return None
    else:
        try:
            if "v=" in url:
                url = url.split("v=")[1].split("&")[0]
            elif "youtu.be/" in url:
                url = url.split("youtu.be/")[1].split("?")[0]
            elif "/embed/" in url:
                url = url.split("/embed/")[1].split("?")[0]
            else:
                return None
                
            return f"https://www.youtube.com/embed/{url}"
        except:
            return None

#récupére les donnée pour chargé un média
def get_data_for_media():
    genres, _ = api_search('genres', '', 1, 100)
    franchises, _ = api_search('franchises', '', 1, 100)
    persons, _ = api_search('persons', '', 1, 100)

    if not genres:
        genres = []
    if not franchises:
        franchises = []
    if not persons:
        persons = []

    return genres, franchises, persons