from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app import db
from backend.app.models import User, Subsite
from backend.app.routes.admin import require_admin_or_subadmin
from werkzeug.security import generate_password_hash

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
@require_admin_or_subadmin
def list_users():
    if current_user.is_admin():
        # Admin can see all users or filter by subsite
        subsite_id = request.args.get('subsite_id', type=int)
        if subsite_id:
            users = User.query.filter_by(subsite_id=subsite_id).all()
        else:
            users = User.query.all()
    else:
        # Subadmin can only see users in their subsite
        users = User.query.filter_by(subsite_id=current_user.subsite_id).all()

    return jsonify([user.to_dict() for user in users])

@user_bp.route('/users/<int:id>', methods=['GET'])
@require_admin_or_subadmin
def get_user(id):
    user = User.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and user.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(user.to_dict())

@user_bp.route('/users', methods=['POST'])
@require_admin_or_subadmin
def create_user():
    data = request.get_json()

    # Validate required fields
    required_fields = ['email', 'username', 'password']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if user already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400

    # Determine subsite_id
    if current_user.is_admin():
        subsite_id = data.get('subsite_id')
        if not subsite_id:
            return jsonify({'error': 'Subsite ID required'}), 400
    else:
        subsite_id = current_user.subsite_id

    # Create new user
    user = User(
        email=data['email'],
        username=data['username'],
        role='user',  # Only admins and subadmins can create regular users
        subsite_id=subsite_id
    )
    user.set_password(data['password'])

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify(user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:id>', methods=['PUT'])
@require_admin_or_subadmin
def update_user(id):
    user = User.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and user.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    # Only admin can change subsite
    if 'subsite_id' in data and not current_user.is_admin():
        return jsonify({'error': 'Unauthorized to change subsite'}), 403

    # Update fields
    if 'email' in data:
        user.email = data['email']
    if 'username' in data:
        user.username = data['username']
    if 'is_active' in data:
        user.is_active = data['is_active']
    if 'subsite_id' in data and current_user.is_admin():
        user.subsite_id = data['subsite_id']

    try:
        db.session.commit()
        return jsonify(user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/users/<int:id>', methods=['DELETE'])
@require_admin_or_subadmin
def delete_user(id):
    user = User.query.get_or_404(id)

    # Verify access rights
    if not current_user.is_admin() and user.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    # Cannot delete admins unless you're the super admin
    if user.is_admin() or (user.is_subadmin() and not current_user.is_admin()):
        return jsonify({'error': 'Cannot delete admin users'}), 403

    try:
        db.session.delete(user)
        db.session.commit()
        return '', 204
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user's profile"""
    return jsonify(current_user.to_dict())

@user_bp.route('/profile', methods=['PUT'])
@login_required
def update_profile():
    """Update current user's profile"""
    data = request.get_json()

    # Users can only update certain fields
    if 'email' in data:
        current_user.email = data['email']
    if 'username' in data:
        current_user.username = data['username']

    try:
        db.session.commit()
        return jsonify(current_user.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
