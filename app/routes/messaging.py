from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import User, Message
from app.forms import MessageForm

messaging_bp = Blueprint('messaging', __name__)  # plus besoin de template_folder

@login_required
@messaging_bp.route('/', methods=['GET','POST'])
def inbox():
    form = MessageForm()
    messages = current_user.messages_received.order_by(Message.timestamp.desc()).all()
    if form.validate_on_submit():
        recipient_id = request.form.get('recipient_id')
        recipient = User.query.get(recipient_id)
        if recipient:
            msg = Message(sender_id=current_user.id, recipient_id=recipient.id, body=form.body.data)
            db.session.add(msg)
            db.session.commit()
            flash('Message envoyé', 'success')
            return redirect(url_for('messaging.inbox'))
        else:
            flash('Destinataire introuvable', 'danger')

    # Liste des destinataires possibles
    if current_user.role == 'super_admin':
        recipients = User.query.all()
    elif current_user.role == 'sub_admin':
        site = current_user.sites[0] if current_user.sites else None
        recipients = site.users if site else []
    else:
        recipients = current_user.sites[0].users if current_user.sites else []
        recipients = [u for u in recipients if u.role == 'sub_admin']

    return render_template('messaging/inbox.html', messages=messages, form=form, recipients=recipients)
