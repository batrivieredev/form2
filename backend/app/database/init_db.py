from backend.app import create_app, db
from backend.app.models import User
from werkzeug.security import generate_password_hash
import os

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()

        # Check if admin user exists
        admin = User.query.filter_by(email=os.getenv('ADMIN_EMAIL')).first()
        if not admin:
            # Create admin user
            admin = User(
                email=os.getenv('ADMIN_EMAIL', 'admin@baptisteriviere.fr'),
                username=os.getenv('ADMIN_USERNAME', 'admin'),
                role='admin'
            )
            admin.password_hash = generate_password_hash(
                os.getenv('ADMIN_PASSWORD', 'change-this-admin-password')
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created successfully")
        else:
            print("Admin user already exists")

if __name__ == '__main__':
    init_db()
