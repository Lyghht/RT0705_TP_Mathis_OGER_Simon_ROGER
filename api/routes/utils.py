from flask import jsonify, request


def get_pagination_params():
    """
    Récupère et valide les paramètres de pagination depuis l'URL de la requête
    Retourne la tuple: (numéro_de_la_page, nombre_d_éléments_par_page)
    """

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if page < 1:
        page = 1
    
    # Pas plus de 100 faut pas abusé
    if per_page < 1 or per_page > 100:
        per_page = 20
    
    return page, per_page


class FilteredPagination:
    """
    utilisé pour faire le pont entre la liste python et la pagination sqlalchemy

    paginated_response attend un objet de type pagination (hérité de l'objet query) qui nécéssite :
        items, page, per_page
    donc vus qu'on a une liste python de base on ajoute les param nécéssaire

    """
    def __init__(self, items, page, per_page):
        self.items = items
        self.page = page
        self.per_page = per_page


def paginated_response(pagination, serializer_func, total_real=None):
    """
    pagination : informations sur la pagination (page actuelle, total, etc.)
    serializer_func : fonction qui transforme chaque élément en dico
    total_real : nombre total personnalisé
    
    Ex de réponse :
    {
        "data": [
            {"id": 1, "name": "Exemple"},
            {"id": 2, "name": "Autre"}
        ],
        "pagination": {
            "page": 1,
            "per_page": 20,
            "total": 50,
            "pages": 3
        }
    }
    """
    # Utilise le total personnalisé sinon le total de la pagination
    total = total_real if total_real is not None else pagination.total
    per_page = pagination.per_page
    
    # Calcul du nombre total de pages
    # Ex : 50 éléments / 20 par page = 3 pages
    total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1
    
    # Transformation de chaque élément en dico JSON
    serialized_items = [serializer_func(item) for item in pagination.items]
    
    return jsonify({
        'data': serialized_items,
        'pagination': {
            'page': pagination.page,
            'per_page': per_page,
            'total': total,
            'pages': total_pages
        }
    }), 200