"""
Test configuration and fixtures for pytest
"""
import os
import pytest
from app import create_app
from models import db, User, Game


class TestConfig:
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    JWT_SECRET_KEY = 'test-jwt-secret-key'
    SECRET_KEY = 'test-secret-key'
    CACHE_TYPE = 'SimpleCache'


@pytest.fixture(scope='function')
def app():
    """Create application for testing"""
    app = create_app()
    app.config.from_object(TestConfig)
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Create test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Create authenticated user and return auth headers"""
    # Register user and get token directly
    response = client.post('/api/auth/signup', json={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    })
    
    # Signup returns the token directly
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def sample_user(app):
    """Create a sample user"""
    with app.app_context():
        user = User(
            username='sampleuser',
            email='sample@example.com'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def sample_game(app, sample_user):
    """Create a sample game"""
    with app.app_context():
        game = Game(
            user_id=sample_user.id,
            rawg_id=12345,
            title='Test Game',
            cover_image='https://example.com/image.jpg',
            rating=4.5,
            release_date='2024-01-01',
            status='wishlist',
            genres=['Action', 'Adventure'],
            platforms=['PC', 'PlayStation 5']
        )
        db.session.add(game)
        db.session.commit()
        return game
