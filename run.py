from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'change_this_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')

    # Crée les dossiers si manquants
    os.makedirs('instance', exist_ok=True)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'user.login'

    # ---------- USER LOADER ----------
    from app.models import User  # nécessaire pour user_loader

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Migration
    migrate = Migrate(app, db)

    # Blueprints
    from app.routes.super_admin import super_admin_bp
    from app.routes.sub_admin import sub_admin_bp
    from app.routes.user import user_bp
    from app.routes.messaging import messaging_bp

    app.register_blueprint(super_admin_bp, url_prefix='/super_admin')
    app.register_blueprint(sub_admin_bp, url_prefix='/sub_admin')
    app.register_blueprint(user_bp)
    app.register_blueprint(messaging_bp, url_prefix='/messaging')

    return app

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Run the Flask application.")
    parser.add_argument('--port', type=int, default=5001, help='Port to run the application on')
    args = parser.parse_args()

    app = create_app()
    app.run(debug=True, port=args.port)
