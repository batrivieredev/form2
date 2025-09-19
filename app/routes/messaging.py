from flask import Blueprint, render_template

messaging_bp = Blueprint('messaging', __name__)

@messaging_bp.route('/', methods=['GET'])
def inbox():
    try:
        return render_template('messaging/inbox.html')
    except Exception:
        return "Inbox"
