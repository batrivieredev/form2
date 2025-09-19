import os
from app import create_app, db
from app.models import User, Dossier, Site, File

# Crée l'application Flask
app = create_app()

# Crée le dossier instance si inexistant
instance_dir = os.path.join(os.path.dirname(__file__), 'instance')
os.makedirs(instance_dir, exist_ok=True)

with app.app_context():
    print("📦 Création de la base et des tables...")

    # Supprime toutes les tables existantes et recrée-les
    db.drop_all()
    db.create_all()
    print("✅ Tables créées avec succès !")

    # Création du super admin si inexistant
    super_admin = User.query.filter_by(username="superadmin").first()
    if not super_admin:
        super_admin = User(
            username="superadmin",
            email="superadmin@baptisteriviere.fr",
            role="super_admin"
        )
        super_admin.set_password("superadmin123")
        db.session.add(super_admin)
        db.session.commit()
        print("👑 Super admin créé : superadmin / superadmin123")
    else:
        print("👑 Super admin déjà existant")

    # Vérification finale
    print("Chemin DB :", app.config['SQLALCHEMY_DATABASE_URI'])
    print("Tables :", db.inspect(db.engine).get_table_names())
    print("Utilisateurs :", [u.username for u in User.query.all()])
