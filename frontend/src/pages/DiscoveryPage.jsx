import { useState, useEffect } from 'react';
import api from '../utils/api';
import GameCard from '../components/GameCard';
import GameModal from '../components/GameModal';
import FilterBar from '../components/FilterBar';
import './DiscoveryPage.css';

function DiscoveryPage() {
  const [games, setGames] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [selectedGame, setSelectedGame] = useState(null);
  const [filters, setFilters] = useState({
    search: '',
    genres: '',
    platforms: '',
    release_filter: 'both',
  });
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  useEffect(() => {
    fetchGames();
  }, [filters, page, refreshTrigger]);

  const fetchGames = async () => {
    setLoading(true);
    setError('');

    try {
      const params = {
        page,
        page_size: 20,
        ...filters,
      };

      const response = await api.get('/games/search', { params });
      
      if (response.data.results) {
        if (page === 1) {
          setGames(response.data.results);
        } else {
          setGames(prev => [...prev, ...response.data.results]);
        }
        setHasMore(response.data.next !== null);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load games');
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
    setPage(1);
    setGames([]);
    // Trigger refresh even if filter values haven't changed
    setRefreshTrigger(prev => prev + 1);
  };

  const loadMore = () => {
    if (!loading && hasMore) {
      setPage(prev => prev + 1);
    }
  };

  const handleGameClick = (game) => {
    setSelectedGame(game);
  };

  const closeModal = () => {
    setSelectedGame(null);
    // Refresh the games list to exclude any newly played games
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <div className="discovery-page">
      <h1>Discover Games</h1>
      <p className="subtitle">Search and filter to find your next favorite game</p>
      
      <FilterBar filters={filters} onFilterChange={handleFilterChange} />

      {error && <div className="error-message">{error}</div>}

      <div className="games-grid">
        {games.map(game => (
          <GameCard
            key={game.id}
            game={game}
            onClick={() => handleGameClick(game)}
          />
        ))}
      </div>

      {loading && <div className="loading">Loading games...</div>}

      {!loading && games.length === 0 && (
        <div className="no-results">
          No games found. Try adjusting your filters.
        </div>
      )}

      {!loading && hasMore && games.length > 0 && (
        <button onClick={loadMore} className="btn-load-more">
          Load More
        </button>
      )}

      {selectedGame && (
        <GameModal game={selectedGame} onClose={closeModal} />
      )}
    </div>
  );
}

export default DiscoveryPage;
