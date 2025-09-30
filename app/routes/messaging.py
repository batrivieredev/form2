from flask import Blueprint, render_template, request, redirect, url_for, flash
from datetime import datetime

# Blueprint pour la messagerie, les templates sont dans templates/messaging
messaging_bp = Blueprint('messaging', __name__, template_folder='messaging')

# Fake storage pour tester
messages = [
    {
        "id": 1,
        "from": "alice@example.com",
        "subject": "Salut",
        "body": "Bonjour !",
        "date": datetime.now()   # Date ajoutée
    },
    {
        "id": 2,
        "from": "bob@example.com",
        "subject": "Réunion",
        "body": "Rappel réunion demain",
        "date": datetime.now()   # Date ajoutée
    }
]

# Boîte de réception
@messaging_bp.route('/', methods=['GET'])
def inbox():
    return render_template('messaging/inbox.html', messages=messages)

# Voir un message
@messaging_bp.route('/message/<int:msg_id>', methods=['GET'])
def view_message(msg_id):
    msg = next((m for m in messages if m["id"] == msg_id), None)
    if not msg:
        flash("Message introuvable", "danger")
        return redirect(url_for('messaging.inbox'))
    return render_template('messaging/message.html', message=msg)

# Composer un message
@messaging_bp.route('/compose', methods=['GET', 'POST'])
def compose():
    if request.method == 'POST':
        new_id = max((m["id"] for m in messages), default=0) + 1
        messages.append({
            "id": new_id,
            "from": request.form["from"],
            "subject": request.form["subject"],
            "body": request.form["body"],
            "date": datetime.now()   # Date ajoutée automatiquement
        })
        flash("Message envoyé !", "success")
        return redirect(url_for('messaging.inbox'))
    return render_template('messaging/compose.html')
