from backend.app import db
from datetime import datetime

class Ticket(db.Model):
    __tablename__ = 'tickets'
    __table_args__ = {'extend_existing': True}  # <-- permet de ne pas lever d'erreur si table déjà déclarée

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='open')  # open, in_progress, closed, reopened
    priority = db.Column(db.String(20), nullable=False, default='normal')  # low, normal, high, urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    closed_at = db.Column(db.DateTime)

    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    subsite_id = db.Column(db.Integer, db.ForeignKey('subsites.id'), nullable=False)

    responses = db.relationship(
        'TicketResponse',
        backref='ticket',
        lazy=True,
        cascade='all, delete-orphan',
        order_by='TicketResponse.created_at'
    )

    def __init__(self, title, description, creator_id, subsite_id, priority='normal'):
        self.title = title
        self.description = description
        self.creator_id = creator_id
        self.subsite_id = subsite_id
        self.priority = priority

    def assign_to(self, user_id):
        self.assigned_to = user_id
        self.status = 'in_progress'
        self.updated_at = datetime.utcnow()

    def close(self):
        self.status = 'closed'
        self.closed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def reopen(self):
        self.status = 'reopened'
        self.closed_at = None
        self.updated_at = datetime.utcnow()

    def add_response(self, content, user_id):
        from backend.app.models.ticket import TicketResponse  # import local pour éviter import circulaire
        response = TicketResponse(content=content, user_id=user_id, ticket_id=self.id)
        db.session.add(response)
        db.session.commit()
        return response

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'creator_id': self.creator_id,
            'assigned_to': self.assigned_to,
            'subsite_id': self.subsite_id,
            'response_count': len(self.responses)
        }


class TicketResponse(db.Model):
    __tablename__ = 'ticket_responses'
    __table_args__ = {'extend_existing': True}  # <-- idem, évite le conflit de table

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'ticket_id': self.ticket_id,
            'user_id': self.user_id
        }
