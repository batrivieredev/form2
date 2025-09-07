import os
import pymysql
pymysql.install_as_MySQLdb()  # Permet à SQLAlchemy d'utiliser PyMySQL à la place de MySQLdb

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from backend.config import Config

# Initialisation des extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# Importer tous les modèles pour que Flask-Migrate puisse les détecter
from backend.app.models import User, Subsite, Form, FormResponse, Message, Ticket, File

def create_app(config_class=Config):
    # Définir le chemin de base pour éviter les problèmes de chemins relatifs
    basedir = os.path.abspath(os.path.dirname(__file__))

    app = Flask(
        __name__,
        static_folder=os.path.join(basedir, '../../../frontend/static'),
        template_folder=os.path.join(basedir, '../../../frontend/templates')
    )

    # Charger la configuration
    app.config.from_object(config_class)

    # Initialiser les extensions avec l'app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    CORS(app)

    # Importer et enregistrer les blueprints
    from backend.app.routes.auth import auth_bp
    from backend.app.routes.admin import admin_bp
    from backend.app.routes.user import user_bp
    from backend.app.routes.api import api_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Créer le dossier d'uploads s'il n'existe pas
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    # Route principale pour servir la page index
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app
