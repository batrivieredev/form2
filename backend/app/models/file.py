from backend.app import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from uuid import uuid4

class File(db.Model):
    __tablename__ = 'files'

    id = db.Column(db.Integer, primary_key=True)
    original_name = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(50), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)

    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subsite_id = db.Column(db.Integer, db.ForeignKey('subsites.id'), nullable=False)
    form_response_id = db.Column(db.Integer, db.ForeignKey('form_responses.id'))

    def __init__(self, original_name, file_type, file_size, owner_id, subsite_id,
                 form_response_id=None, description=None, is_public=False):
        self.original_name = original_name
        self.filename = self._generate_unique_filename(original_name)
        self.file_type = file_type
        self.file_size = file_size
        self.owner_id = owner_id
        self.subsite_id = subsite_id
        self.form_response_id = form_response_id
        self.description = description
        self.is_public = is_public

    @staticmethod
    def _generate_unique_filename(original_name):
        _, ext = os.path.splitext(secure_filename(original_name))
        return f"{uuid4().hex}{ext}"

    def rename(self, new_name):
        self.original_name = new_name
        db.session.commit()

    def get_file_path(self, upload_folder):
        return os.path.join(upload_folder, self.filename)

    def get_download_url(self):
        return f"/api/files/{self.id}/download"

    def can_access(self, user):
        if user.is_admin():
            return True
        if user.is_subadmin() and user.subsite_id == self.subsite_id:
            return True
        if user.id == self.owner_id:
            return True
        if self.is_public and user.subsite_id == self.subsite_id:
            return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'original_name': self.original_name,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'created_at': self.created_at.isoformat(),
            'description': self.description,
            'is_public': self.is_public,
            'owner_id': self.owner_id,
            'subsite_id': self.subsite_id,
            'form_response_id': self.form_response_id,
            'download_url': self.get_download_url()
        }
