import os
from app import create_app, db
from app.models import User, Message, Dossier, Site, File  # ajoute Message ici

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

    # Création d'un utilisateur test si inexistant
    user_test = User.query.filter_by(username="user_test").first()
    if not user_test:
        user_test = User(
            username="user_test",
            email="user_test@example.com",
            role="user"
        )
        user_test.set_password("test123")
        db.session.add(user_test)
        db.session.commit()
        print("👤 Utilisateur test créé : user_test / test123")
    else:
        print("👤 Utilisateur test déjà existant")

    # Création d'un message test entre superadmin et user_test si aucun message
    if not Message.query.first():
        test_message = Message(
            sender_id=super_admin.id,
            recipient_id=user_test.id,
            subject="Bienvenue",
            body="Ceci est un message de test pour la messagerie privée."
        )
        db.session.add(test_message)
        db.session.commit()
        print("✉️ Message test créé entre superadmin et user_test")
    else:
        print("✉️ Messages existants détectés, aucun message test ajouté")

    # Vérification finale
    print("Chemin DB :", app.config['SQLALCHEMY_DATABASE_URI'])
    print("Tables :", db.inspect(db.engine).get_table_names())
    print("Utilisateurs :", [u.username for u in User.query.all()])
    print("Messages :", [(m.sender.username, m.recipient.username, m.subject) for m in Message.query.all()])

    # Exemple pour vérifier la colonne slug dans Site
    if 'site' in db.inspect(db.engine).get_table_names():
        site_columns = db.inspect(db.engine).get_columns('site')
        print("Colonnes site :", [col['name'] for col in site_columns])
