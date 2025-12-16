from flask import jsonify, request
from extensions import db

"""
fonctionnement du gestionnaire d'erreurs :
Classe APIError qui est une exception
Dictionnaire ERROR_CODES qui contient les codes d'erreurs
format_error transforme l'erreur en un dictionnaire
handle_api_error qui gère l'erreur et renvoie un json
handle_exception qui gère l'erreur et renvoie un json
"""

class APIError(Exception):
    def __init__(self, code, message, status_code=400, details=None, resource=None, resource_id=None):
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or []
        self.resource = resource
        self.resource_id = resource_id

ERROR_CODES = {
    'MISSING_FIELD': 'MISSING_FIELD',
    'AUTHENTICATION_ERROR': 'AUTHENTICATION_ERROR',
    'AUTHORIZATION_ERROR': 'AUTHORIZATION_ERROR',
    'RESOURCE_NOT_FOUND': 'RESOURCE_NOT_FOUND',
    'RESOURCE_ALREADY_EXISTS': 'RESOURCE_ALREADY_EXISTS',
    'RESOURCE_CONFLICT': 'RESOURCE_CONFLICT',
    'METHOD_NOT_ALLOWED': 'METHOD_NOT_ALLOWED',
    'INTERNAL_SERVER_ERROR': 'INTERNAL_SERVER_ERROR'
}

def format_error(error):
    error_dict = {
        "code": error.code,
        "message": error.message
    }
    
    if error.details:
        error_dict["details"] = error.details
    
    if error.resource:
        error_dict["resource"] = error.resource
        if error.resource_id:
            error_dict["resource_id"] = error.resource_id
    
    error_dict["path"] = request.path
    
    return {"error": error_dict}

def handle_api_error(error):
    return jsonify(format_error(error)), error.status_code

def handle_exception(e):
    db.session.rollback()
    
    try:
        status = e.code
    except AttributeError:
        status = 500
    
    return jsonify(format_error(APIError(
        code=ERROR_CODES['INTERNAL_SERVER_ERROR'],
        message="Une erreur interne s'est produite. Veuillez réessayer plus tard.",
        status_code= status
    ))), status

def missing_field_error(field_name):
    return APIError(
        code=ERROR_CODES['MISSING_FIELD'],
        message=f"Le champ '{field_name}' est requis",
        status_code=400,
        details=[{"field": field_name, "message": f"Le champ '{field_name}' est requis"}]
    )

def missing_fields_error(fields):
    details = [{"field": field, "message": f"Le champ '{field}' est requis"} for field in fields]
    return APIError(
        code=ERROR_CODES['MISSING_FIELD'],
        message=f"Champs requis: {', '.join(fields)}",
        status_code=400,
        details=details
    )

def authentication_error(message="Authentification requise"):
    return APIError(
        code=ERROR_CODES['AUTHENTICATION_ERROR'],
        message=message,
        status_code=401
    )

def authorization_error(message="Accès refusé"):
    return APIError(
        code=ERROR_CODES['AUTHORIZATION_ERROR'],
        message=message,
        status_code=403
    )

def not_found_error(resource, resource_id=None):
    message = f"{resource.capitalize()} non trouvé"
    if resource_id:
        message += f" (ID: {resource_id})"
    return APIError(
        code=ERROR_CODES['RESOURCE_NOT_FOUND'],
        message=message,
        status_code=404,
        resource=resource,
        resource_id=resource_id
    )

def already_exists_error(resource, field=None, value=None):
    if field and value:
        message = f"{resource.capitalize()} avec {field} '{value}' existe déjà"
    else:
        message = f"{resource.capitalize()} existe déjà"
    return APIError(
        code=ERROR_CODES['RESOURCE_ALREADY_EXISTS'],
        message=message,
        status_code=409,
        resource=resource
    )

def conflict_error(message, resource=None):
    return APIError(
        code=ERROR_CODES['RESOURCE_CONFLICT'],
        message=message,
        status_code=409,
        resource=resource
    )

def method_not_allowed_error(message, resource=None):
    return APIError(
        code=ERROR_CODES['METHOD_NOT_ALLOWED'],
        message=message,
        status_code=405,
        resource=resource
    )
