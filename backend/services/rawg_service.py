import requests
from datetime import datetime, timedelta
from flask import current_app
from flask_caching import Cache

cache = Cache()

class RAWGService:
    """Service for interacting with RAWG Video Games Database API"""
    
    @staticmethod
    def _get_api_key():
        """Get RAWG API key from config"""
        return current_app.config['RAWG_API_KEY']
    
    @staticmethod
    def _get_base_url():
        """Get RAWG base URL from config"""
        return current_app.config['RAWG_BASE_URL']
    
    @staticmethod
    def search_games(page=1, page_size=20, genres=None, platforms=None, release_filter='both', search=None):
        """
        Search for games with filters
        
        Args:
            page: Page number
            page_size: Number of results per page
            genres: Comma-separated genre slugs (e.g., 'action,rpg')
            platforms: Comma-separated platform IDs (e.g., '4,187')
            release_filter: 'upcoming', 'current', or 'both'
            search: Search query string
        """
        base_url = RAWGService._get_base_url()
        api_key = RAWGService._get_api_key()
        
        params = {
            'key': api_key,
            'page': page,
            'page_size': page_size,
            'ordering': '-released'
        }
        
        # Add search query
        if search:
            params['search'] = search
        
        # Add genre filter
        if genres:
            params['genres'] = genres
        
        # Add platform filter
        if platforms:
            params['platforms'] = platforms
        
        # Add date filters based on release_filter
        today = datetime.now().strftime('%Y-%m-%d')
        six_months_ago = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
        two_years_ago = (datetime.now() - timedelta(days=730)).strftime('%Y-%m-%d')
        one_year_from_now = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        if release_filter == 'upcoming':
            params['dates'] = f'{today},{one_year_from_now}'
        elif release_filter == 'current':
            params['dates'] = f'{six_months_ago},{today}'
        else:  # 'both' - show games from past 2 years to 1 year future
            params['dates'] = f'{two_years_ago},{one_year_from_now}'
        
        try:
            response = requests.get(f'{base_url}/games', params=params, timeout=10)
            response.raise_for_status()
            result = response.json()
            return result
        except requests.RequestException as e:
            current_app.logger.error(f'RAWG API error: {str(e)}')
            return {'error': str(e), 'results': []}
    
    @staticmethod
    @cache.memoize(timeout=21600)
    def get_game_details(game_id):
        """Get detailed information about a specific game"""
        base_url = RAWGService._get_base_url()
        api_key = RAWGService._get_api_key()
        
        params = {'key': api_key}
        
        try:
            response = requests.get(f'{base_url}/games/{game_id}', params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f'RAWG API error: {str(e)}')
            return {'error': str(e)}
    
    @staticmethod
    @cache.memoize(timeout=21600)
    def get_game_screenshots(game_id):
        """Get screenshots for a specific game"""
        base_url = RAWGService._get_base_url()
        api_key = RAWGService._get_api_key()
        
        params = {'key': api_key}
        
        try:
            response = requests.get(f'{base_url}/games/{game_id}/screenshots', params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f'RAWG API error: {str(e)}')
            return {'error': str(e), 'results': []}
    
    @staticmethod
    @cache.memoize(timeout=86400)  # Cache for 24 hours (genres don't change often)
    def get_genres():
        """Get list of available genres"""
        base_url = RAWGService._get_base_url()
        api_key = RAWGService._get_api_key()
        
        params = {'key': api_key}
        
        try:
            response = requests.get(f'{base_url}/genres', params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f'RAWG API error: {str(e)}')
            return {'error': str(e), 'results': []}
    
    @staticmethod
    @cache.memoize(timeout=86400)  # Cache for 24 hours
    def get_platforms():
        """Get list of available platforms"""
        base_url = RAWGService._get_base_url()
        api_key = RAWGService._get_api_key()
        
        params = {'key': api_key}
        
        try:
            response = requests.get(f'{base_url}/platforms', params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            current_app.logger.error(f'RAWG API error: {str(e)}')
            return {'error': str(e), 'results': []}
