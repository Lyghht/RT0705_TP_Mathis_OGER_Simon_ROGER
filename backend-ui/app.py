import os
from flask import Flask, render_template
from utils.utils import get_current_user
from routes.auth import auth_bp
from routes.pages import pages_bp
from routes.admin import admin_bp
from routes.profile import profile_bp
from routes.media import media_bp
from routes.persons import persons_bp
from routes.add_media import add_media_bp
from routes.libraries import libraries_bp
from routes.franchises import franchises_bp

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY_UI')

app.register_blueprint(add_media_bp, url_prefix='/add-media')
app.register_blueprint(franchises_bp, url_prefix='/franchises')
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(auth_bp)
app.register_blueprint(libraries_bp)
app.register_blueprint(media_bp, url_prefix='/media')
app.register_blueprint(pages_bp)
app.register_blueprint(persons_bp, url_prefix='/persons')
app.register_blueprint(profile_bp, url_prefix='/profile')

@app.context_processor
def inject_user():
    return {'current_user': get_current_user()}

@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html', error_code=404, error_message="Page non trouvée"), 404

@app.errorhandler(500)
def internal_server_error(error):
    return render_template('error.html', error_code=500, error_message="Erreur interne du serveur"), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT_UI'))
