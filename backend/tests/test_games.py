"""
Tests for games routes
"""
import pytest
from unittest.mock import patch, MagicMock


class TestGamesSearch:
    """Tests for game search endpoint"""
    
    @patch('routes.games.RAWGService.search_games')
    def test_search_games_success(self, mock_search, client, auth_headers):
        """Test successful game search"""
        mock_search.return_value = {
            'results': [
                {
                    'id': 1,
                    'name': 'Test Game',
                    'rating': 4.5,
                    'background_image': 'https://example.com/image.jpg'
                }
            ],
            'next': None
        }
        
        response = client.get('/api/games/search?page=1&page_size=20', 
                            headers=auth_headers)
        
        assert response.status_code == 200
        assert 'results' in response.json
        assert len(response.json['results']) == 1
        mock_search.assert_called_once()
    
    @patch('routes.games.RAWGService.search_games')
    def test_search_excludes_played_games(self, mock_search, client, auth_headers, app):
        """Test that search excludes played games"""
        from models import db, Game
        
        with app.app_context():
            # Add a played game to user's collection
            # First, get user from auth_headers
            response = client.get('/api/auth/me', headers=auth_headers)
            user_id = response.json['id']
            
            game = Game(
                user_id=user_id,
                rawg_id=999,
                title='Played Game',
                status='played'
            )
            db.session.add(game)
            db.session.commit()
        
        mock_search.return_value = {
            'results': [
                {'id': 999, 'name': 'Played Game'},
                {'id': 1000, 'name': 'Unplayed Game'}
            ],
            'next': None
        }
        
        response = client.get('/api/games/search', headers=auth_headers)
        
        # Should only return the unplayed game
        assert response.status_code == 200
        assert len(response.json['results']) == 1
        assert response.json['results'][0]['id'] == 1000
    
    @patch('routes.games.RAWGService.search_games')
    def test_search_filters_adult_content(self, mock_search, client, auth_headers):
        """Test that adult content is filtered out"""
        mock_search.return_value = {
            'results': [
                {'id': 1, 'name': 'Normal Game'},
                {'id': 2, 'name': 'Adult XXX Game'},
                {'id': 3, 'name': 'NSFW Content'}
            ],
            'next': None
        }
        
        response = client.get('/api/games/search', headers=auth_headers)
        
        assert response.status_code == 200
        # Should only return the normal game
        assert len(response.json['results']) == 1
        assert response.json['results'][0]['name'] == 'Normal Game'


class TestGameDetails:
    """Tests for game details endpoint"""
    
    @patch('routes.games.RAWGService.get_game_details')
    def test_get_game_details(self, mock_details, client, auth_headers):
        """Test getting game details"""
        mock_details.return_value = {
            'id': 1,
            'name': 'Test Game',
            'description': 'A test game',
            'rating': 4.5
        }
        
        response = client.get('/api/games/1', headers=auth_headers)
        
        assert response.status_code == 200
        assert response.json['name'] == 'Test Game'
        mock_details.assert_called_once_with(1)


class TestRecommendations:
    """Tests for recommendations endpoint"""
    
    @patch('routes.games.RAWGService.search_games')
    @patch('routes.games.RAWGService.get_genres')
    @patch('routes.games.RAWGService.get_platforms')
    def test_recommendations_with_preferences(self, mock_platforms, mock_genres, 
                                             mock_search, client, auth_headers, app):
        """Test recommendations based on user preferences"""
        mock_genres.return_value = {
            'results': [{'id': 1, 'name': 'Action', 'slug': 'action'}]
        }
        mock_platforms.return_value = {
            'results': [{'id': 4, 'name': 'PC'}]
        }
        mock_search.return_value = {
            'results': [
                {'id': 1, 'name': 'Game 1', 'rating': 4.5},
                {'id': 2, 'name': 'Game 2', 'rating': 4.0}
            ],
            'next': None
        }
        
        with app.app_context():
            # Set user preferences
            client.patch('/api/auth/preferences',
                headers=auth_headers,
                json={
                    'favorite_genres': ['Action'],
                    'favorite_platforms': ['PC']
                }
            )
        
        response = client.get('/api/games/recommendations', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'preference_based' in response.json
        assert 'genre_based' in response.json
    
    def test_recommendations_filters_low_rated(self, client, auth_headers):
        """Test that recommendations only include 3.0+ rated games"""
        # This is tested by the backend filtering logic
        # The actual filtering is done in the route
        response = client.get('/api/games/recommendations', headers=auth_headers)
        
        assert response.status_code == 200
        # All returned games should have rating >= 3.0
        for game in response.json.get('preference_based', []):
            if 'rating' in game and game['rating'] is not None:
                assert game['rating'] >= 3.0
