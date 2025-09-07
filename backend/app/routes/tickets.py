from backend.app import db
from datetime import datetime

class Ticket(db.Model):
    __tablename__ = 'tickets'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='open')
    priority = db.Column(db.String(50), default='normal')
    creator_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subsite_id = db.Column(db.Integer, db.ForeignKey('subsites.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relation avec les réponses
    responses = db.relationship('TicketResponse', backref='ticket', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'creator_id': self.creator_id,
            'subsite_id': self.subsite_id,
            'created_at': self.created_at.isoformat()
        }

    def add_response(self, content, user_id):
        response = TicketResponse(ticket_id=self.id, responder_id=user_id, content=content)
        db.session.add(response)
        db.session.commit()
        return response

class TicketResponse(db.Model):
    __tablename__ = 'ticket_responses'

    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    responder_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'ticket_id': self.ticket_id,
            'responder_id': self.responder_id,
            'content': self.content,
            'created_at': self.created_at.isoformat()
        }
