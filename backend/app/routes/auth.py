from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from backend.app import db
from backend.app.models import User, Subsite
from datetime import datetime
import jwt

auth_bp = Blueprint('auth', __name__)

# --- ROUTE ACCUEIL ---
@auth_bp.route('/')
def home():
    return jsonify({'message': 'Bienvenue sur DJ Pro Studio !'}), 200

# --- ROUTE REGISTER ---
@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    required_fields = ['email', 'username', 'password', 'subsite_slug']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already registered'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already taken'}), 400

    subsite = Subsite.query.filter_by(slug=data['subsite_slug']).first()
    if not subsite:
        return jsonify({'error': 'Invalid subsite'}), 400

    user = User(
        email=data['email'],
        username=data['username'],
        role='user',
        subsite_id=subsite.id
    )
    user.set_password(data['password'])

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# --- ROUTE LOGIN ---
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing email or password'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if user and user.check_password(data['password']):
        user.last_login = datetime.utcnow()
        db.session.commit()
        login_user(user)

        token = jwt.encode(
            {'user_id': user.id},
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'token': token, 'user': user.to_dict()})

    return jsonify({'error': 'Invalid email or password'}), 401

# --- ROUTE LOGOUT ---
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Successfully logged out'})

# --- ROUTE ME ---
@auth_bp.route('/me')
@login_required
def me():
    return jsonify(current_user.to_dict())

# --- ROUTE CHANGE PASSWORD ---
@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    data = request.get_json()
    if not data.get('old_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing old or new password'}), 400

    if not current_user.check_password(data['old_password']):
        return jsonify({'error': 'Invalid current password'}), 401

    current_user.set_password(data['new_password'])
    db.session.commit()
    return jsonify({'message': 'Password updated successfully'})

# --- ROUTE RESET PASSWORD ---
@auth_bp.route('/reset-password', methods=['POST'])
@login_required
def reset_password():
    data = request.get_json()
    if not current_user.is_admin() and not current_user.is_subadmin():
        return jsonify({'error': 'Unauthorized'}), 403

    user = User.query.get(data.get('user_id'))
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if current_user.is_subadmin() and user.subsite_id != current_user.subsite_id:
        return jsonify({'error': 'Unauthorized'}), 403

    new_password = data.get('new_password', 'changeme123')
    user.set_password(new_password)
    db.session.commit()

    return jsonify({'message': 'Password reset successfully', 'new_password': new_password})
