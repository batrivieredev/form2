# app.py
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'user.login'  # Nom exact de ta route login

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # ton fichier config.py

    # Crée le dossier instance si nécessaire
    os.makedirs(app.instance_path, exist_ok=True)

    # Initialisation extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Importer modèles pour flask-login
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Importer Blueprints
    from app.routes.user import user_bp
    from app.routes.super_admin import super_admin_bp
    from app.routes.sub_admin import sub_admin_bp
    from app.routes.messaging import messaging_bp

    # Enregistrement Blueprints
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
    app.register_blueprint(sub_admin_bp, url_prefix='/sub_admin')
    app.register_blueprint(messaging_bp, url_prefix='/messages')

    # Optionnel : page d’accueil simple
    @app.route('/')
    def index():
        return "Bienvenue sur l'application !"

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
