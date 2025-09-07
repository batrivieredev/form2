import pytest
from backend.app.models import User, Subsite, Form, Message, Ticket
from datetime import datetime

def test_user_creation(regular_user):
    """Test user creation and basic attributes"""
    assert regular_user.email == 'user@test.com'
    assert regular_user.username == 'user'
    assert regular_user.role == 'user'
    assert regular_user.is_active is True
    assert regular_user.created_at is not None
    assert regular_user.last_login is None

def test_user_password(regular_user):
    """Test password hashing and verification"""
    assert regular_user.password_hash is not None
    assert regular_user.check_password('password') is True
    assert regular_user.check_password('wrong') is False

def test_user_roles(admin_user, subadmin_user, regular_user):
    """Test user role checks"""
    assert admin_user.is_admin() is True
    assert admin_user.is_subadmin() is False

    assert subadmin_user.is_admin() is False
    assert subadmin_user.is_subadmin() is True

    assert regular_user.is_admin() is False
    assert regular_user.is_subadmin() is False

def test_user_to_dict(regular_user):
    """Test user serialization"""
    user_dict = regular_user.to_dict()
    assert user_dict['email'] == regular_user.email
    assert user_dict['username'] == regular_user.username
    assert user_dict['role'] == regular_user.role
    assert 'password_hash' not in user_dict

def test_subsite_creation(test_subsite):
    """Test subsite creation and attributes"""
    assert test_subsite.name == 'Test Subsite'
    assert test_subsite.description == 'A test subsite'
    assert test_subsite.access_code == 'test123'
    assert test_subsite.is_active is True
    assert test_subsite.created_at is not None

def test_subsite_urls(test_subsite):
    """Test subsite URL generation"""
    assert test_subsite.get_admin_url() == f'/admin/{test_subsite.slug}'
    assert test_subsite.get_user_url() == f'/user/{test_subsite.slug}'

def test_form_creation(test_form):
    """Test form creation and attributes"""
    assert test_form.title == 'Test Form'
    assert test_form.description == 'A test form'
    assert test_form.is_active is True
    assert test_form.created_at is not None
    assert len(test_form.structure['fields']) == 1

def test_form_field_management(test_form):
    """Test form field management"""
    new_field = {
        'name': 'field2',
        'type': 'checkbox',
        'label': 'Field 2',
        'required': False
    }
    test_form.add_field(new_field)
    assert len(test_form.structure['fields']) == 2
    assert test_form.structure['fields'][1] == new_field

def test_message_creation(test_message):
    """Test message creation and attributes"""
    assert test_message.subject == 'Test Message'
    assert test_message.content == 'Test content'
    assert test_message.is_read is False
    assert test_message.is_global is False
    assert test_message.created_at is not None

def test_message_thread(test_message, regular_user, _db):
    """Test message threading"""
    # Create a reply
    reply = test_message.add_reply('Reply content', regular_user.id)
    _db.session.refresh(test_message)

    assert reply.parent_id == test_message.id
    assert reply.content == 'Reply content'
    assert reply.sender_id == regular_user.id

    # Get thread messages
    thread = test_message.get_thread()
    assert len(thread) == 2
    assert thread[0] == test_message
    assert thread[1] == reply

def test_ticket_creation(test_ticket):
    """Test ticket creation and attributes"""
    assert test_ticket.title == 'Test Ticket'
    assert test_ticket.description == 'A test ticket'
    assert test_ticket.status == 'open'
    assert test_ticket.priority == 'normal'
    assert test_ticket.created_at is not None
    assert test_ticket.closed_at is None

def test_ticket_status_changes(test_ticket, admin_user):
    """Test ticket status management"""
    # Close ticket
    test_ticket.close()
    assert test_ticket.status == 'closed'
    assert test_ticket.closed_at is not None

    # Reopen ticket
    test_ticket.reopen()
    assert test_ticket.status == 'reopened'
    assert test_ticket.closed_at is None

    # Assign ticket
    test_ticket.assign_to(admin_user.id)
    assert test_ticket.assigned_to == admin_user.id
    assert test_ticket.status == 'in_progress'

def test_ticket_responses(test_ticket, admin_user, _db):
    """Test ticket response management"""
    # Add a response
    response = test_ticket.add_response('Test response', admin_user.id)
    _db.session.refresh(test_ticket)

    assert len(test_ticket.responses) == 1
    assert response.content == 'Test response'
    assert response.user_id == admin_user.id
    assert response.ticket_id == test_ticket.id

def test_relationships(regular_user, test_subsite, test_form, test_message, test_ticket):
    """Test model relationships"""
    # User - Subsite relationship
    assert regular_user.subsite == test_subsite
    assert regular_user in test_subsite.users

    # Form relationships
    assert test_form.creator is not None
    assert test_form.subsite == test_subsite

    # Message relationships
    assert test_message.sender is not None
    assert test_message.receiver is not None
    assert test_message.subsite == test_subsite

    # Ticket relationships
    assert test_ticket.creator is not None
    assert test_ticket.subsite == test_subsite
