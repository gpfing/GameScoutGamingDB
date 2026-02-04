from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    favorite_genres = db.Column(db.JSON, default=list)
    favorite_platforms = db.Column(db.JSON, default=list)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    games = db.relationship('Game', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.hashed_password.encode('utf-8'))
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'favorite_genres': self.favorite_genres or [],
            'favorite_platforms': self.favorite_platforms or [],
            'created_at': self.created_at.isoformat()
        }


class Game(db.Model):
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rawg_id = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    cover_image = db.Column(db.String(500))
    rating = db.Column(db.Float)
    release_date = db.Column(db.String(50))
    status = db.Column(db.String(20), default='wishlist')
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    genres = db.Column(db.JSON, default=list)
    platforms = db.Column(db.JSON, default=list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'rawg_id': self.rawg_id,
            'title': self.title,
            'cover_image': self.cover_image,
            'rating': self.rating,
            'release_date': self.release_date,
            'status': self.status,
            'added_at': self.added_at.isoformat(),
            'genres': self.genres or [],
            'platforms': self.platforms or []
        }
