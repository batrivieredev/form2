from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app import db
from backend.app.models import User, Subsite
from werkzeug.security import generate_password_hash
import secrets
import string

admin_bp = Blueprint('admin', __name__)

def require_admin(f):
    """Decorator to require admin role"""
    def wrapper(*args, **kwargs):
        if not current_user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return login_required(wrapper)

def require_admin_or_subadmin(f):
    """Decorator to require admin or subadmin role"""
    def wrapper(*args, **kwargs):
        if not (current_user.is_admin() or current_user.is_subadmin()):
            return jsonify({'error': 'Admin or Subadmin access required'}), 403
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return login_required(wrapper)

def generate_access_code(length=12):
    """Generate a secure random access code"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

@admin_bp.route('/subsites', methods=['GET'])
@require_admin_or_subadmin
def list_subsites():
    if current_user.is_admin():
        subsites = Subsite.query.all()
    else:
        subsites = [current_user.subsite]
    return jsonify([s.to_dict() for s in subsites])

@admin_bp.route('/subsites', methods=['POST'])
@require_admin
def create_subsite():
    data = request.get_json()

    if not data.get('name'):
        return jsonify({'error': 'Name is required'}), 400

    # Generate access code if not provided
    access_code = data.get('access_code', generate_access_code())

    subsite = Subsite(
        name=data['name'],
        description=data.get('description'),
        access_code=access_code
    )

    try:
        db.session.add(subsite)
        db.session.commit()
        return jsonify(subsite.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subsites/<int:id>', methods=['PUT'])
@require_admin
def update_subsite(id):
    subsite = Subsite.query.get_or_404(id)
    data = request.get_json()

    if 'name' in data:
        subsite.name = data['name']
    if 'description' in data:
        subsite.description = data['description']
    if 'access_code' in data:
        subsite.access_code = data['access_code']
    if 'is_active' in data:
        subsite.is_active = data['is_active']

    try:
        db.session.commit()
        return jsonify(subsite.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subsites/<int:id>', methods=['DELETE'])
@require_admin
def delete_subsite(id):
    subsite = Subsite.query.get_or_404(id)

    try:
        db.session.delete(subsite)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/subsites/<int:id>/admins', methods=['POST'])
@require_admin
def add_subsite_admin(id):
    subsite = Subsite.query.get_or_404(id)
    data = request.get_json()

    # Create new subadmin
    if data.get('email') and data.get('username'):
        user = User(
            email=data['email'],
            username=data['username'],
            role='subadmin',
            subsite_id=subsite.id
        )
        user.set_password(data.get('password', generate_access_code()))

        try:
            db.session.add(user)
            db.session.commit()
            return jsonify(user.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    # Promote existing user to subadmin
    elif data.get('user_id'):
        user = User.query.get_or_404(data['user_id'])
        user.role = 'subadmin'
        user.subsite_id = subsite.id

        try:
            db.session.commit()
            return jsonify(user.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid request data'}), 400

@admin_bp.route('/subsites/<int:id>/admins/<int:user_id>', methods=['DELETE'])
@require_admin
def remove_subsite_admin(id, user_id):
    subsite = Subsite.query.get_or_404(id)
    user = User.query.get_or_404(user_id)

    if user.subsite_id != subsite.id or user.role != 'subadmin':
        return jsonify({'error': 'User is not an admin of this subsite'}), 400

    # Demote to regular user
    user.role = 'user'

    try:
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
