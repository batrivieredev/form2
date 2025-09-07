import pytest
from backend.app import create_app, db
from backend.app.models import User, Subsite, Form, FormResponse, Message, Ticket, File
from datetime import datetime
import os

@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-key',
        'UPLOAD_FOLDER': 'tests/uploads'
    })

    # Create uploads directory if it doesn't exist
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

    return app

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()

@pytest.fixture
def _db(app):
    """Create and initialize test database"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()

@pytest.fixture
def admin_user(_db):
    """Create a test admin user"""
    user = User(
        email='admin@test.com',
        username='admin',
        role='admin'
    )
    user.set_password('password')
    _db.session.add(user)
    _db.session.commit()
    return user

@pytest.fixture
def test_subsite(_db):
    """Create a test subsite"""
    subsite = Subsite(
        name='Test Subsite',
        description='A test subsite',
        access_code='test123'
    )
    _db.session.add(subsite)
    _db.session.commit()
    return subsite

@pytest.fixture
def subadmin_user(_db, test_subsite):
    """Create a test subadmin user"""
    user = User(
        email='subadmin@test.com',
        username='subadmin',
        role='subadmin',
        subsite_id=test_subsite.id
    )
    user.set_password('password')
    _db.session.add(user)
    _db.session.commit()
    return user

@pytest.fixture
def regular_user(_db, test_subsite):
    """Create a test regular user"""
    user = User(
        email='user@test.com',
        username='user',
        role='user',
        subsite_id=test_subsite.id
    )
    user.set_password('password')
    _db.session.add(user)
    _db.session.commit()
    return user

@pytest.fixture
def test_form(_db, test_subsite, subadmin_user):
    """Create a test form"""
    form = Form(
        title='Test Form',
        description='A test form',
        structure={
            'fields': [
                {
                    'name': 'field1',
                    'type': 'text',
                    'label': 'Field 1',
                    'required': True
                }
            ]
        },
        creator_id=subadmin_user.id,
        subsite_id=test_subsite.id
    )
    _db.session.add(form)
    _db.session.commit()
    return form

@pytest.fixture
def test_ticket(_db, test_subsite, subadmin_user):
    """Create a test ticket"""
    ticket = Ticket(
        title='Test Ticket',
        description='A test ticket',
        creator_id=subadmin_user.id,
        subsite_id=test_subsite.id
    )
    _db.session.add(ticket)
    _db.session.commit()
    return ticket

@pytest.fixture
def test_message(_db, subadmin_user, regular_user, test_subsite):
    """Create a test message"""
    message = Message(
        subject='Test Message',
        content='Test content',
        sender_id=subadmin_user.id,
        receiver_id=regular_user.id,
        subsite_id=test_subsite.id
    )
    _db.session.add(message)
    _db.session.commit()
    return message

@pytest.fixture
def auth_headers(client, regular_user):
    """Get authentication headers for a user"""
    response = client.post('/api/auth/login', json={
        'email': regular_user.email,
        'password': 'password'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}
