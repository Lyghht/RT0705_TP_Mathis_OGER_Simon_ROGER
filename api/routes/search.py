from flask import Blueprint, request, jsonify
from sqlalchemy import or_, func

from models.media import Media, Genre, MediaGenre, Franchise
from models.persons import Person, MediaPerson
from models.users import User
from models.libraries import Library
from decorators import can_view_media, can_view_library
from jwt_utils import get_current_user
from routes.utils import get_pagination_params, paginated_response, FilteredPagination
from error_handler import handle_exception

search_bp = Blueprint('search', __name__)


@search_bp.route('/persons', methods=['GET'])
def search_persons():
    """
    - q : texte de recherche par nom
    - page : numéro de la page
    - per_page : nb de resultat par page
    
    Ex : /api/search/persons?q=Jean&page=1&per_page=10
    """
    try:
        param_recherche = request.args.get('q', '')
        page, per_page = get_pagination_params()
        liste_perssonne = Person.query
        
        # filtrage selon le nom (ilike = insensitive like, cd: LIKE en SQL))
        if param_recherche:
            # Utilisation de paramètres pour éviter les injections SQL
            search_pattern = f'%{param_recherche}%'
            liste_perssonne = liste_perssonne.filter(Person.name.ilike(search_pattern))

        #.paginate hérité de l'objet query, retourne un objet de pagination
        pagination = liste_perssonne.paginate(page=page, per_page=per_page, error_out=False)

        # appliquer la lambda fonction cad .to_dict à toutes les personnes
        return paginated_response(pagination, lambda person: person.to_dict())
    except Exception as e:
        return handle_exception(e)


@search_bp.route('/users', methods=['GET'])
def search_users():
    """
    - q : texte de recherche : username ou email
    - role : filtre par rôle 
    - page : numéro de la page
    - per_page : nb de resultat par page
    
    Exemple : /api/search/users?q=admin&role=admin&page=1
    """
    try:
        param_recherche = request.args.get('q', '')
        role = request.args.get('role')
        page, per_page = get_pagination_params()

        liste_users = User.query
        
        if param_recherche:
            # Recherche par nom d'utilisateur ou mail (paramètres pour sécurité)
            search_pattern = f'%{param_recherche}%'
            liste_users = liste_users.filter(
                (User.username.ilike(search_pattern)) | (User.email.ilike(search_pattern))
            )
        if role:
            # Filtre par role (admin, trusted, user)
            liste_users = liste_users.filter_by(role=role)

        pagination = liste_users.paginate(page=page, per_page=per_page, error_out=False)
        
        current_user = get_current_user()
        is_admin = current_user is not None and current_user.role == "admin"

        # si admin : on retourne les emails en plus
        return paginated_response(pagination, lambda user: user.to_dict(is_admin))
    except Exception as e:
        return handle_exception(e)


@search_bp.route('/media', methods=['GET'])
def search_media():
    """

    utilisation de FilteredPagination afin de convertir un objet de type liste
    en objet de type pagination (pagination heritant de query obliger pour paginer)

    - q : texte de recherche par titre
    - library_id : filtre par vidéothèque
    - visibility : filtre par visibilité
    - franchise_id : filtre par franchise
    - genre_id : filtre par genre
    - person_id : filtre par acteur associée
    - page : numéro de la page
    - per_page : nb de resultat par page

    Ex : /api/search/media?q=Star&genre_id=5&franchise_id=1&person_id=1&page=1&per_page=10
    """
    try:
        
        user = get_current_user()

        param_recherche = request.args.get('q', '')
        library_id = request.args.get('library_id', type=int)
        visibility = request.args.get('visibility')
        genre_id = request.args.get('genre_id', type=int)
        person_id = request.args.get('person_id', type=int)
        franchise_id = request.args.get('franchise_id', type=int)
        
        page, per_page = get_pagination_params()

        liste_medias = Media.query
        
        if param_recherche:
            # Recherche sécurisée avec paramètres
            search_pattern = f'%{param_recherche}%'
            liste_medias = liste_medias.filter(Media.title.ilike(search_pattern))
        if library_id:
            liste_medias = liste_medias.filter_by(library_id=library_id)
        if visibility:
            liste_medias = liste_medias.filter_by(visibility=visibility)
        if genre_id:
            # Jointure avec la table de liaison pour filtrer par genre
            liste_medias = liste_medias.join(MediaGenre).filter(MediaGenre.genre_id == genre_id)
        if person_id:
            # Jointure avec la table de liaison pour filtrer par personne
            liste_medias = liste_medias.join(MediaPerson).filter(MediaPerson.person_id == person_id)
        if franchise_id:
            # Jointure avec la table de liaison pour filtrer par franchise
            liste_medias = liste_medias.join(Franchise).filter(Franchise.id == franchise_id)

        pagination = liste_medias.paginate(page=page, per_page=per_page, error_out=False)

        # on vérifie que l'utilisateur a le droit de voir les média mais les admin peuvent tout voir
        visible_medias = [media for media in pagination.items if can_view_media(user, media)]
        
        # Calculer le total réel de tous les médias visibles
        # Pour les admins, tous les médias sont visibles donc on utilise pagination.total
        # Sinon, on doit compter uniquement les médias publics ou ceux de l'utilisateur
        if user and user.role == 'admin':
            total_visible = pagination.total
        else:
            # Compter les médias visibles en parcourant tous les résultats de la requête
            total_visible = sum(1 for media in liste_medias.all() if can_view_media(user, media))
        
        filtered_pagination = FilteredPagination(
            items=visible_medias,
            page=pagination.page,
            per_page=pagination.per_page
        )

        return paginated_response(pagination=filtered_pagination, serializer_func=lambda media: media.to_dict_summary(), total_real=total_visible)
    except Exception as e:
        return handle_exception(e)


@search_bp.route('/libraries', methods=['GET'])
def search_libraries():
    """

    utilisation de FilteredPagination afin de convertir un objet liste en objet pagination
    heritant de query

    - q : texte de recherche par nom
    - owner_id : filtre par propriétaire 
    - visibility : filtre par visibilité
    - page : numéro de la page
    - per_page : nb de resultat par page
    
    Exemple : /api/search/libraries?q=Ma&visibility=public&page=1
    """
    try:
        user = get_current_user()

        param_recherche = request.args.get('q', '')
        owner_id = request.args.get('owner_id', type=int)
        visibility = request.args.get('visibility')
        
        page, per_page = get_pagination_params()

        liste_libraries = Library.query
        
        # Filtrer pour n'inclure que les vidéothèques visibles par l'utilisateur AVANT la pagination
        # Les admins et trusted peuvent tout voir, sinon on filtre : publiques OU propriété de l'utilisateur
        if not (user and user.role in ['admin', 'trusted']):
            if user:
                # Inclure les vidéothèques publiques OU celles de l'utilisateur
                liste_libraries = liste_libraries.filter(
                    or_(Library.visibility == 'public', Library.owner_id == user.id)
                )
            else:
                # Utilisateur non connecté : seulement les vidéothèques publiques
                liste_libraries = liste_libraries.filter_by(visibility='public')
        
        if param_recherche:
            # Recherche par nom ou description (paramètres pour sécurité)
            search_pattern = f'%{param_recherche}%'
            liste_libraries = liste_libraries.filter(
                (Library.name.ilike(search_pattern)) | (Library.description.ilike(search_pattern))
            )
        if owner_id:
            liste_libraries = liste_libraries.filter_by(owner_id=owner_id)
        if visibility:
            liste_libraries = liste_libraries.filter_by(visibility=visibility)

        pagination = liste_libraries.paginate(page=page, per_page=per_page, error_out=False)

        # On vérifie que l'utilisateur a le droit de voir les libraries (double vérification)
        visible_libraries = [library for library in pagination.items if can_view_library(user, library)]
        
        # Calculer le total réel de toutes les vidéothèques visibles
        # Pour les admins et trusted, toutes les vidéothèques sont visibles donc on utilise pagination.total
        # Sinon, on doit compter uniquement les vidéothèques publiques ou celles de l'utilisateur
        if user and user.role in ['admin', 'trusted']:
            total_visible = pagination.total
        else:
            # Compter les vidéothèques visibles en parcourant tous les résultats de la requête
            total_visible = sum(1 for library in liste_libraries.all() if can_view_library(user, library))
        
        filtered_pagination = FilteredPagination(
            items=visible_libraries,
            page=pagination.page,
            per_page=pagination.per_page
        )

        return paginated_response(pagination=filtered_pagination, serializer_func=lambda library: library.to_dict(), total_real=total_visible)
    except Exception as e:
        return handle_exception(e)


@search_bp.route('/genres', methods=['GET'])
def search_genres():
    """    
    - q : texte de recherche par nom
    - page : numéro de la page
    - per_page : nb de resultat par page
    
    Exemple : /api/search/genres?q=Action&page=1
    """
    try:
        param_recherche = request.args.get('q', '')
        page, per_page = get_pagination_params()

        liste_genres = Genre.query
        
        if param_recherche:
            # Recherche par nom (paramètres pour sécurité)
            search_pattern = f'%{param_recherche}%'
            liste_genres = liste_genres.filter(Genre.name.ilike(search_pattern))

        pagination = liste_genres.paginate(page=page, per_page=per_page, error_out=False)

        return paginated_response(pagination, lambda genre: genre.to_dict())
    except Exception as e:
        return handle_exception(e)


@search_bp.route('/franchises', methods=['GET'])
def search_franchises():
    """
    - q : texte de recherche par nom
    - page : numéro de la page
    - per_page : nb de resultat par page
    
    Exemple : /api/search/franchises?q=Star&page=1
    """
    try:
        param_recherche = request.args.get('q', '')
        page, per_page = get_pagination_params()
        liste_franchises = Franchise.query
        
        if param_recherche:
            # Recherche par nom ou description (paramètres pour sécurité)
            search_pattern = f'%{param_recherche}%'
            liste_franchises = liste_franchises.filter(
                (Franchise.name.ilike(search_pattern)) | (Franchise.description.ilike(search_pattern))
            )

        pagination = liste_franchises.paginate(page=page, per_page=per_page, error_out=False)
        
        return paginated_response(pagination, lambda franchise: franchise.to_dict())
    except Exception as e:
        return handle_exception(e)


@search_bp.route('/stats', methods=['GET'])
def get_stats():
    """
    Retourne les statistiques nb médias et vidéothèques dont privés
    """
    try:
        total_media = Media.query.count()
        total_libraries = Library.query.count()
        
        return jsonify({
            'media': total_media,
            'libraries': total_libraries
        }), 200
    except Exception as e:
        return handle_exception(e)


