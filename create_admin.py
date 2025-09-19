from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    db.create_all()  # Crée toutes les tables
    # Crée un super admin par défaut si inexistant
    if not User.query.filter_by(email='admin@example.com').first():
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('motdepasse')  # méthode à définir dans ton modèle
        db.session.add(admin)
        db.session.commit()
