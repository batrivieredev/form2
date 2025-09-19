import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'user.login'  # redirection vers login si non connecté

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(__file__), 'static'))

    app.config.from_object('config.Config')

    # Crée le dossier instance si nécessaire
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)

    # Importer les blueprints
    from app.routes.user import user_bp
    app.register_blueprint(user_bp, url_prefix='/user')

    from app.routes.auth import auth_bp
    app.register_blueprint(auth_bp)

    # User loader pour Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Optionnel : debug template
    print("Template folder:", app.template_folder)
    print("Templates disponibles:", os.listdir(app.template_folder))

    return app
