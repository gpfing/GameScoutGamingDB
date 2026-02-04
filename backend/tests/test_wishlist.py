"""
Tests for wishlist/collection routes
"""
import pytest
from models import db, Game


class TestWishlistGet:
    """Tests for getting wishlist/collection"""
    
    def test_get_empty_wishlist(self, client, auth_headers):
        """Test getting empty collection"""
        response = client.get('/api/wishlist', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'games' in response.json
        assert len(response.json['games']) == 0
    
    def test_get_wishlist_with_games(self, client, auth_headers, app):
        """Test getting collection with games"""
        with app.app_context():
            # Get user ID
            profile = client.get('/api/auth/me', headers=auth_headers)
            user_id = profile.json['id']
            
            # Add games to collection
            game1 = Game(
                user_id=user_id,
                rawg_id=1,
                title='Game 1',
                status='wishlist'
            )
            game2 = Game(
                user_id=user_id,
                rawg_id=2,
                title='Game 2',
                status='played'
            )
            db.session.add(game1)
            db.session.add(game2)
            db.session.commit()
        
        response = client.get('/api/wishlist', headers=auth_headers)
        
        assert response.status_code == 200
        assert len(response.json['games']) == 2


class TestWishlistAdd:
    """Tests for adding games to collection"""
    
    def test_add_game_to_wishlist(self, client, auth_headers):
        """Test adding a game to wishlist"""
        response = client.post('/api/wishlist',
            headers=auth_headers,
            json={
                'rawg_id': 12345,
                'title': 'New Game',
                'cover_image': 'https://example.com/image.jpg',
                'rating': 4.5,
                'release_date': '2024-01-01',
                'status': 'wishlist',
                'genres': ['Action', 'Adventure'],
                'platforms': ['PC']
            }
        )
        
        assert response.status_code == 201
        assert 'game' in response.json
        assert response.json['game']['title'] == 'New Game'
        assert response.json['game']['status'] == 'wishlist'
    
    def test_add_game_as_played(self, client, auth_headers):
        """Test adding a game directly as played"""
        response = client.post('/api/wishlist',
            headers=auth_headers,
            json={
                'rawg_id': 99999,
                'title': 'Completed Game',
                'status': 'played'
            }
        )
        
        assert response.status_code == 201
        assert response.json['game']['status'] == 'played'
    
    def test_update_existing_game_status(self, client, auth_headers):
        """Test updating status of existing game"""
        # Add game to wishlist
        client.post('/api/wishlist',
            headers=auth_headers,
            json={
                'rawg_id': 555,
                'title': 'Game',
                'status': 'wishlist'
            }
        )
        
        # Try to add same game as played (should update)
        response = client.post('/api/wishlist',
            headers=auth_headers,
            json={
                'rawg_id': 555,
                'title': 'Game',
                'status': 'played'
            }
        )
        
        assert response.status_code == 200
        assert 'updated' in response.json['message'].lower()
        assert response.json['game']['status'] == 'played'
    
    def test_add_game_missing_fields(self, client, auth_headers):
        """Test adding game with missing required fields"""
        response = client.post('/api/wishlist',
            headers=auth_headers,
            json={
                'rawg_id': 123
                # Missing title
            }
        )
        
        assert response.status_code == 400


class TestWishlistUpdate:
    """Tests for updating games in collection"""
    
    def test_update_game_status(self, client, auth_headers, app):
        """Test updating game status"""
        with app.app_context():
            # Get user and add game
            profile = client.get('/api/auth/me', headers=auth_headers)
            user_id = profile.json['id']
            
            game = Game(
                user_id=user_id,
                rawg_id=777,
                title='Test Game',
                status='wishlist'
            )
            db.session.add(game)
            db.session.commit()
            game_id = game.id
        
        response = client.patch(f'/api/wishlist/{game_id}',
            headers=auth_headers,
            json={'status': 'played'}
        )
        
        assert response.status_code == 200
        assert response.json['game']['status'] == 'played'
    
    def test_update_nonexistent_game(self, client, auth_headers):
        """Test updating game that doesn't exist"""
        response = client.patch('/api/wishlist/99999',
            headers=auth_headers,
            json={'status': 'played'}
        )
        
        assert response.status_code == 404


class TestWishlistDelete:
    """Tests for deleting games from collection"""
    
    def test_delete_game(self, client, auth_headers, app):
        """Test deleting a game"""
        with app.app_context():
            # Get user and add game
            profile = client.get('/api/auth/me', headers=auth_headers)
            user_id = profile.json['id']
            
            game = Game(
                user_id=user_id,
                rawg_id=888,
                title='Game to Delete',
                status='wishlist'
            )
            db.session.add(game)
            db.session.commit()
            game_id = game.id
        
        response = client.delete(f'/api/wishlist/{game_id}',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # Verify it's gone
        get_response = client.get('/api/wishlist', headers=auth_headers)
        assert len(get_response.json['games']) == 0
    
    def test_delete_nonexistent_game(self, client, auth_headers):
        """Test deleting game that doesn't exist"""
        response = client.delete('/api/wishlist/99999',
            headers=auth_headers
        )
        
        assert response.status_code == 404


class TestWishlistCheck:
    """Tests for checking if game is in collection"""
    
    def test_check_game_in_wishlist(self, client, auth_headers, app):
        """Test checking if game is in collection"""
        with app.app_context():
            # Get user and add game
            profile = client.get('/api/auth/me', headers=auth_headers)
            user_id = profile.json['id']
            
            game = Game(
                user_id=user_id,
                rawg_id=444,
                title='Checked Game',
                status='wishlist'
            )
            db.session.add(game)
            db.session.commit()
        
        response = client.get('/api/wishlist/check/444',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json['in_wishlist'] is True
        assert response.json['game'] is not None
    
    def test_check_game_not_in_wishlist(self, client, auth_headers):
        """Test checking game not in collection"""
        response = client.get('/api/wishlist/check/99999',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        assert response.json['in_wishlist'] is False
        assert response.json['game'] is None
