import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Création des instances globales
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'user.login'  # redirection si non connecté

def create_app():
    """Création et configuration de l'application Flask"""
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static')
    )

    # Chargement de la configuration
    app.config.from_object('config.Config')

    # Crée le dossier d'uploads si manquant
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'static/uploads'), exist_ok=True)

    # Initialisation des extensions
    db.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        # Import des modèles pour éviter les imports circulaires
        from app import models
        from app.models import User

        # Fonction pour charger l'utilisateur
        @login_manager.user_loader
        def load_user(user_id):
            try:
                return db.session.get(User, int(user_id))
            except Exception:
                return None

        # Crée les tables si elles n'existent pas
        db.create_all()

    # Import et enregistrement des blueprints
    from app.routes.user import user_bp
    from app.routes.super_admin import super_admin_bp
    from app.routes.sub_admin import sub_admin_bp

    app.register_blueprint(user_bp)
    app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
    app.register_blueprint(sub_admin_bp, url_prefix='/sub_admin')

    from app.routes.messaging import messaging_bp
    app.register_blueprint(messaging_bp, url_prefix='/messaging')

    return app
