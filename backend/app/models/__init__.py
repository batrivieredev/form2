from backend.app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Import all models to make them available when importing the package
from backend.app.models.user import User
from backend.app.models.subsite import Subsite
from backend.app.models.form import Form, FormResponse
from backend.app.models.message import Message
from backend.app.models.ticket import Ticket, TicketResponse
from backend.app.models.file import File

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
