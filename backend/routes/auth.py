from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Create a new user account with preferences"""
    data = request.get_json()
    
    # Validate required fields
    if not data or not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Missing required fields'}), 400
    
    # Check if user already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 409
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 409
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        favorite_genres=data.get('favorite_genres', []),
        favorite_platforms=data.get('favorite_platforms', [])
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Create JWT token (convert ID to string)
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'User created successfully',
        'access_token': access_token,
        'user': user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['username', 'password']):
        return jsonify({'error': 'Missing username or password'}), 400
    
    # Find user
    user = User.query.filter_by(username=data['username']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid username or password'}), 401
    
    # Create JWT token (convert ID to string)
    access_token = create_access_token(identity=str(user.id))
    
    return jsonify({
        'message': 'Login successful',
        'access_token': access_token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current authenticated user's information"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify(user.to_dict()), 200


@auth_bp.route('/preferences', methods=['PATCH'])
@jwt_required()
def update_preferences():
    """Update user's favorite genres and platforms"""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    if 'favorite_genres' in data:
        user.favorite_genres = data['favorite_genres']
    
    if 'favorite_platforms' in data:
        user.favorite_platforms = data['favorite_platforms']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Preferences updated successfully',
        'user': user.to_dict()
    }), 200
