from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import User, Dossier, File, Site
from app.forms import LoginForm, RegistrationForm, DossierForm

# Création du blueprint
user_bp = Blueprint('user', __name__, template_folder='templates')

# Dashboard / home
@user_bp.route('/', methods=['GET'])
@login_required
def home():
    # Redirection selon le rôle
    if current_user.role == 'super_admin':
        return redirect(url_for('super_admin.dashboard'))
    elif current_user.role == 'sub_admin':
        return redirect(url_for('sub_admin.dashboard'))
    else:
        return render_template('user/dashboard.html')

# Login
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # Redirection selon le rôle si déjà connecté
        if current_user.role == 'super_admin':
            return redirect(url_for('super_admin.dashboard'))
        elif current_user.role == 'sub_admin':
            return redirect(url_for('sub_admin.dashboard'))
        else:
            return redirect(url_for('user.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Connexion réussie !", "success")

            # Redirection selon le rôle
            if user.role == 'super_admin':
                return redirect(url_for('super_admin.dashboard'))
            elif user.role == 'sub_admin':
                return redirect(url_for('sub_admin.dashboard'))
            else:
                return redirect(url_for('user.home'))
        else:
            flash("Email ou mot de passe incorrect", "danger")

    return render_template('user/login.html', form=form)

# Registration
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        if current_user.role == 'super_admin':
            return redirect(url_for('super_admin.dashboard'))
        elif current_user.role == 'sub_admin':
            return redirect(url_for('sub_admin.dashboard'))
        else:
            return redirect(url_for('user.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Vérifie si l'email ou le username existe déjà
        if User.query.filter_by(email=form.email.data).first():
            flash("Email déjà utilisé.", "warning")
            return redirect(url_for('user.register'))
        if User.query.filter_by(username=form.username.data).first():
            flash("Nom d'utilisateur déjà utilisé.", "warning")
            return redirect(url_for('user.register'))

        # Création de l'utilisateur
        new_user = User(
            email=form.email.data,
            username=form.username.data,
            role='user'  # tous les nouveaux utilisateurs sont "user"
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
        return redirect(url_for('user.login'))

    return render_template('user/register.html', form=form)

# Logout
@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie !", "success")
    return redirect(url_for('user.login'))

# Soumettre un dossier avec questionnaire + upload
@user_bp.route('/submit_dossier', methods=['GET', 'POST'])
@login_required
def submit_dossier():
    form = DossierForm()

    # Remplir la liste des sites dans le formulaire
    form.site.choices = [(site.id, site.name) for site in Site.query.all()]

    if form.validate_on_submit():
        # Création d'un nouveau dossier
        nouveau_dossier = Dossier(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            job_type=form.job_type.data,
            site_id=form.site.data,
            status='déposé',
            user_id=current_user.id
        )
        db.session.add(nouveau_dossier)
        db.session.commit()

        # Upload des fichiers
        uploaded_files = request.files.getlist("files")
        upload_folder = os.path.join(current_app.root_path, 'static/uploads')
        os.makedirs(upload_folder, exist_ok=True)

        for file in uploaded_files:
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(upload_folder, filename))
                nouveau_dossier.files.append(File(filename=filename))
        db.session.commit()

        flash("Dossier soumis avec succès !", "success")

        # Redirection selon le rôle
        if current_user.role == 'super_admin':
            return redirect(url_for('super_admin.dashboard'))
        elif current_user.role == 'sub_admin':
            return redirect(url_for('sub_admin.dashboard'))
        else:
            return redirect(url_for('user.home'))

    return render_template('user/submit_dossier.html', form=form)
