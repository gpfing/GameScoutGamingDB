import { useState } from 'react';
import './GameCard.css';

function GameCard({ game, onClick }) {
  const [imageError, setImageError] = useState(false);

  const getRatingColor = (rating) => {
    if (rating >= 4.5) return '#4caf50';
    if (rating >= 4.0) return '#8bc34a';
    if (rating >= 3.5) return '#ffc107';
    if (rating >= 3.0) return '#ff9800';
    return '#f44336';
  };

  return (
    <div className="game-card" onClick={onClick}>
      <div className="game-card-image">
        {!imageError && game.background_image ? (
          <img
            src={game.background_image}
            alt={game.name}
            onError={() => setImageError(true)}
          />
        ) : (
          <div className="game-card-placeholder">
            <span>🎮</span>
          </div>
        )}
        {game.rating && (
          <div 
            className="game-rating" 
            style={{ backgroundColor: getRatingColor(game.rating) }}
          >
            ⭐ {game.rating.toFixed(1)}
          </div>
        )}
      </div>
      
      <div className="game-card-content">
        <h3 className="game-title">{game.name}</h3>
        
        {game.released && (
          <p className="game-release-date">
            📅 {new Date(game.released).toLocaleDateString()}
          </p>
        )}
        
        {game.genres && game.genres.length > 0 && (
          <div className="game-genres">
            {game.genres.slice(0, 2).map(genre => (
              <span key={genre.id} className="genre-tag">
                {genre.name}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default GameCard;
