from flask import Blueprint
from backend.app.routes.auth import auth_bp
from backend.app.routes.admin import admin_bp
from backend.app.routes.user import user_bp
from backend.app.routes.forms import forms_bp
from backend.app.routes.files import files_bp
from backend.app.routes.messages import messages_bp
from backend.app.routes.tickets import tickets_bp

# Create main API blueprint
api_bp = Blueprint('api', __name__)

# Register all sub-blueprints
api_bp.register_blueprint(auth_bp, url_prefix='/auth')
api_bp.register_blueprint(admin_bp, url_prefix='/admin')
api_bp.register_blueprint(user_bp, url_prefix='/users')
api_bp.register_blueprint(forms_bp, url_prefix='/forms')
api_bp.register_blueprint(files_bp, url_prefix='/files')
api_bp.register_blueprint(messages_bp, url_prefix='/messages')
api_bp.register_blueprint(tickets_bp, url_prefix='/tickets')

# API health check endpoint
@api_bp.route('/health', methods=['GET'])
def health_check():
    return {'status': 'ok'}

# API version endpoint
@api_bp.route('/version', methods=['GET'])
def version():
    return {
        'version': '1.0.0',
        'name': 'Form Management API',
        'description': 'API for multi-site form management system'
    }
