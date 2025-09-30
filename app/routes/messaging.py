from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.models import User, Message
from datetime import datetime

# Blueprint pour la messagerie
messaging_bp = Blueprint('messaging', __name__, template_folder='messaging')


# Boîte de réception : messages reçus par l'utilisateur connecté
@messaging_bp.route('/', methods=['GET'])
@login_required
def inbox():
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.timestamp.desc()).all()
    return render_template('messaging/inbox.html', messages=messages)


# Voir un message : uniquement si l'utilisateur est expéditeur ou destinataire
@messaging_bp.route('/message/<int:msg_id>', methods=['GET'])
@login_required
def view_message(msg_id):
    msg = Message.query.get_or_404(msg_id)
    if msg.sender_id != current_user.id and msg.recipient_id != current_user.id:
        flash("Accès interdit", "danger")
        return redirect(url_for('messaging.inbox'))
    return render_template('messaging/message.html', message=msg)


# Composer un message
@messaging_bp.route('/compose', methods=['GET', 'POST'])
@login_required
def compose():
    # Récupère tous les utilisateurs sauf celui connecté
    users = User.query.filter(User.id != current_user.id).order_by(User.role.desc(), User.username).all()

    # Organiser les utilisateurs par rôle
    roles_dict = {'super_admin': [], 'sub_admin': [], 'user': []}
    for u in users:
        roles_dict[u.role].append(u)

    if request.method == 'POST':
        recipient_id = int(request.form['recipient_id'])
        recipient = User.query.get(recipient_id)
        if not recipient:
            flash("Destinataire introuvable", "danger")
            return redirect(url_for('messaging.compose'))

        new_message = Message(
            sender_id=current_user.id,
            recipient_id=recipient.id,
            subject=request.form['subject'],
            body=request.form['body'],
            timestamp=datetime.utcnow()
        )
        db.session.add(new_message)
        db.session.commit()
        flash("Message envoyé !", "success")
        return redirect(url_for('messaging.inbox'))

    return render_template('messaging/compose.html', roles_dict=roles_dict)

# Suppression d'un message
@messaging_bp.route('/message/<int:msg_id>/delete', methods=['POST'])
@login_required
def delete_message(msg_id):
    msg = Message.query.get_or_404(msg_id)

    # Vérifie que l'utilisateur est autorisé à supprimer (propriétaire ou super admin)
    if current_user.id != msg.recipient_id and current_user.role != 'super_admin':
        flash("Vous n'êtes pas autorisé à supprimer ce message.", "danger")
        return redirect(url_for('messaging.inbox'))

    db.session.delete(msg)
    db.session.commit()
    flash("Message supprimé avec succès.", "success")
    return redirect(url_for('messaging.inbox'))
