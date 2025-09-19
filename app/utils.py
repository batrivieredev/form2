import os
from werkzeug.utils import secure_filename
from flask import current_app

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_file(file, dossier_id):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        dossier_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], f'dossier_{dossier_id}')
        os.makedirs(dossier_folder, exist_ok=True)
        file_path = os.path.join(dossier_folder, filename)
        file.save(file_path)
        return filename
    return None
