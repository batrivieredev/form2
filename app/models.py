from datetime import datetime
from app import db
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')

    sites = db.relationship('Site', backref='owner', lazy='dynamic')
    dossiers = db.relationship('Dossier', backref='owner', lazy='dynamic')
    messages_sent = db.relationship('Message', foreign_keys='Message.sender_id', backref='sender', lazy='dynamic')
    messages_received = db.relationship('Message', foreign_keys='Message.recipient_id', backref='recipient', lazy='dynamic')


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)



class Site(db.Model):
    __tablename__ = 'sites'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    dossiers = db.relationship('Dossier', backref='site', lazy='dynamic')
    users = db.relationship('User', secondary='site_users', backref='sites_assoc')


site_users = db.Table('site_users',
    db.Column('site_id', db.Integer, db.ForeignKey('sites.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class Dossier(db.Model):
    __tablename__ = 'dossiers'
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(64), nullable=False)
    nom = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    telephone = db.Column(db.String(20))
    metier = db.Column(db.String(100))
    statut = db.Column(db.String(20), default='déposé')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    site_id = db.Column(db.Integer, db.ForeignKey('sites.id'))

    fichiers = db.relationship('Fichier', backref='dossier', lazy='dynamic')


class Fichier(db.Model):
    __tablename__ = 'fichiers'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    dossier_id = db.Column(db.Integer, db.ForeignKey('dossiers.id'))


class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    body = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
