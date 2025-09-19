from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Site, Dossier

admin_bp = Blueprint('admin', __name__, template_folder='templates')

# --------------------------
# Dashboard Super Admin
# --------------------------
@admin_bp.route('/super', methods=['GET'])
@login_required
def super_dashboard():
    if current_user.role != 'super_admin':
        flash("Accès refusé.", "danger")
        return redirect(url_for('user.home'))

    sites = Site.query.all()
    users = User.query.all()
    return render_template('admin/super_dashboard.html', sites=sites, users=users)

# --------------------------
# Dashboard Sub Admin
# --------------------------
@admin_bp.route('/sub', methods=['GET'])
@login_required
def sub_dashboard():
    if current_user.role != 'sub_admin':
        flash("Accès refusé.", "danger")
        return redirect(url_for('user.home'))

    # Le sous-admin ne voit que les dossiers de son site
    site = current_user.site
    dossiers = Dossier.query.filter_by(site_id=site.id).all()
    return render_template('admin/sub_dashboard.html', site=site, dossiers=dossiers)

# --------------------------
# CRUD Sites (Super Admin)
# --------------------------
@admin_bp.route('/super/site/add', methods=['GET', 'POST'])
@login_required
def add_site():
    if current_user.role != 'super_admin':
        flash("Accès refusé.", "danger")
        return redirect(url_for('user.home'))

    if request.method == 'POST':
        name = request.form.get('name')
        slug = request.form.get('slug')
        if not name or not slug:
            flash("Nom et URL obligatoires", "warning")
            return redirect(url_for('admin.add_site'))
        if Site.query.filter_by(url_slug=slug).first():
            flash("Ce slug est déjà utilisé", "warning")
            return redirect(url_for('admin.add_site'))

        new_site = Site(name=name, url_slug=slug)
        db.session.add(new_site)
        db.session.commit()
        flash("Site créé avec succès", "success")
        return redirect(url_for('admin.super_dashboard'))

    return render_template('admin/add_site.html')

# --------------------------
# CRUD Utilisateurs (Super Admin)
# --------------------------
@admin_bp.route('/super/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'super_admin':
        flash("Accès refusé.", "danger")
        return redirect(url_for('user.home'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Utilisateur supprimé", "success")
    return redirect(url_for('admin.super_dashboard'))

# --------------------------
# CRUD Dossiers (Sub Admin)
# --------------------------
@admin_bp.route('/sub/dossier/<int:dossier_id>/update_status', methods=['POST'])
@login_required
def update_dossier_status(dossier_id):
    if current_user.role != 'sub_admin':
        flash("Accès refusé.", "danger")
        return redirect(url_for('user.home'))

    dossier = Dossier.query.get_or_404(dossier_id)
    if dossier.site_id != current_user.site_id:
        flash("Accès refusé.", "danger")
        return redirect(url_for('admin.sub_dashboard'))

    new_status = request.form.get('status')
    if new_status not in ['déposé', 'en cours', 'validé']:
        flash("Statut invalide", "warning")
    else:
        dossier.status = new_status
        db.session.commit()
        flash("Statut mis à jour", "success")

    return redirect(url_for('admin.sub_dashboard'))
