from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from backend.app import db
from backend.app.models import File, FormResponse
from backend.app.routes.admin import require_admin_or_subadmin
from werkzeug.utils import secure_filename
import os
import uuid

files_bp = Blueprint('files', __name__)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def get_file_type(filename):
    """Get file type from extension"""
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['pdf']:
        return 'document'
    elif ext in ['jpg', 'jpeg', 'png', 'gif']:
        return 'image'
    return 'other'

@files_bp.route('/files', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400

    # Get form_response_id if provided
    form_response_id = request.form.get('form_response_id', type=int)
    if form_response_id:
        form_response = FormResponse.query.get_or_404(form_response_id)
        if form_response.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403

    # Secure filename and save file
    original_name = secure_filename(file.filename)
    file_ext = original_name.rsplit('.', 1)[1].lower()
    filename = f"{uuid.uuid4().hex}.{file_ext}"

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Create file record
    file_record = File(
        original_name=original_name,
        filename=filename,
        file_type=get_file_type(original_name),
        file_size=os.path.getsize(file_path),
        owner_id=current_user.id,
        subsite_id=current_user.subsite_id,
        form_response_id=form_response_id,
        description=request.form.get('description'),
        is_public=request.form.get('is_public', type=bool, default=False)
    )

    try:
        db.session.add(file_record)
        db.session.commit()
        return jsonify(file_record.to_dict()), 201
    except Exception as e:
        # Delete file if database operation fails
        os.remove(file_path)
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@files_bp.route('/files/<int:id>', methods=['GET'])
@login_required
def get_file(id):
    file = File.query.get_or_404(id)

    if not file.can_access(current_user):
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(file.to_dict())

@files_bp.route('/files/<int:id>/download', methods=['GET'])
@login_required
def download_file(id):
    file = File.query.get_or_404(id)

    if not file.can_access(current_user):
        return jsonify({'error': 'Unauthorized'}), 403

    file_path = file.get_file_path(current_app.config['UPLOAD_FOLDER'])
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    return send_file(
        file_path,
        download_name=file.original_name,
        as_attachment=True
    )

@files_bp.route('/files/<int:id>', methods=['PUT'])
@require_admin_or_subadmin
def update_file(id):
    file = File.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and file.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if 'original_name' in data:
        file.original_name = secure_filename(data['original_name'])
    if 'description' in data:
        file.description = data['description']
    if 'is_public' in data:
        file.is_public = data['is_public']

    try:
        db.session.commit()
        return jsonify(file.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@files_bp.route('/files/<int:id>', methods=['DELETE'])
@require_admin_or_subadmin
def delete_file(id):
    file = File.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and file.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    file_path = file.get_file_path(current_app.config['UPLOAD_FOLDER'])

    try:
        # Delete file from disk
        if os.path.exists(file_path):
            os.remove(file_path)

        # Delete database record
        db.session.delete(file)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@files_bp.route('/files/shared', methods=['GET'])
@login_required
def list_shared_files():
    """List public files in user's subsite"""
    files = File.query.filter_by(
        subsite_id=current_user.subsite_id,
        is_public=True
    ).all()
    return jsonify([f.to_dict() for f in files])
