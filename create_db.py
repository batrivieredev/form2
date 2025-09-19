"""
create_db.py
Script d'initialisation de la base PostgreSQL avec SQLAlchemy
"""
from app import create_app, db
from app.models import User, Site, Dossier, Message

app = create_app()

with app.app_context():
    print("📦 Création de la base et des tables...")
    db.drop_all()
    db.create_all()
    print("✅ Base initialisée avec succès !")

    # Création d'un super admin par défaut
    super_admin = User(
        username="superadmin",
        email="superadmin@baptisteriviere.fr",
        role="super_admin"
    )
    super_admin.set_password("superadmin123")

    db.session.add(super_admin)
    db.session.commit()
    print("👑 Super admin créé : superadmin / superadmin123")
