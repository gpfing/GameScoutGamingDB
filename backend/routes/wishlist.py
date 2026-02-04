from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Game, User

wishlist_bp = Blueprint('wishlist', __name__, url_prefix='/api/wishlist')

@wishlist_bp.route('', methods=['GET'])
@jwt_required()
def get_wishlist():
    """Get all games in user's wishlist"""
    user_id = int(get_jwt_identity())
    games = Game.query.filter_by(user_id=user_id).order_by(Game.added_at.desc()).all()
    
    return jsonify({
        'games': [game.to_dict() for game in games]
    }), 200


@wishlist_bp.route('', methods=['POST'])
@jwt_required()
def add_to_wishlist():
    """Add a game to user's wishlist or update existing game status"""
    user_id = int(get_jwt_identity())
    data = request.get_json()
    
    # Validate required fields
    if not data or not all(k in data for k in ['rawg_id', 'title']):
        return jsonify({'error': 'Missing required fields (rawg_id, title)'}), 400
    
    # Check if game already in wishlist
    existing_game = Game.query.filter_by(
        user_id=user_id,
        rawg_id=data['rawg_id']
    ).first()
    
    if existing_game:
        # Update existing game status instead of erroring
        new_status = data.get('status', 'wishlist')
        existing_game.status = new_status
        db.session.commit()
        return jsonify({
            'message': f'Game status updated to {new_status}',
            'game': existing_game.to_dict()
        }), 200
    
    # Create new game entry
    game = Game(
        user_id=user_id,
        rawg_id=data['rawg_id'],
        title=data['title'],
        cover_image=data.get('cover_image'),
        rating=data.get('rating'),
        release_date=data.get('release_date'),
        status=data.get('status', 'wishlist'),
        genres=data.get('genres', []),
        platforms=data.get('platforms', [])
    )
    
    db.session.add(game)
    db.session.commit()
    
    return jsonify({
        'message': 'Game added to wishlist',
        'game': game.to_dict()
    }), 201


@wishlist_bp.route('/<int:game_id>', methods=['GET'])
@jwt_required()
def get_wishlist_game(game_id):
    """Get a specific game from wishlist"""
    user_id = int(get_jwt_identity())
    game = Game.query.filter_by(id=game_id, user_id=user_id).first()
    
    if not game:
        return jsonify({'error': 'Game not found in wishlist'}), 404
    
    return jsonify(game.to_dict()), 200


@wishlist_bp.route('/<int:game_id>', methods=['PATCH'])
@jwt_required()
def update_wishlist_game(game_id):
    """Update a game's status in wishlist"""
    user_id = int(get_jwt_identity())
    game = Game.query.filter_by(id=game_id, user_id=user_id).first()
    
    if not game:
        return jsonify({'error': 'Game not found in wishlist'}), 404
    
    data = request.get_json()
    
    # Update status if provided
    if 'status' in data:
        if data['status'] not in ['wishlist', 'played', 'interested']:
            return jsonify({'error': 'Invalid status. Must be: wishlist, played, or interested'}), 400
        game.status = data['status']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Game updated successfully',
        'game': game.to_dict()
    }), 200


@wishlist_bp.route('/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_wishlist_game(game_id):
    """Remove a game from wishlist"""
    user_id = int(get_jwt_identity())
    game = Game.query.filter_by(id=game_id, user_id=user_id).first()
    
    if not game:
        return jsonify({'error': 'Game not found in wishlist'}), 404
    
    db.session.delete(game)
    db.session.commit()
    
    return jsonify({'message': 'Game removed from wishlist'}), 200


@wishlist_bp.route('/check/<int:rawg_id>', methods=['GET'])
@jwt_required()
def check_in_wishlist(rawg_id):
    """Check if a game is in user's wishlist"""
    user_id = int(get_jwt_identity())
    game = Game.query.filter_by(user_id=user_id, rawg_id=rawg_id).first()
    
    return jsonify({
        'in_wishlist': game is not None,
        'game': game.to_dict() if game else None
    }), 200
