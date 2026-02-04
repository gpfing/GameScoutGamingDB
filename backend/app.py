import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from models import db
from services.rawg_service import cache
from config import Config
from routes.auth import auth_bp
from routes.wishlist import wishlist_bp
from routes.games import games_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    cache.init_app(app)
    
    allowed_origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        os.getenv('FRONTEND_URL', '')
    ]
    allowed_origins = [origin for origin in allowed_origins if origin]
    
    CORS(app, resources={
        r"/api/*": {
            "origins": allowed_origins,
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": True
        }
    })
    jwt = JWTManager(app)
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return {'error': 'Invalid token', 'message': error_string}, 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        return {'error': 'Missing authorization', 'message': error_string}, 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has expired'}, 401
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {'error': 'Token has been revoked'}, 401
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(wishlist_bp)
    app.register_blueprint(games_bp)
    
    @app.errorhandler(422)
    def handle_unprocessable_entity(e):
        return {'error': 'Unprocessable Entity', 'message': str(e)}, 422
    
    with app.app_context():
        db.create_all()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'message': 'GameScout API is running'}, 200
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
