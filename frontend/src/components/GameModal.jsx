import { useState, useEffect } from 'react';
import api from '../utils/api';
import './GameModal.css';

function GameModal({ game, onClose }) {
  const [details, setDetails] = useState(null);
  const [screenshots, setScreenshots] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addingToWishlist, setAddingToWishlist] = useState(false);
  const [message, setMessage] = useState('');
  const [currentStatus, setCurrentStatus] = useState(null);

  useEffect(() => {
    fetchGameDetails();
    checkGameStatus();
  }, [game.id]);

  const fetchGameDetails = async () => {
    try {
      const [detailsRes, screenshotsRes] = await Promise.all([
        api.get(`/games/${game.id}`),
        api.get(`/games/${game.id}/screenshots`),
      ]);
      setDetails(detailsRes.data);
      setScreenshots(screenshotsRes.data.results || []);
    } catch (err) {
      console.error('Failed to fetch game details:', err);
    } finally {
      setLoading(false);
    }
  };

  const checkGameStatus = async () => {
    try {
      const response = await api.get(`/wishlist/check/${game.id}`);
      if (response.data.in_wishlist && response.data.game) {
        setCurrentStatus(response.data.game.status);
      }
    } catch (err) {
      console.error('Failed to check game status:', err);
    }
  };

  const addToWishlist = async (status = 'wishlist') => {
    setAddingToWishlist(true);
    setMessage('');

    try {
      const gameData = {
        rawg_id: game.id,
        title: game.name,
        cover_image: game.background_image,
        rating: game.rating,
        release_date: game.released,
        status,
        genres: game.genres?.map(g => g.name) || [],
        platforms: game.platforms?.map(p => p.platform.name) || [],
      };

      await api.post('/wishlist', gameData);
      setCurrentStatus(status);
      setMessage(`Status updated to ${status}!`);
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      setMessage(err.response?.data?.error || 'Failed to update status');
    } finally {
      setAddingToWishlist(false);
    }
  };

  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  if (loading) {
    return (
      <div className="modal-backdrop" onClick={handleBackdropClick}>
        <div className="modal-content">
          <div className="modal-loading">Loading...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-backdrop" onClick={handleBackdropClick}>
      <div className="modal-content">
        <button className="modal-close" onClick={onClose}>
          ✕
        </button>

        <div className="modal-header">
          <img
            src={game.background_image || '/placeholder.png'}
            alt={game.name}
            className="modal-cover"
          />
          <div className="modal-title-section">
            <h2>{game.name}</h2>
            {game.rating && (
              <div className="modal-rating">⭐ {game.rating.toFixed(1)}</div>
            )}
          </div>
        </div>

        <div className="modal-body">
          {message && (
            <div className={`modal-message ${message.includes('Failed') ? 'error' : 'success'}`}>
              {message}
            </div>
          )}

          {currentStatus && (
            <div className="current-status">
              Current Status: <strong>{currentStatus.charAt(0).toUpperCase() + currentStatus.slice(1)}</strong>
            </div>
          )}

          <div className="wishlist-actions">
            <button
              onClick={() => addToWishlist('wishlist')}
              disabled={addingToWishlist || currentStatus === 'wishlist'}
              className={`btn-wishlist ${currentStatus === 'wishlist' ? 'active' : ''}`}
            >
              {currentStatus === 'wishlist' ? '✓ In Wishlist' : 'Add to Wishlist'}
            </button>
            <button
              onClick={() => addToWishlist('played')}
              disabled={addingToWishlist || currentStatus === 'played'}
              className={`btn-played ${currentStatus === 'played' ? 'active' : ''}`}
            >
              {currentStatus === 'played' ? '✓ Played' : 'Mark as Played'}
            </button>
          </div>

          <div className="modal-info">
            <div className="info-row">
              <strong>Release Date:</strong>
              <span>{game.released ? new Date(game.released).toLocaleDateString() : 'TBA'}</span>
            </div>

            {details?.developers && details.developers.length > 0 && (
              <div className="info-row">
                <strong>Developers:</strong>
                <span>{details.developers.map(d => d.name).join(', ')}</span>
              </div>
            )}

            {details?.publishers && details.publishers.length > 0 && (
              <div className="info-row">
                <strong>Publishers:</strong>
                <span>{details.publishers.map(p => p.name).join(', ')}</span>
              </div>
            )}

            {game.genres && game.genres.length > 0 && (
              <div className="info-row">
                <strong>Genres:</strong>
                <div className="genre-tags">
                  {game.genres.map(genre => (
                    <span key={genre.id} className="genre-tag">
                      {genre.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {game.platforms && game.platforms.length > 0 && (
              <div className="info-row">
                <strong>Platforms:</strong>
                <span>{game.platforms.map(p => p.platform.name).join(', ')}</span>
              </div>
            )}
          </div>

          {details?.description_raw && (
            <div className="modal-description">
              <h3>About</h3>
              <p>{details.description_raw}</p>
            </div>
          )}

          {screenshots.length > 0 && (
            <div className="modal-screenshots">
              <h3>Screenshots</h3>
              <div className="screenshots-grid">
                {screenshots.map((screenshot, index) => (
                  <img
                    key={screenshot.id}
                    src={screenshot.image}
                    alt={`Screenshot ${index + 1}`}
                    className="screenshot-image"
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default GameModal;
