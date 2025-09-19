from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Site
from app.forms import SiteForm, UserForm
from functools import wraps

# Blueprint super-admin
super_admin_bp = Blueprint('super_admin', __name__, template_folder='templates/super_admin')

# Vérifie que l'utilisateur est super-admin
def super_admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'super_admin':
            flash("Accès interdit : Super Admin uniquement.", "danger")
            return redirect(url_for('user.home'))
        return func(*args, **kwargs)
    return wrapper

# ---------------- Dashboard ----------------
@super_admin_bp.route('/')
@login_required
@super_admin_required
def dashboard():
    sites = Site.query.all()
    users = User.query.all()
    return render_template('super_admin/dashboard.html', sites=sites, users=users)

# ---------------- Sites ----------------
@super_admin_bp.route('/site/create', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_site():
    form = SiteForm()
    # Ajouter le choix du sous-admin
    sub_admins = User.query.filter_by(role='sub_admin').all()
    form.sub_admin = UserForm().site  # juste pour injecter le champ dans le template
    form.sub_admin.choices = [(u.id, u.username) for u in sub_admins]

    if form.validate_on_submit():
        site = Site(
            name=form.name.data,
            sub_admin_id=request.form.get('sub_admin')  # récupérer l'ID du sous-admin
        )
        db.session.add(site)
        db.session.commit()
        flash("Site créé avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))
    return render_template('super_admin/create_site.html', form=form)

@super_admin_bp.route('/site/<int:site_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_site(site_id):
    site = Site.query.get_or_404(site_id)
    form = SiteForm(obj=site)

    # Ajouter le choix du sous-admin
    sub_admins = User.query.filter_by(role='sub_admin').all()
    form.sub_admin = UserForm().site
    form.sub_admin.choices = [(0, 'Aucun')] + [(u.id, u.username) for u in sub_admins]

    if request.method == 'GET':
        form.sub_admin.data = site.sub_admin_id or 0

    if form.validate_on_submit():
        site.name = form.name.data
        site.sub_admin_id = int(form.sub_admin.data) if form.sub_admin.data != 0 else None
        db.session.commit()
        flash("Site modifié avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))

    return render_template('super_admin/edit_site.html', form=form, site=site)

@super_admin_bp.route('/site/<int:site_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_site(site_id):
    site = Site.query.get_or_404(site_id)
    db.session.delete(site)
    db.session.commit()
    flash("Site supprimé avec succès !", "success")
    return redirect(url_for('super_admin.dashboard'))

@super_admin_bp.route('/site/<int:site_id>')
@login_required
@super_admin_required
def view_site(site_id):
    site = Site.query.get_or_404(site_id)
    return render_template('super_admin/view_site.html', site=site)

# ---------------- Utilisateurs ----------------
@super_admin_bp.route('/user/create', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_user():
    form = UserForm()
    form.site.choices = [(s.id, s.name) for s in Site.query.order_by(Site.name).all()]
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data,
            site_id=form.site.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Utilisateur créé avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))
    return render_template('super_admin/create_user.html', form=form)

@super_admin_bp.route('/user/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@super_admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    form.site.choices = [(s.id, s.name) for s in Site.query.order_by(Site.name).all()]

    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.role = form.role.data
        user.site_id = form.site.data
        db.session.commit()
        flash("Utilisateur modifié avec succès !", "success")
        return redirect(url_for('super_admin.dashboard'))
    return render_template('super_admin/edit_user.html', form=form, user=user)

@super_admin_bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@super_admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé avec succès !", "success")
    return redirect(url_for('super_admin.dashboard'))
