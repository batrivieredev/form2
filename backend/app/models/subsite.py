from backend.app import db
from datetime import datetime
from sqlalchemy.orm import relationship
from slugify import slugify

class Subsite(db.Model):
    __tablename__ = 'subsites'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    access_code = db.Column(db.String(128), nullable=False)

    users = relationship('User', backref='subsite', lazy=True)
    forms = relationship('Form', backref='subsite', lazy=True)
    messages = relationship('Message', backref='subsite', lazy=True)
    files = relationship('File', backref='subsite', lazy=True)

    def __init__(self, name, description=None, access_code=None):
        self.name = name
        self.slug = slugify(name)
        self.description = description
        self.access_code = access_code

    def get_admin_url(self):
        return f'/admin/{self.slug}'

    def get_user_url(self):
        return f'/user/{self.slug}'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'is_active': self.is_active,
            'user_count': len(self.users),
            'form_count': len(self.forms)
        }

    def __repr__(self):
        return f'<Subsite {self.name}>'
