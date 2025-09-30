from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Site
from app.forms import LoginForm, RegistrationForm

site_bp = Blueprint('site', __name__, template_folder='templates')

# Page d'accueil
@site_bp.route('/')
def home():
    if current_user.is_authenticated:
        if current_user.role == 'super_admin':
            return redirect(url_for('super_admin.dashboard'))
        elif current_user.role == 'sub_admin':
            return redirect(url_for('sub_admin.dashboard'))
    return render_template('home.html')

# Connexion
@site_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.routes.user import user_bp
    return user_bp.login()

# Inscription
@site_bp.route('/register', methods=['GET', 'POST'])
def register():
    from app.routes.user import user_bp
    return user_bp.register()
