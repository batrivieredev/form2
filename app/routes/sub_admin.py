from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import User, Dossier, Site

sub_admin_bp = Blueprint('sub_admin', __name__)

def sub_admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.role != 'sub_admin':
            abort(403)
        return func(*args, **kwargs)
    return wrapper

@sub_admin_bp.route('/', methods=['GET'])
@login_required
@sub_admin_required
def dashboard():
    site = Site.query.get(current_user.site_id)
    if not site:
        flash("Aucun site assigné à votre compte. Contactez le super-admin.", "warning")
        return redirect(url_for('user.home'))
    dossiers = Dossier.query.filter_by(site_id=site.id).all()
    return render_template('sub_admin/dashboard.html', site=site, dossiers=dossiers)

@sub_admin_bp.route('/dossier/<int:dossier_id>', methods=['GET'])
@login_required
@sub_admin_required
def view_dossier(dossier_id):
    dossier = Dossier.query.get_or_404(dossier_id)
    if dossier.site_id != current_user.site_id:
        abort(403)
    return render_template('sub_admin/view_dossier.html', dossier=dossier)

@sub_admin_bp.route('/dossier/<int:dossier_id>/status', methods=['POST'])
@login_required
@sub_admin_required
def update_status(dossier_id):
    dossier = Dossier.query.get_or_404(dossier_id)
    if dossier.site_id != current_user.site_id:
        abort(403)
    new_status = request.form.get('status')
    if new_status in ['déposé', 'en cours de décision', 'validé']:
        dossier.status = new_status
        db.session.commit()
        flash("Statut du dossier mis à jour.", "success")
    return redirect(url_for('sub_admin.dashboard'))

@sub_admin_bp.route('/search', methods=['GET'])
@login_required
@sub_admin_required
def search():
    query = request.args.get('q', '')
    site_id = current_user.site_id
    dossiers = Dossier.query.filter(
        Dossier.site_id == site_id,
        (Dossier.title.ilike(f'%{query}%')) |
        (Dossier.content.ilike(f'%{query}%'))
    ).all()
    site = Site.query.get(site_id)
    return render_template('sub_admin/dashboard.html', site=site, dossiers=dossiers)

@sub_admin_bp.route('/user/<int:user_id>/reset_password', methods=['POST'])
@login_required
@sub_admin_required
def reset_user_password(user_id):
    user = User.query.get_or_404(user_id)
    if user.site_id != current_user.site_id or user.role != 'user':
        abort(403)
    new_password = request.form.get('password')
    if new_password:
        user.set_password(new_password)
        db.session.commit()
        flash("Mot de passe réinitialisé.", "success")
    return redirect(url_for('sub_admin.dashboard'))

@sub_admin_bp.route('/dossier/<int:dossier_id>/delete', methods=['POST'])
@login_required
@sub_admin_required
def delete_dossier(dossier_id):
    dossier = Dossier.query.get_or_404(dossier_id)
    if dossier.site_id != current_user.site_id:
        abort(403)
    db.session.delete(dossier)
    db.session.commit()
    flash("Dossier supprimé.", "success")
    return redirect(url_for('sub_admin.dashboard'))
