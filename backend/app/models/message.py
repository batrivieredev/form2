from backend.app import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    is_global = db.Column(db.Boolean, default=False)

    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    subsite_id = db.Column(db.Integer, db.ForeignKey('subsites.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('messages.id'))

    replies = db.relationship(
        'Message',
        backref=db.backref('parent', remote_side=[id]),
        lazy='dynamic'
    )

    def __init__(self, content, sender_id, subsite_id, subject=None, receiver_id=None,
                 is_global=False, parent_id=None):
        self.content = content
        self.sender_id = sender_id
        self.subsite_id = subsite_id
        self.subject = subject
        self.receiver_id = receiver_id
        self.is_global = is_global
        self.parent_id = parent_id

    def mark_as_read(self):
        self.is_read = True
        db.session.commit()

    def add_reply(self, content, sender_id):
        reply = Message(
            content=content,
            sender_id=sender_id,
            subsite_id=self.subsite_id,
            subject=f"Re: {self.subject}" if self.subject else None,
            receiver_id=self.sender_id if self.sender_id != sender_id else self.receiver_id,
            parent_id=self.id
        )
        db.session.add(reply)
        db.session.commit()
        return reply

    def get_thread(self):
        if self.parent_id:
            return self.parent.get_thread()
        return [self] + [msg for reply in self.replies for msg in reply.get_thread()]

    def to_dict(self):
        return {
            'id': self.id,
            'subject': self.subject,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read,
            'is_global': self.is_global,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'subsite_id': self.subsite_id,
            'parent_id': self.parent_id,
            'reply_count': self.replies.count()
        }
