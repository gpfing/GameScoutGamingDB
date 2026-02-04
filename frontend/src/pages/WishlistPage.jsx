import { useState, useEffect } from 'react';
import api from '../utils/api';
import './WishlistPage.css';

function WishlistPage() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, wishlist, played

  useEffect(() => {
    fetchWishlist();
  }, []);

  const fetchWishlist = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await api.get('/wishlist');
      setGames(response.data.games || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load collection');
    } finally {
      setLoading(false);
    }
  };

  const updateGameStatus = async (gameId, newStatus) => {
    try {
      await api.patch(`/wishlist/${gameId}`, { status: newStatus });
      setGames(games.map(game =>
        game.id === gameId ? { ...game, status: newStatus } : game
      ));
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to update game');
    }
  };

  const removeGame = async (gameId) => {
    if (!confirm('Are you sure you want to remove this game from your collection?')) {
      return;
    }

    try {
      await api.delete(`/wishlist/${gameId}`);
      setGames(games.filter(game => game.id !== gameId));
    } catch (err) {
      alert(err.response?.data?.error || 'Failed to remove game');
    }
  };

  const filteredGames = filter === 'all'
    ? games
    : games.filter(game => game.status === filter);

  const getStatusCount = (status) => {
    return games.filter(game => game.status === status).length;
  };

  if (loading) {
    return <div className="loading">Loading collection...</div>;
  }

  return (
    <div className="wishlist-page">
      <h1>My Collection</h1>

      <div className="wishlist-filters">
        <button
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All ({games.length})
        </button>
        <button
          className={`filter-btn ${filter === 'wishlist' ? 'active' : ''}`}
          onClick={() => setFilter('wishlist')}
        >
          Wishlist ({getStatusCount('wishlist')})
        </button>
        <button
          className={`filter-btn ${filter === 'played' ? 'active' : ''}`}
          onClick={() => setFilter('played')}
        >
          Played ({getStatusCount('played')})
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {filteredGames.length === 0 ? (
        <div className="empty-state">
          <p>🎮</p>
          <h2>No games found</h2>
          <p>Start adding games to your collection from the Discover page!</p>
        </div>
      ) : (
        <div className="wishlist-grid">
          {filteredGames.map(game => (
            <div key={game.id} className="wishlist-item">
              <div className="wishlist-item-image">
                {game.cover_image ? (
                  <img src={game.cover_image} alt={game.title} />
                ) : (
                  <div className="image-placeholder">🎮</div>
                )}
              </div>

              <div className="wishlist-item-content">
                <h3>{game.title}</h3>

                {game.release_date && (
                  <p className="release-date">
                    📅 {new Date(game.release_date).toLocaleDateString()}
                  </p>
                )}

                {game.rating && (
                  <p className="rating">⭐ {game.rating.toFixed(1)}</p>
                )}

                {game.genres && game.genres.length > 0 && (
                  <div className="genres">
                    {game.genres.slice(0, 3).map((genre, index) => (
                      <span key={index} className="genre-tag">
                        {genre}
                      </span>
                    ))}
                  </div>
                )}

                <div className="wishlist-item-actions">
                  <select
                    value={game.status}
                    onChange={(e) => updateGameStatus(game.id, e.target.value)}
                    className="status-select"
                  >
                    <option value="wishlist">Wishlist</option>
                    <option value="played">Played</option>
                  </select>

                  <button
                    onClick={() => removeGame(game.id)}
                    className="btn-remove"
                    title="Remove from wishlist"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default WishlistPage;
