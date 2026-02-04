from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.rawg_service import RAWGService
from models import db, Game, User
from collections import Counter

games_bp = Blueprint('games', __name__, url_prefix='/api/games')

# Keywords to filter out adult/NSFW content
ADULT_KEYWORDS = ['nsfw', 'adult', 'xxx', 'sex', 'porn', 'hentai', 'nude', 'naked', 
                  'bdsm', 'milf', 'fap', 'tits', 'ass', 'sexy', 'erotic', '18+']

def is_adult_content(game):
    """Check if game appears to be adult content"""
    name = game.get('name', '').lower()
    # Check if any adult keywords appear in the name
    return any(keyword in name for keyword in ADULT_KEYWORDS)

@games_bp.route('/search', methods=['GET'])
@jwt_required()
def search_games():
    """Search for games with filters"""
    try:
        user_id = int(get_jwt_identity())
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        genres = request.args.get('genres') or None  # Convert empty string to None
        platforms = request.args.get('platforms') or None  # Convert empty string to None
        release_filter = request.args.get('release_filter', 'both')
        search = request.args.get('search') or None  # Convert empty string to None
        
        result = RAWGService.search_games(
            page=page,
            page_size=page_size,
            genres=genres,
            platforms=platforms,
            release_filter=release_filter,
            search=search
        )
        
        # Get list of played games to exclude
        played_games = Game.query.filter_by(user_id=user_id, status='played').all()
        played_rawg_ids = {game.rawg_id for game in played_games}
        
        # Filter out adult content and played games from search results
        if 'results' in result:
            result['results'] = [
                game for game in result['results']
                if not is_adult_content(game) and game['id'] not in played_rawg_ids
            ]
        
        return jsonify(result), 200
    except Exception as e:
        print(f"Error in search_games: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@games_bp.route('/<int:game_id>', methods=['GET'])
@jwt_required()
def get_game_details(game_id):
    """Get detailed information about a specific game"""
    details = RAWGService.get_game_details(game_id)
    return jsonify(details), 200


@games_bp.route('/<int:game_id>/screenshots', methods=['GET'])
@jwt_required()
def get_game_screenshots(game_id):
    """Get screenshots for a specific game"""
    screenshots = RAWGService.get_game_screenshots(game_id)
    return jsonify(screenshots), 200


@games_bp.route('/genres', methods=['GET'])
def get_genres():
    """Get list of available genres (no auth required for filters)"""
    genres = RAWGService.get_genres()
    return jsonify(genres), 200


@games_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """Get list of available platforms (no auth required for filters)"""
    platforms = RAWGService.get_platforms()
    return jsonify(platforms), 200


@games_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    """Get personalized game recommendations based on user preferences"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get user's played games to exclude from recommendations
    played_games = Game.query.filter_by(user_id=user_id, status='played').all()
    played_rawg_ids = {game.rawg_id for game in played_games}
    
    # Get wishlist and played games for genre-based recommendations
    wishlist_and_played = Game.query.filter(
        Game.user_id == user_id,
        Game.status.in_(['wishlist', 'played'])
    ).all()
    
    # Convert user's favorite genre names to slugs for RAWG API
    genres_param = None
    if user.favorite_genres and len(user.favorite_genres) > 0:
        genres_response = RAWGService.get_genres()
        all_genres = genres_response.get('results', [])
        genre_name_to_slug = {g['name'].lower(): g['slug'] for g in all_genres}
        
        # Debug: Print available genres
        print(f"Available genres from RAWG: {list(genre_name_to_slug.keys())}")
        print(f"User's favorite genres: {user.favorite_genres}")
        
        # Convert user's favorite genre names to slugs
        genre_slugs = []
        for fav_genre in user.favorite_genres:
            slug = genre_name_to_slug.get(fav_genre.lower())
            if slug:
                genre_slugs.append(slug)
            else:
                print(f"Warning: Could not find slug for genre '{fav_genre}'")
        
        if genre_slugs:
            genres_param = ','.join(genre_slugs)
            print(f"Using genre slugs: {genres_param}")
    
    # Convert user's favorite platform names to IDs for RAWG API
    platforms_param = None
    if user.favorite_platforms and len(user.favorite_platforms) > 0:
        platforms_response = RAWGService.get_platforms()
        all_platforms = platforms_response.get('results', [])
        platform_name_to_id = {p['name'].lower(): str(p['id']) for p in all_platforms}
        
        print(f"Available platforms from RAWG: {list(platform_name_to_id.keys())}")
        print(f"User's favorite platforms: {user.favorite_platforms}")
        
        # Convert user's favorite platform names to IDs
        platform_ids = []
        for fav_platform in user.favorite_platforms:
            pid = platform_name_to_id.get(fav_platform.lower())
            if pid:
                platform_ids.append(pid)
            else:
                print(f"Warning: Could not find ID for platform '{fav_platform}'")
        
        if platform_ids:
            platforms_param = ','.join(platform_ids)
            print(f"Using platform IDs: {platforms_param}")
    
    # Fetch games matching user preferences from RAWG
    # Always use preferences now (max 2 genres, 1 platform)
    page_size = 40
    
    result = RAWGService.search_games(
        page=request.args.get('page', 1, type=int),
        page_size=page_size,
        genres=genres_param,
        platforms=platforms_param,
        release_filter='both'
    )
    
    # Filter out played games and adult content
    # Only show games with rating >= 3.0
    if 'results' in result:
        # Filter out adult content, played games, and low-rated/unrated games
        preference_based = [
            game for game in result['results']
            if game.get('id') not in played_rawg_ids 
            and not is_adult_content(game)
            and game.get('rating', 0) >= 3.0
        ][:20]  # Limit to 20 results
        
        # Sort by rating descending
        preference_based.sort(key=lambda x: x.get('rating', 0), reverse=True)
    else:
        preference_based = []
    
    # Get genre-based recommendations from wishlist and played games
    genre_based = []
    if wishlist_and_played:
        # Collect all genres from user's wishlist and played games
        user_genre_names = set()
        for game in wishlist_and_played:
            if game.genres:
                user_genre_names.update(g.lower() for g in game.genres)
        
        if user_genre_names:
            # Convert genre names to slugs for RAWG API
            genres_response = RAWGService.get_genres()
            all_genres = genres_response.get('results', [])
            genre_name_to_slug = {g['name'].lower(): g['slug'] for g in all_genres}
            
            print(f"User's collection genre names: {user_genre_names}")
            
            # Only use genres that match the user's collection
            genre_slugs = [genre_name_to_slug.get(g) for g in user_genre_names if genre_name_to_slug.get(g)]
            
            print(f"Matched genre slugs for recommendations: {genre_slugs}")
            
            if genre_slugs:
                # Fetch games matching ONLY these genres (not mixed)
                genre_result = RAWGService.search_games(
                    page=1,
                    page_size=40,
                    genres=','.join(genre_slugs),  # Use all matched genres
                    platforms=platforms_param,
                    release_filter='both'
                )
                
                if 'results' in genre_result:
                    # Filter to only include games where AT LEAST ONE genre matches user's collection
                    # and ensure high quality recommendations
                    filtered_games = []
                    for game in genre_result['results']:
                        if game.get('id') in played_rawg_ids or is_adult_content(game):
                            continue
                        if game.get('rating', 0) < 3.5:  # Higher threshold for collection-based
                            continue
                        
                        # Check if game has at least one genre from user's collection
                        game_genres = [g['name'].lower() for g in game.get('genres', [])]
                        has_matching_genre = any(ug in game_genres for ug in user_genre_names)
                        
                        if has_matching_genre:
                            filtered_games.append(game)
                    
                    # Sort by rating and limit
                    genre_based = sorted(filtered_games, key=lambda x: x.get('rating', 0), reverse=True)[:10]
                    
                    print(f"Found {len(genre_based)} genre-based recommendations")
    
    return jsonify({
        'preference_based': preference_based,
        'genre_based': genre_based
    }), 200
