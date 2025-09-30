from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # user / sub_admin / super_admin
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'), nullable=True)

    # Relations
    site = db.relationship(
        'Site',
        back_populates='users',
        foreign_keys=[site_id]
    )
    dossiers = db.relationship('Dossier', backref='user', lazy=True)

    # Sites dont l'utilisateur est sub-admin
    managed_sites = db.relationship(
        'Site',
        back_populates='sub_admin',
        foreign_keys='Site.sub_admin_id'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Site(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)  # partie du lien
    sub_admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    # Relations
    users = db.relationship(
        'User',
        back_populates='site',
        foreign_keys='User.site_id'
    )
    sub_admin = db.relationship(
        'User',
        back_populates='managed_sites',
        foreign_keys=[sub_admin_id]
    )
    dossiers = db.relationship('Dossier', backref='site', lazy=True)


class Dossier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    job_type = db.Column(db.String(100))
    status = db.Column(db.String(50), default='déposé')  # déposé / en cours / validé
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    site_id = db.Column(db.Integer, db.ForeignKey('site.id'))
    files = db.relationship('File', backref='dossier', lazy=True)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    dossier_id = db.Column(db.Integer, db.ForeignKey('dossier.id'))
