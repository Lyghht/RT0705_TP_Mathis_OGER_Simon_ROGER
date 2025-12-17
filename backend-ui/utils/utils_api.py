import requests
from flask import session
import os

API_BASE_URL = f'http://backend-api:{os.getenv('PORT_API')}/api'
#Si on veux contacter l'api par l'extérieur il faut faire http://nginx/api

#GET sur l'api
def api_get(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    if 'auth_token' in session:
        headers['Authorization'] = f"Bearer {session['auth_token']}"
    return requests.get(url, headers=headers)

#GET sur l'api TMDB
def api_get_tmdb(endpoint):
    url = f"https://api.themoviedb.org/3{endpoint}"
    headers = {'Authorization': f"Bearer {os.getenv('TOKEN_API_TMDB')}"}
    return requests.get(url, headers=headers)

#POST sur l'api
def api_post(endpoint, data=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    if 'auth_token' in session:
        headers['Authorization'] = f"Bearer {session['auth_token']}"
    return requests.post(url, json=data, headers=headers)

#PATCH sur l'api
def api_patch(endpoint, data=None):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    if 'auth_token' in session:
        headers['Authorization'] = f"Bearer {session['auth_token']}"
    return requests.patch(url, json=data, headers=headers)

#API DELETE
def api_delete(endpoint):
    url = f"{API_BASE_URL}{endpoint}"
    headers = {}
    if 'auth_token' in session:
        headers['Authorization'] = f"Bearer {session['auth_token']}"
    return requests.delete(url, headers=headers)

#API Recherche simple
def api_search(base, query=None, page=1, per_page=10):
    try:
        response = api_get(f'/search/{base}?q={query}&page={page}&per_page={per_page}')
        if response.status_code == 200:
            data = response.json()
            content = data.get('data', [])
            pagination = data.get('pagination', {})
            return content, pagination
        else:
            return None, None
    except:
        return None, None