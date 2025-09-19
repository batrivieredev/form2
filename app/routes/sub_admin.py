from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Dossier, User, Site

sub_admin_bp = Blueprint('sub_admin', __name__)  # plus besoin de template_folder

def sub_admin_required(func):
    from functools import wraps
    from flask import abort
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'sub_admin':
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

@sub_admin_bp.route('/dashboard')
@login_required
@sub_admin_required
def dashboard():
    site = current_user.sites[0] if current_user.sites else None
    dossiers = site.dossiers if site else []
    return render_template('sub_admin/dashboard.html', dossiers=dossiers, site=site)

@sub_admin_bp.route('/update_dossier/<int:dossier_id>', methods=['GET', 'POST'])
@login_required
@sub_admin_required
def update_dossier(dossier_id):
    dossier = Dossier.query.get_or_404(dossier_id)
    if request.method == 'POST':
        statut = request.form.get('statut')
        if statut in ['déposé', 'en cours', 'validé']:
            dossier.statut = statut
            db.session.commit()
            flash('Statut mis à jour', 'success')
            return redirect(url_for('sub_admin.dashboard'))
    return render_template('sub_admin/update_dossier.html', dossier=dossier)

@sub_admin_bp.route('/manage_users')
@login_required
@sub_admin_required
def manage_users():
    site = current_user.sites[0] if current_user.sites else None
    users = site.users if site else []
    return render_template('sub_admin/manage_users.html', users=users)
