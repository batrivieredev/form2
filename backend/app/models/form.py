from backend.app import db
from datetime import datetime
import json

class Form(db.Model):
    __tablename__ = 'forms'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    structure = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subsite_id = db.Column(db.Integer, db.ForeignKey('subsites.id'), nullable=False)
    responses = db.relationship('FormResponse', backref='form', lazy=True, cascade='all, delete-orphan')

    def __init__(self, title, structure, creator_id, subsite_id, description=None):
        self.title = title
        self.description = description
        self.structure = structure if isinstance(structure, dict) else json.loads(structure)
        self.creator_id = creator_id
        self.subsite_id = subsite_id

    def add_field(self, field_data):
        if not isinstance(self.structure, dict):
            self.structure = {}
        self.structure['fields'] = self.structure.get('fields', [])
        self.structure['fields'].append(field_data)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'structure': self.structure,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'creator_id': self.creator_id,
            'subsite_id': self.subsite_id,
            'response_count': len(self.responses)
        }

class FormResponse(db.Model):
    __tablename__ = 'form_responses'

    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('forms.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    answers = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    is_draft = db.Column(db.Boolean, default=True)

    files = db.relationship('File', backref='form_response', lazy=True)

    def __init__(self, form_id, user_id, answers=None):
        self.form_id = form_id
        self.user_id = user_id
        self.answers = answers or {}

    def submit(self):
        self.is_draft = False
        self.submitted_at = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'form_id': self.form_id,
            'user_id': self.user_id,
            'answers': self.answers,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'is_draft': self.is_draft,
            'files': [f.to_dict() for f in self.files]
        }
