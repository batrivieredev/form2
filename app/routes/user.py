from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import os
from app import db
from app.models import User, Dossier, File, Site
from app.forms import LoginForm, RegistrationForm, DossierForm

user_bp = Blueprint('user', __name__, template_folder='templates')

# Dashboard / home
@user_bp.route('/', methods=['GET'])
@login_required
def home():
    if current_user.role == 'super_admin':
        return redirect(url_for('super_admin.dashboard'))
    elif current_user.role == 'sub_admin':
        return redirect(url_for('sub_admin.dashboard'))
    else:
        return render_template('user/dashboard.html')

# Login global
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
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
            if user.role == 'super_admin':
                return redirect(url_for('super_admin.dashboard'))
            elif user.role == 'sub_admin':
                return redirect(url_for('sub_admin.dashboard'))
            else:
                return redirect(url_for('user.home'))
        else:
            flash("Email ou mot de passe incorrect", "danger")
    return render_template('user/login.html', form=form)

# Registration global
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('user.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email déjà utilisé.", "warning")
            return redirect(url_for('user.register'))
        if User.query.filter_by(username=form.username.data).first():
            flash("Nom d'utilisateur déjà utilisé.", "warning")
            return redirect(url_for('user.register'))

        new_user = User(
            email=form.email.data,
            username=form.username.data,
            role='user'
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash("Inscription réussie !", "success")
        return redirect(url_for('user.login'))
    return render_template('user/register.html', form=form)

# Logout
@user_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Déconnexion réussie !", "success")
    return redirect(url_for('user.login'))

# Login spécifique site
@user_bp.route('/<slug>/login', methods=['GET', 'POST'])
def site_login(slug):
    site = Site.query.filter_by(slug=slug).first_or_404()
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data, site_id=site.id).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash("Connexion réussie !", "success")
            return redirect(url_for('user.home'))
        flash("Email ou mot de passe incorrect", "danger")
    return render_template('user/login.html', form=form, site=site)

# Registration spécifique site
@user_bp.route('/<slug>/register', methods=['GET', 'POST'])
def site_register(slug):
    site = Site.query.filter_by(slug=slug).first_or_404()
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data, site_id=site.id).first():
            flash("Email déjà utilisé.", "warning")
            return redirect(url_for('user.site_register', slug=slug))
        user = User(
            email=form.email.data,
            username=form.username.data,
            role='user',
            site_id=site.id
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Inscription réussie !", "success")
        return redirect(url_for('user.site_login', slug=slug))
    return render_template('user/register.html', form=form, site=site)

@user_bp.route('/dossier/submit', methods=['GET', 'POST'])
@login_required
def submit_dossier():
    form = DossierForm()
    if form.validate_on_submit():
        # Créer le dossier
        new_dossier = Dossier(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            job_type=form.job_type.data,
            site_id=form.site.data.id,  # selon comment ton SelectField renvoie le site
            user_id=current_user.id
        )
        db.session.add(new_dossier)
        db.session.commit()

        # Gérer les fichiers uploadés
        files = request.files.getlist(form.files.name)
        upload_folder = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        for f in files:
            if f.filename:
                filename = secure_filename(f.filename)
                filepath = os.path.join(upload_folder, filename)
                f.save(filepath)
                # Ajouter en base
                file_record = File(
                    filename=filename,
                    path=filepath,
                    dossier_id=new_dossier.id
                )
                db.session.add(file_record)

        db.session.commit()
        flash("Dossier soumis avec succès !", "success")
        return redirect(url_for('user.home'))

    return render_template('user/submit_dossier.html', form=form)
