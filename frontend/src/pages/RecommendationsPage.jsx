import { useState, useEffect } from 'react';
import api from '../utils/api';
import { useAuth } from '../context/AuthContext';
import GameCard from '../components/GameCard';
import GameModal from '../components/GameModal';
import PreferenceBar from '../components/PreferenceBar';
import './RecommendationsPage.css';

function RecommendationsPage() {
  const { user } = useAuth();
  const [preferenceRecommendations, setPreferenceRecommendations] = useState([]);
  const [genreRecommendations, setGenreRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedGame, setSelectedGame] = useState(null);

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await api.get('/games/recommendations');
      setPreferenceRecommendations(response.data.preference_based || []);
      setGenreRecommendations(response.data.genre_based || []);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load recommendations');
    } finally {
      setLoading(false);
    }
  };

  const handleGameClick = (game) => {
    setSelectedGame(game);
  };

  const closeModal = () => {
    setSelectedGame(null);
  };

  if (loading) {
    return <div className="loading">Loading recommendations...</div>;
  }

  return (
    <div className="recommendations-page">
      <div className="recommendations-header">
        <h1>Recommended for You</h1>
        <p className="subtitle">
          Update your preferences below to get personalized recommendations based on your taste and wishlist
        </p>
      </div>

      <PreferenceBar user={user} onPreferencesUpdate={fetchRecommendations} />

      {error && <div className="error-message">{error}</div>}

      {preferenceRecommendations.length === 0 && genreRecommendations.length === 0 ? (
        <div className="empty-state">
          <p>🎯</p>
          <h2>No recommendations found</h2>
          <p>
            We only show games with a rating of 3.0 or higher. Try selecting different genres or platforms, 
            or check the Discovery page to search all available games.
          </p>
        </div>
      ) : (
        <>
          {preferenceRecommendations.length > 0 && (
            <div className="recommendation-section">
              <h2 className="section-title">Based on Your Preferences</h2>
              <div className="games-grid">
                {preferenceRecommendations.map(game => (
                  <GameCard
                    key={game.id}
                    game={game}
                    onClick={() => handleGameClick(game)}
                  />
                ))}
              </div>
            </div>
          )}

          {genreRecommendations.length > 0 && (
            <div className="recommendation-section">
              <h2 className="section-title">Based on Your Collection</h2>
              <p className="section-subtitle">
                Games that share genres with titles you've enjoyed or want to play
              </p>
              <div className="games-grid">
                {genreRecommendations.map(game => (
                  <GameCard
                    key={game.id}
                    game={game}
                    onClick={() => handleGameClick(game)}
                  />
                ))}
              </div>
            </div>
          )}

          <button onClick={fetchRecommendations} className="btn-refresh">
            🔄 Refresh Recommendations
          </button>
        </>
      )}

      {selectedGame && (
        <GameModal game={selectedGame} onClose={closeModal} />
      )}
    </div>
  );
}

export default RecommendationsPage;
