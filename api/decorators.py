from functools import wraps
from flask import request
from jwt_utils import get_current_user
from models.libraries import Library
from models.media import Media
from error_handler import authentication_error, authorization_error, not_found_error, handle_api_error

"""
principe d'un décorateur :
rajouter un comportement a une fonction sans modifier son code source

comme ca simon on toute pas aux fonction 1 à 1 de toute l'api
"""


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return handle_api_error(authentication_error())
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return handle_api_error(authentication_error())
        if user.role != 'admin':
            return handle_api_error(authorization_error("Accès admin requis"))
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def require_trusted_or_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return handle_api_error(authentication_error())
        if user.role not in ['trusted', 'admin']:
            return handle_api_error(authorization_error("Permissions insuffisantes. Rôle trusted ou admin requis"))
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def require_owner_or_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return handle_api_error(authentication_error())
        
        if user.role == 'admin':
            request.current_user = user
            return f(*args, **kwargs)
        
        # On vérifie si il propriétaire de la biblio ou média
        library_id = kwargs.get('library_id')
        media_id = kwargs.get('media_id')
        
        if library_id:
            library = Library.query.get(library_id)
            if not library:
                return handle_api_error(not_found_error("library", library_id))
            if library.owner_id != user.id:
                return handle_api_error(authorization_error("Vous n'êtes pas propriétaire de cette vidéothèque"))
        
        if media_id:
            media = Media.query.get(media_id)
            if not media:
                return handle_api_error(not_found_error("media", media_id))
            library = Library.query.get(media.library_id)
            if not library or library.owner_id != user.id:
                return handle_api_error(authorization_error("Vous n'êtes pas propriétaire de ce média"))
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def require_self_or_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return handle_api_error(authentication_error())
        
        user_id = kwargs.get('user_id')
        if user.role != 'admin' and user.id != user_id:
            return handle_api_error(authorization_error("Vous ne pouvez modifier que votre propre profil"))
        
        request.current_user = user
        return f(*args, **kwargs)
    return decorated_function

def can_view_media(user, media):
    if media.visibility == 'public':
        return True
    if not user:
        return False

    library = Library.query.get(media.library_id)
    if not library:
        return False

    # Pour les médias privés : propriétaire de la bibliothèque, trusted ou admin peuvent voir
    return library.owner_id == user.id or user.role in ['trusted', 'admin']

def can_view_library(user, library):
    if library.visibility == 'public':
        return True
    if not user:
        return False

    # Pour les bibliothèques privées : propriétaire, trusted ou admin peuvent voir
    return library.owner_id == user.id or user.role in ['trusted', 'admin']

