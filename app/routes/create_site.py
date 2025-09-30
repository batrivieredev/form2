import os
from flask import Blueprint, request, redirect, url_for, flash, render_template, abort, current_app
from werkzeug.utils import secure_filename

superadmin_bp = Blueprint('superadmin', __name__, template_folder='templates/super_admin')

# Chemins
BASE_TEMPLATE = os.path.join(current_app.root_path if hasattr(current_app, 'root_path') else '', 'app', 'templates', 'user', 'register.html')
SITES_TEMPLATE_FOLDER = os.path.join('app', 'templates', 'sites')
SITES_STATIC_FOLDER = os.path.join('app', 'static', 'sites')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Création site ---
@superadmin_bp.route('/create_site', methods=['GET', 'POST'])
def create_site():
    if request.method == 'POST':
        site_name = request.form.get('site_name')
        logo = request.files.get('logo')

        if not site_name:
            flash("Nom du site obligatoire", "error")
            return redirect(request.url)

        # --- Créer dossier template ---
        site_template_dir = os.path.join(SITES_TEMPLATE_FOLDER, site_name)
        os.makedirs(site_template_dir, exist_ok=True)

        # --- Copier formulaire de base ---
        new_template_path = os.path.join(site_template_dir, 'register.html')
        with open(BASE_TEMPLATE, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(new_template_path, 'w', encoding='utf-8') as f:
            f.write(content)

        # --- Créer dossier static ---
        site_static_dir = os.path.join(SITES_STATIC_FOLDER, site_name)
        os.makedirs(site_static_dir, exist_ok=True)

        logo_filename = ''
        if logo and allowed_file(logo.filename):
            logo_filename = secure_filename(logo.filename)
            logo.save(os.path.join(site_static_dir, logo_filename))

        flash(f"Site {site_name} créé avec succès !", "success")
        return redirect(url_for('superadmin.view_site', site_name=site_name))

    return render_template('create_site.html')

# --- Afficher site dynamique ---
@superadmin_bp.route('/sites/<site_name>')
def view_site(site_name):
    # --- Vérification que le dossier existe ---
    template_path = os.path.join(current_app.root_path, SITES_TEMPLATE_FOLDER, site_name, 'register.html')
    if not os.path.exists(template_path):
        abort(404)

    # --- Charger le contenu du template ---
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    # --- Chercher logo ---
    logo_url = None
    static_dir = os.path.join(current_app.root_path, SITES_STATIC_FOLDER, site_name)
    if os.path.exists(static_dir):
        files = [f for f in os.listdir(static_dir) if os.path.isfile(os.path.join(static_dir, f))]
        if files:
            logo_url = f'/static/sites/{site_name}/{files[0]}'

    # --- Rendre le contenu avec render_template_string ---
    from flask import render_template_string
    return render_template_string(template_content, site_name=site_name, logo_url=logo_url)
