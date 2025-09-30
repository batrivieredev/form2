from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Site, User
from app.forms import SiteForm, UserForm
from functools import wraps

super_admin_bp = Blueprint('super_admin', __name__, template_folder='templates/super_admin')

# --- Décorateur super admin ---
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

# --- Sites ---
@super_admin_bp.route('/site/create', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_site():
    form = SiteForm()
    sub_admins = User.query.filter_by(role='sub_admin').all()
    form.sub_admin_id.choices = [(0, 'Aucun')] + [(u.id, u.username) for u in sub_admins]

    if form.validate_on_submit():
        site = Site(
            name=form.name.data,
            slug=form.slug.data,
            sub_admin_id=form.sub_admin_id.data if form.sub_admin_id.data != 0 else None
        )
        db.session.add(site)
        db.session.commit()
        flash("Site créé avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))

    return render_template('super_admin/create_site.html', form=form, site=None)

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
        site.name = form.name.data
        site.slug = form.slug.data
        site.sub_admin_id = form.sub_admin_id.data if form.sub_admin_id.data != 0 else None
        db.session.commit()
        flash("Site modifié avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))

    return render_template('super_admin/create_site.html', form=form, site=site)

@super_admin_bp.route('/site/<int:site_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    flash("Site supprimé !", "success")
    return redirect(url_for('super_admin.dashboard'))

# --- Utilisateurs ---
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
