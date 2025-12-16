from flask import Flask
from flask_cors import CORS
from werkzeug.exceptions import MethodNotAllowed
from extensions import db
from error_handler import handle_exception, handle_api_error, method_not_allowed_error
import os

# Enregistrement des Blueprints
from routes.auth import auth_bp
from routes.media import media_bp
from routes.libraries import libraries_bp
from routes.users import users_bp
from routes.franchises import franchises_bp
from routes.genres import genres_bp
from routes.persons import persons_bp
from routes.search import search_bp

app = Flask(__name__)
CORS(app)

#Si la méthode n'existe pas pour le chemin
@app.errorhandler(MethodNotAllowed)
def handle_method_not_allowed(error):
    return handle_api_error(method_not_allowed_error("Méthode non trouvée pour cette ressource"))

#Erreur générique qui ne serais pas traité
@app.errorhandler(Exception)
def handle_generic_error(e):
    return handle_exception(e)

# Connexion à la base de données
app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres_db:5432/{os.getenv('POSTGRES_DB')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(media_bp, url_prefix='/api/media')
app.register_blueprint(libraries_bp, url_prefix='/api/libraries')
app.register_blueprint(users_bp, url_prefix='/api/users')
app.register_blueprint(franchises_bp, url_prefix='/api/franchises')
app.register_blueprint(genres_bp, url_prefix='/api/genres')
app.register_blueprint(persons_bp, url_prefix='/api/persons')
app.register_blueprint(search_bp, url_prefix='/api/search')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)