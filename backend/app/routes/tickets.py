from flask import Blueprint, request, jsonify
from backend.app import db
from backend.app.models.ticket import Ticket, TicketResponse

tickets_bp = Blueprint("tickets", __name__)

# Créer un ticket
@tickets_bp.route("/tickets", methods=["POST"])
def create_ticket():
    data = request.get_json()

    if not data or "title" not in data or "description" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    ticket = Ticket(
        title=data["title"],
        description=data["description"],
        status=data.get("status", "open"),
        priority=data.get("priority", "normal"),
        creator_id=data["creator_id"],
        subsite_id=data["subsite_id"],
    )
    db.session.add(ticket)
    db.session.commit()

    return jsonify(ticket.to_dict()), 201


# Récupérer tous les tickets
@tickets_bp.route("/tickets", methods=["GET"])
def get_tickets():
    tickets = Ticket.query.all()
    return jsonify([t.to_dict() for t in tickets])


# Récupérer un ticket par ID
@tickets_bp.route("/tickets/<int:ticket_id>", methods=["GET"])
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return jsonify(ticket.to_dict())


# Ajouter une réponse à un ticket
@tickets_bp.route("/tickets/<int:ticket_id>/responses", methods=["POST"])
def add_ticket_response(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    data = request.get_json()

    if not data or "content" not in data or "responder_id" not in data:
        return jsonify({"error": "Missing required fields"}), 400

    response = ticket.add_response(content=data["content"], user_id=data["responder_id"])
    return jsonify(response.to_dict()), 201


# Récupérer toutes les réponses d’un ticket
@tickets_bp.route("/tickets/<int:ticket_id>/responses", methods=["GET"])
def get_ticket_responses(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    responses = ticket.responses.all()
    return jsonify([r.to_dict() for r in responses])
