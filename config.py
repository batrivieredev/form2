import os

# dossier courant : app/
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Base de données SQLite dans app/instance/
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(basedir, "instance", "app.db")
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Uploads dans app/instance/uploads
    UPLOAD_FOLDER = os.path.join(basedir, "instance", "uploads")
