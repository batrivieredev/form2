import os
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app import db
from app.models import Site, User
from app.forms import SiteForm, UserForm

super_admin_bp = Blueprint('super_admin', __name__, template_folder='templates/super_admin')

# --- Décorateur Super Admin ---
def super_admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'super_admin':
            flash("Accès interdit : Super Admin uniquement.", "danger")
            return redirect(url_for('user.home'))
        return func(*args, **kwargs)
    return wrapper

# --- Dashboard ---
@super_admin_bp.route('/')
@login_required
@super_admin_required
def dashboard():
    sites = Site.query.all()
    users = User.query.all()
    return render_template('super_admin/dashboard.html', sites=sites, users=users)

# --- Création Site ---
@super_admin_bp.route('/site/create', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_site():
    form = SiteForm()
    sub_admins = User.query.filter_by(role='sub_admin').all()
    form.sub_admin_id.choices = [(0, 'Aucun')] + [(u.id, u.username) for u in sub_admins]

    if form.validate_on_submit():
        # Vérification slug unique
        if Site.query.filter_by(slug=form.slug.data).first():
            flash("Ce slug est déjà utilisé. Choisissez un autre.", "danger")
            return redirect(request.url)

        # Création en base de données
        site = Site(
            name=form.name.data,
            slug=form.slug.data,
            sub_admin_id=form.sub_admin_id.data if form.sub_admin_id.data != 0 else None
        )
        db.session.add(site)
        db.session.commit()

        # Création dossiers templates et static
        site_slug = form.slug.data
        template_folder = os.path.join(current_app.root_path, 'templates', 'sites', site_slug)
        static_folder = os.path.join(current_app.root_path, 'static', 'sites', site_slug)
        os.makedirs(template_folder, exist_ok=True)
        os.makedirs(static_folder, exist_ok=True)

        # Copier formulaire de base
        base_form_path = os.path.join(current_app.root_path, 'templates', 'user', 'register.html')
        new_form_path = os.path.join(template_folder, 'register.html')
        if os.path.exists(base_form_path):
            with open(base_form_path, 'r', encoding='utf-8') as f:
                content = f.read()
            with open(new_form_path, 'w', encoding='utf-8') as f:
                f.write(content)

        # Upload logo
        logo = request.files.get('logo')
        if logo and logo.filename != '':
            ext = logo.filename.rsplit('.', 1)[1].lower()
            if ext in {'png', 'jpg', 'jpeg', 'gif'}:
                logo_filename = secure_filename(logo.filename)
                logo.save(os.path.join(static_folder, logo_filename))

        flash(f"Site {site.name} créé avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))

    return render_template('super_admin/create_site.html', form=form, site=None)

# --- Editer Site ---
@super_admin_bp.route('/site/<int:site_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_site(site_id):
    site = Site.query.get_or_404(site_id)
    form = SiteForm(obj=site)
    sub_admins = User.query.filter_by(role='sub_admin').all()
    form.sub_admin_id.choices = [(0, 'Aucun')] + [(u.id, u.username) for u in sub_admins]

    if request.method == 'GET':
        form.sub_admin_id.data = site.sub_admin_id or 0

    if form.validate_on_submit():
        existing_site = Site.query.filter_by(slug=form.slug.data).first()
        if existing_site and existing_site.id != site.id:
            flash("Ce slug est déjà utilisé. Choisissez un autre.", "danger")
            return redirect(request.url)

        site.name = form.name.data
        site.slug = form.slug.data
        site.sub_admin_id = form.sub_admin_id.data if form.sub_admin_id.data != 0 else None
        db.session.commit()
        flash("Site modifié avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))

    return render_template('super_admin/create_site.html', form=form, site=site)

# --- Supprimer Site ---
@super_admin_bp.route('/site/<int:site_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    flash("Site supprimé !", "success")
    return redirect(url_for('super_admin.dashboard'))

# --- Afficher Site ---
@super_admin_bp.route('/sites/<slug>')
def view_site(slug):
    site = Site.query.filter_by(slug=slug).first_or_404()
    template_path = os.path.join('sites', slug, 'register.html')
    full_template_path = os.path.join(current_app.root_path, 'templates', template_path)
    if not os.path.exists(full_template_path):
        abort(404)

    # Chercher le logo si présent
    site_logo = None
    static_folder = os.path.join(current_app.root_path, 'static', 'sites', slug)
    if os.path.exists(static_folder):
        logos = [f for f in os.listdir(static_folder) if os.path.isfile(os.path.join(static_folder, f))]
        if logos:
            site_logo = url_for('static', filename=f'sites/{slug}/{logos[0]}')

    return render_template(template_path, site=site, site_logo=site_logo)

# --- Redirection automatique /slug vers /sites/<slug> ---
@super_admin_bp.route('/<slug>')
def redirect_to_site(slug):
    site = Site.query.filter_by(slug=slug).first()
    if site:
        return redirect(url_for('super_admin.view_site', slug=slug))
    abort(404)

# --- Gestion Utilisateurs ---
@super_admin_bp.route('/user/create', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_user():
    form = UserForm()
    sites = Site.query.all()
    form.site_id.choices = [(0, 'Aucun')] + [(s.id, s.name) for s in sites]

    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            site_id=form.site_id.data if form.site_id.data != 0 else None
        )
        if form.password.data:
            user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Utilisateur créé avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))

    return render_template('super_admin/create_user.html', form=form, user=None)

@super_admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    sites = Site.query.all()
    form.site_id.choices = [(0, 'Aucun')] + [(s.id, s.name) for s in sites]

    if request.method == 'GET':
        form.password.data = ''
        form.site_id.data = user.site_id or 0

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.site_id = form.site_id.data if form.site_id.data != 0 else None
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash("Utilisateur modifié avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))

    return render_template('super_admin/create_user.html', form=form, user=user)

@super_admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'super_admin':
        flash("Impossible de supprimer le super admin.", "danger")
        return redirect(url_for('super_admin.dashboard'))
    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé !", "success")
    return redirect(url_for('super_admin.dashboard'))
