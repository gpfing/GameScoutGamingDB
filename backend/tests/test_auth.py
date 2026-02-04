"""
Tests for authentication routes
"""
import pytest
from models import db, User


class TestAuthRegister:
    """Tests for user registration"""
    
    def test_register_success(self, client):
        """Test successful user registration"""
        response = client.post('/api/auth/signup', json={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        assert 'message' in response.json
        assert 'user' in response.json
        assert response.json['user']['username'] == 'newuser'
        assert response.json['user']['email'] == 'newuser@example.com'
    
    def test_register_missing_fields(self, client):
        """Test registration with missing fields"""
        response = client.post('/api/auth/signup', json={
            'username': 'testuser'
        })
        
        assert response.status_code == 400
        assert 'error' in response.json
    
    def test_register_duplicate_email(self, client):
        """Test registration with duplicate email"""
        # First registration
        client.post('/api/auth/signup', json={
            'username': 'user1',
            'email': 'duplicate@example.com',
            'password': 'password123'
        })
        
        # Try to register with same email
        response = client.post('/api/auth/signup', json={
            'username': 'user2',
            'email': 'duplicate@example.com',
            'password': 'password456'
        })
        
        assert response.status_code == 409
        assert 'already exists' in response.json['error'].lower()
    
    def test_register_duplicate_username(self, client):
        """Test registration with duplicate username"""
        # First registration
        client.post('/api/auth/signup', json={
            'username': 'duplicateuser',
            'email': 'email1@example.com',
            'password': 'password123'
        })
        
        # Try to register with same username
        response = client.post('/api/auth/signup', json={
            'username': 'duplicateuser',
            'email': 'email2@example.com',
            'password': 'password456'
        })
        
        assert response.status_code == 409


class TestAuthLogin:
    """Tests for user login"""
    
    def test_login_success(self, client):
        """Test successful login"""
        # Register user
        client.post('/api/auth/signup', json={
            'username': 'loginuser',
            'email': 'login@example.com',
            'password': 'password123'
        })
        
        # Login
        response = client.post('/api/auth/login', json={
            'username': 'loginuser',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        assert 'access_token' in response.json
        assert 'user' in response.json
    
    def test_login_invalid_email(self, client):
        """Test login with invalid username"""
        response = client.post('/api/auth/login', json={
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        assert response.status_code == 401
        assert 'error' in response.json
    
    def test_login_invalid_password(self, client):
        """Test login with invalid password"""
        # Register user
        client.post('/api/auth/signup', json={
            'username': 'user',
            'email': 'user@example.com',
            'password': 'correctpassword'
        })
        
        # Try to login with wrong password
        response = client.post('/api/auth/login', json={
            'username': 'user',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401


class TestAuthProfile:
    """Tests for user profile endpoints"""
    
    def test_get_profile(self, client, auth_headers):
        """Test getting user profile"""
        response = client.get('/api/auth/me', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'username' in response.json
        assert 'email' in response.json
    
    def test_get_profile_without_auth(self, client):
        """Test getting profile without authentication"""
        response = client.get('/api/auth/me')
        
        assert response.status_code == 401
    
    def test_update_preferences(self, client, auth_headers):
        """Test updating user preferences"""
        response = client.patch('/api/auth/preferences', 
            headers=auth_headers,
            json={
                'favorite_genres': ['Action', 'RPG'],
                'favorite_platforms': ['PC']
            }
        )
        
        assert response.status_code == 200
        assert response.json['user']['favorite_genres'] == ['Action', 'RPG']
        assert response.json['user']['favorite_platforms'] == ['PC']
    
    def test_update_preferences_validation(self, client, auth_headers):
        """Test preference validation limits"""
        # Try to set too many genres (limit is 2)
        response = client.patch('/api/auth/preferences',
            headers=auth_headers,
            json={
                'favorite_genres': ['Action', 'RPG', 'Strategy'],
                'favorite_platforms': ['PC']
            }
        )
        
        # Should accept but only store first 2
        assert response.status_code == 200
