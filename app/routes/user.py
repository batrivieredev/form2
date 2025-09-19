from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, Dossier, Site, Fichier
from app.forms import LoginForm, RegistrationForm, DossierForm
from app.utils import save_file

# Blueprint sans template_folder pour utiliser le dossier templates par défaut
user_bp = Blueprint('user', __name__)

# Route Home
@user_bp.route('/', methods=['GET'])
def home():
    dossiers = current_user.dossiers if current_user.is_authenticated else []
    return render_template('user/dashboard.html', dossiers=dossiers)

# Route Inscription
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, role='user')
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Compte créé avec succès !', 'success')
        return redirect(url_for('user.login'))
    return render_template('user/register.html', form=form)

# Route Login
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Connecté avec succès', 'success')
            if user.role == 'super_admin':
                return redirect(url_for('super_admin.dashboard'))
            elif user.role == 'sub_admin':
                return redirect(url_for('sub_admin.dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Nom d’utilisateur ou mot de passe incorrect', 'danger')
    return render_template('user/login.html', form=form)

# Route Logout
@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Déconnecté', 'info')
    return redirect(url_for('user.login'))

# Dashboard utilisateur
@user_bp.route('/dashboard')
@login_required
def dashboard():
    dossiers = current_user.dossiers
    return render_template('user/dashboard.html', dossiers=dossiers)

# Soumission dossier
@user_bp.route('/submit_dossier', methods=['GET', 'POST'])
@login_required
def submit_dossier():
    form = DossierForm()
    if form.validate_on_submit():
        site = Site.query.first()
        dossier = Dossier(
            prenom=form.prenom.data,
            nom=form.nom.data,
            email=form.email.data,
            telephone=form.telephone.data,
            metier=form.metier.data,
            owner=current_user,
            site=site
        )
        db.session.add(dossier)
        db.session.commit()

        filename = save_file(form.fichier.data, dossier.id)
        if filename:
            fichier = Fichier(filename=filename, dossier=dossier)
            db.session.add(fichier)
            db.session.commit()

        flash('Dossier soumis avec succès', 'success')
        return redirect(url_for('user.dashboard'))
    return render_template('user/submit_dossier.html', form=form)
