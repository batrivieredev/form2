from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Site, User

super_admin_bp = Blueprint('super_admin', __name__)  # plus besoin de template_folder

def super_admin_required(func):
    from functools import wraps
    from flask import abort
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'super_admin':
            abort(403)
        return func(*args, **kwargs)
    return decorated_view

@super_admin_bp.route('/dashboard')
@login_required
@super_admin_required
def dashboard():
    sites = Site.query.all()
    users = User.query.all()
    return render_template('super_admin/dashboard.html', sites=sites, users=users)

@super_admin_bp.route('/create_site', methods=['GET', 'POST'])
@login_required
@super_admin_required
def create_site():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        if name:
            site = Site(name=name, description=description)
            db.session.add(site)
            db.session.commit()
            flash('Site créé avec succès !', 'success')
            return redirect(url_for('super_admin.dashboard'))
        else:
            flash('Le nom du site est obligatoire', 'danger')
    return render_template('super_admin/create_site.html')
