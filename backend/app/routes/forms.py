from flask import Blueprint, request, jsonify, send_file
from flask_login import login_required, current_user
from backend.app import db
from backend.app.models import Form, FormResponse, File, Subsite
from backend.app.routes.admin import require_admin_or_subadmin
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from weasyprint import HTML

forms_bp = Blueprint('forms', __name__)

@forms_bp.route('/forms', methods=['GET'])
@login_required
def list_forms():
    if current_user.is_admin():
        # Admin can see all forms or filter by subsite
        subsite_id = request.args.get('subsite_id', type=int)
        if subsite_id:
            forms = Form.query.filter_by(subsite_id=subsite_id).all()
        else:
            forms = Form.query.all()
    else:
        # Users and subadmins only see forms in their subsite
        forms = Form.query.filter_by(subsite_id=current_user.subsite_id).all()

    return jsonify([form.to_dict() for form in forms])

@forms_bp.route('/forms/<int:id>', methods=['GET'])
@login_required
def get_form(id):
    form = Form.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and form.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(form.to_dict())

@forms_bp.route('/forms', methods=['POST'])
@require_admin_or_subadmin
def create_form():
    data = request.get_json()

    # Validate required fields
    if not all(k in data for k in ['title', 'structure']):
        return jsonify({'error': 'Missing required fields'}), 400

    # Validate form structure
    try:
        if isinstance(data['structure'], str):
            structure = json.loads(data['structure'])
        else:
            structure = data['structure']
    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid form structure'}), 400

    # Create form
    form = Form(
        title=data['title'],
        description=data.get('description'),
        structure=structure,
        creator_id=current_user.id,
        subsite_id=current_user.subsite_id
    )

    try:
        db.session.add(form)
        db.session.commit()
        return jsonify(form.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms_bp.route('/forms/<int:id>', methods=['PUT'])
@require_admin_or_subadmin
def update_form(id):
    form = Form.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and form.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if 'title' in data:
        form.title = data['title']
    if 'description' in data:
        form.description = data['description']
    if 'structure' in data:
        try:
            if isinstance(data['structure'], str):
                structure = json.loads(data['structure'])
            else:
                structure = data['structure']
            form.structure = structure
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid form structure'}), 400
    if 'is_active' in data:
        form.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify(form.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms_bp.route('/forms/<int:id>/responses', methods=['GET'])
@require_admin_or_subadmin
def list_form_responses(id):
    form = Form.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and form.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    responses = FormResponse.query.filter_by(form_id=id).all()
    return jsonify([response.to_dict() for response in responses])

@forms_bp.route('/forms/<int:id>/responses', methods=['POST'])
@login_required
def submit_form_response(id):
    form = Form.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and form.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Validate answers against form structure
    if not validate_form_answers(form.structure, data.get('answers', {})):
        return jsonify({'error': 'Invalid form answers'}), 400

    # Create or update response
    response = FormResponse.query.filter_by(
        form_id=id,
        user_id=current_user.id
    ).first()

    if response:
        response.answers = data['answers']
        if data.get('submit', False):
            response.submit()
    else:
        response = FormResponse(
            form_id=id,
            user_id=current_user.id,
            answers=data['answers'],
            is_draft=not data.get('submit', False)
        )
        if data.get('submit', False):
            response.submitted_at = datetime.utcnow()

    try:
        if not response.id:
            db.session.add(response)
        db.session.commit()
        return jsonify(response.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@forms_bp.route('/forms/<int:id>/responses/<int:response_id>', methods=['GET'])
@login_required
def get_form_response(id, response_id):
    response = FormResponse.query.get_or_404(response_id)

    # Verify access rights
    if (not current_user.is_admin() and
        not current_user.is_subadmin() and
        response.user_id != current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(response.to_dict())

@forms_bp.route('/forms/<int:id>/responses/<int:response_id>/pdf', methods=['GET'])
@login_required
def export_response_pdf(id, response_id):
    response = FormResponse.query.get_or_404(response_id)
    form = Form.query.get_or_404(id)

    # Verify access rights
    if (not current_user.is_admin() and
        not current_user.is_subadmin() and
        response.user_id != current_user.id):
        return jsonify({'error': 'Unauthorized'}), 403

    # Generate PDF
    html_content = generate_response_html(form, response)
    pdf = HTML(string=html_content).write_pdf()

    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'form_{id}_response_{response_id}.pdf'
    )

def validate_form_answers(structure, answers):
    """Validate form answers against form structure"""
    required_fields = [
        field['name'] for field in structure.get('fields', [])
        if field.get('required', False)
    ]

    # Check required fields
    for field in required_fields:
        if field not in answers:
            return False

        # Additional validation based on field type could be added here

    return True

def generate_response_html(form, response):
    """Generate HTML for PDF export"""
    html = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ text-align: center; margin-bottom: 20px; }}
                .question {{ margin-bottom: 15px; }}
                .answer {{ margin-left: 20px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{form.title}</h1>
                <p>Submitted by: {response.user.username}</p>
                <p>Date: {response.submitted_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
    """

    # Add questions and answers
    for field in form.structure.get('fields', []):
        html += f"""
            <div class="question">
                <h3>{field.get('label', field['name'])}</h3>
                <div class="answer">
                    {format_answer(field, response.answers.get(field['name']))}
                </div>
            </div>
        """

    html += """
        </body>
    </html>
    """

    return html

def format_answer(field, answer):
    """Format answer based on field type"""
    if not answer:
        return "No answer"

    field_type = field.get('type', 'text')

    if field_type == 'checkbox':
        return "Yes" if answer else "No"
    elif field_type == 'select':
        if isinstance(answer, list):
            return ", ".join(answer)
        return str(answer)
    elif field_type == 'file':
        return f"File uploaded: {answer}"

    return str(answer)
