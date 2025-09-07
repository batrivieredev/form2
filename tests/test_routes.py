import pytest
from backend.app.models import User, Subsite
import json
import os

def test_register(client, test_subsite):
    """Test user registration"""
    response = client.post('/api/auth/register', json={
        'email': 'newuser@test.com',
        'username': 'newuser',
        'password': 'password123',
        'subsite_slug': test_subsite.slug
    })
    assert response.status_code == 201
    data = response.json
    assert data['user']['email'] == 'newuser@test.com'
    assert data['message'] == 'User registered successfully'

def test_login(client, regular_user):
    """Test user login"""
    # Test successful login
    response = client.post('/api/auth/login', json={
        'email': regular_user.email,
        'password': 'password'
    })
    assert response.status_code == 200
    data = response.json
    assert 'token' in data
    assert data['user']['email'] == regular_user.email

    # Test invalid credentials
    response = client.post('/api/auth/login', json={
        'email': regular_user.email,
        'password': 'wrongpassword'
    })
    assert response.status_code == 401

def test_me(client, regular_user, auth_headers):
    """Test getting current user info"""
    response = client.get('/api/auth/me', headers=auth_headers)
    assert response.status_code == 200
    data = response.json
    assert data['email'] == regular_user.email

def test_change_password(client, regular_user, auth_headers):
    """Test password change"""
    response = client.post('/api/auth/change-password',
        headers=auth_headers,
        json={
            'old_password': 'password',
            'new_password': 'newpassword123'
        }
    )
    assert response.status_code == 200

    # Verify new password works
    response = client.post('/api/auth/login', json={
        'email': regular_user.email,
        'password': 'newpassword123'
    })
    assert response.status_code == 200

def test_subsite_management(client, admin_user):
    """Test subsite CRUD operations"""
    # Login as admin
    response = client.post('/api/auth/login', json={
        'email': admin_user.email,
        'password': 'password'
    })
    token = response.json['token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create subsite
    response = client.post('/api/admin/subsites',
        headers=headers,
        json={
            'name': 'New Subsite',
            'description': 'Test description',
            'access_code': 'access123'
        }
    )
    assert response.status_code == 201
    subsite_id = response.json['id']

    # Get subsite
    response = client.get(f'/api/admin/subsites/{subsite_id}', headers=headers)
    assert response.status_code == 200
    assert response.json['name'] == 'New Subsite'

    # Update subsite
    response = client.put(f'/api/admin/subsites/{subsite_id}',
        headers=headers,
        json={
            'name': 'Updated Subsite'
        }
    )
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Subsite'

    # Delete subsite
    response = client.delete(f'/api/admin/subsites/{subsite_id}', headers=headers)
    assert response.status_code == 204

def test_user_management(client, admin_user, test_subsite):
    """Test user management by admin"""
    # Login as admin
    response = client.post('/api/auth/login', json={
        'email': admin_user.email,
        'password': 'password'
    })
    token = response.json['token']
    headers = {'Authorization': f'Bearer {token}'}

    # Create user
    response = client.post('/api/users',
        headers=headers,
        json={
            'email': 'testuser@test.com',
            'username': 'testuser',
            'password': 'password123',
            'subsite_id': test_subsite.id
        }
    )
    assert response.status_code == 201
    user_id = response.json['id']

    # Get user
    response = client.get(f'/api/users/{user_id}', headers=headers)
    assert response.status_code == 200
    assert response.json['email'] == 'testuser@test.com'

    # Update user
    response = client.put(f'/api/users/{user_id}',
        headers=headers,
        json={
            'username': 'updateduser'
        }
    )
    assert response.status_code == 200
    assert response.json['username'] == 'updateduser'

    # Delete user
    response = client.delete(f'/api/users/{user_id}', headers=headers)
    assert response.status_code == 204

def test_file_upload(client, regular_user, auth_headers, _db):
    """Test file upload and management"""
    # Create test file
    test_file_path = 'tests/test_file.txt'
    with open(test_file_path, 'w') as f:
        f.write('Test content')

    try:
        # Upload file
        with open(test_file_path, 'rb') as f:
            response = client.post('/api/files',
                headers=auth_headers,
                data={
                    'file': (f, 'test_file.txt'),
                    'description': 'Test file'
                }
            )
        assert response.status_code == 201
        file_id = response.json['id']

        # Get file info
        response = client.get(f'/api/files/{file_id}', headers=auth_headers)
        assert response.status_code == 200
        assert response.json['original_name'] == 'test_file.txt'

        # Download file
        response = client.get(f'/api/files/{file_id}/download', headers=auth_headers)
        assert response.status_code == 200
        assert response.data == b'Test content'

    finally:
        # Cleanup
        if os.path.exists(test_file_path):
            os.remove(test_file_path)

def test_messaging(client, regular_user, subadmin_user, auth_headers, _db):
    """Test messaging system"""
    # Send message
    response = client.post('/api/messages',
        headers=auth_headers,
        json={
            'subject': 'Test Message',
            'content': 'Hello world',
            'receiver_id': subadmin_user.id
        }
    )
    assert response.status_code == 201
    message_id = response.json['id']

    # Get message
    response = client.get(f'/api/messages/{message_id}', headers=auth_headers)
    assert response.status_code == 200
    assert response.json['subject'] == 'Test Message'

    # Reply to message
    response = client.post(f'/api/messages/{message_id}/reply',
        headers=auth_headers,
        json={
            'content': 'Reply message'
        }
    )
    assert response.status_code == 201

    # Get thread
    response = client.get(f'/api/messages/{message_id}/thread', headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json) == 2
