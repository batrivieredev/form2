from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from backend.app import db
from backend.app.models import Message, User
from backend.app.routes.admin import require_admin_or_subadmin
from datetime import datetime

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/messages', methods=['GET'])
@login_required
def list_messages():
    """List messages for current user"""
    # Get query parameters
    is_global = request.args.get('is_global', type=bool, default=None)
    only_unread = request.args.get('unread', type=bool, default=False)

    # Base query
    query = Message.query.filter(
        (Message.receiver_id == current_user.id) |  # Personal messages
        ((Message.is_global == True) & (Message.subsite_id == current_user.subsite_id))  # Global messages
    )

    # Apply filters
    if is_global is not None:
        query = query.filter(Message.is_global == is_global)
    if only_unread:
        query = query.filter(Message.is_read == False)

    # Order by creation date, newest first
    messages = query.order_by(Message.created_at.desc()).all()

    return jsonify([msg.to_dict() for msg in messages])

@messages_bp.route('/messages/sent', methods=['GET'])
@login_required
def list_sent_messages():
    """List messages sent by current user"""
    messages = Message.query.filter_by(sender_id=current_user.id)\
        .order_by(Message.created_at.desc()).all()
    return jsonify([msg.to_dict() for msg in messages])

@messages_bp.route('/messages', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()

    if not data.get('content'):
        return jsonify({'error': 'Message content is required'}), 400

    # Handle global messages (only admins and subadmins can send them)
    if data.get('is_global', False):
        if not (current_user.is_admin() or current_user.is_subadmin()):
            return jsonify({'error': 'Unauthorized to send global messages'}), 403

        message = Message(
            content=data['content'],
            subject=data.get('subject'),
            sender_id=current_user.id,
            subsite_id=current_user.subsite_id,
            is_global=True
        )

    # Handle personal messages
    else:
        if not data.get('receiver_id'):
            return jsonify({'error': 'Receiver ID is required'}), 400

        receiver = User.query.get_or_404(data['receiver_id'])

        # Verify users are in the same subsite
        if receiver.subsite_id != current_user.subsite_id:
            return jsonify({'error': 'Cannot send message to user in different subsite'}), 403

        message = Message(
            content=data['content'],
            subject=data.get('subject'),
            sender_id=current_user.id,
            receiver_id=receiver.id,
            subsite_id=current_user.subsite_id,
            parent_id=data.get('parent_id')  # For message threads
        )

    try:
        db.session.add(message)
        db.session.commit()
        return jsonify(message.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@messages_bp.route('/messages/<int:id>', methods=['GET'])
@login_required
def get_message(id):
    message = Message.query.get_or_404(id)

    # Verify access rights
    if not can_access_message(message):
        return jsonify({'error': 'Unauthorized'}), 403

    # Mark as read if recipient is accessing
    if message.receiver_id == current_user.id and not message.is_read:
        message.mark_as_read()

    return jsonify(message.to_dict())

@messages_bp.route('/messages/<int:id>/thread', methods=['GET'])
@login_required
def get_message_thread(id):
    message = Message.query.get_or_404(id)

    # Verify access rights
    if not can_access_message(message):
        return jsonify({'error': 'Unauthorized'}), 403

    # Get all messages in thread
    thread = message.get_thread()

    # Mark unread messages as read if recipient is accessing
    for msg in thread:
        if msg.receiver_id == current_user.id and not msg.is_read:
            msg.mark_as_read()

    return jsonify([msg.to_dict() for msg in thread])

@messages_bp.route('/messages/<int:id>/reply', methods=['POST'])
@login_required
def reply_to_message(id):
    parent = Message.query.get_or_404(id)

    # Verify access rights
    if not can_access_message(parent):
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()

    if not data.get('content'):
        return jsonify({'error': 'Message content is required'}), 400

    try:
        reply = parent.add_reply(data['content'], current_user.id)
        return jsonify(reply.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def can_access_message(message):
    """Check if current user can access a message"""
    # Users can access messages they sent or received
    if message.sender_id == current_user.id or message.receiver_id == current_user.id:
        return True

    # Users can access global messages in their subsite
    if message.is_global and message.subsite_id == current_user.subsite_id:
        return True

    # Admins can access all messages
    if current_user.is_admin():
        return True

    # Subadmins can access all messages in their subsite
    if current_user.is_subadmin() and message.subsite_id == current_user.subsite_id:
        return True

    return False
