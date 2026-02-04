import { useState, useEffect } from 'react';
import api from '../utils/api';
import './FilterBar.css';

function FilterBar({ filters, onFilterChange }) {
  const [genres, setGenres] = useState([]);
  const [platforms, setPlatforms] = useState([]);
  const [localFilters, setLocalFilters] = useState(filters);

  useEffect(() => {
    fetchGenres();
    fetchPlatforms();
  }, []);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const fetchGenres = async () => {
    try {
      const response = await api.get('/games/genres');
      setGenres(response.data.results || []);
    } catch (err) {
      console.error('Failed to fetch genres:', err);
    }
  };

  const fetchPlatforms = async () => {
    try {
      const response = await api.get('/games/platforms');
      setPlatforms(response.data.results || []);
    } catch (err) {
      console.error('Failed to fetch platforms:', err);
    }
  };

  const handleChange = (key, value) => {
    const updated = { ...localFilters, [key]: value };
    setLocalFilters(updated);
  };

  const handleSearch = () => {
    onFilterChange(localFilters);
  };

  const handleReset = () => {
    const resetFilters = {
      search: '',
      genres: '',
      platforms: '',
      release_filter: 'both',
    };
    setLocalFilters(resetFilters);
    onFilterChange(resetFilters);
  };

  return (
    <div className="filter-bar">
      <div className="filter-row">
        <input
          type="text"
          placeholder="Search games..."
          value={localFilters.search}
          onChange={(e) => handleChange('search', e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          className="search-input"
        />

        <select
          value={localFilters.release_filter}
          onChange={(e) => handleChange('release_filter', e.target.value)}
          className="filter-select"
        >
          <option value="both">All Games</option>
          <option value="upcoming">Upcoming</option>
          <option value="current">Current (Last 6 Months)</option>
        </select>

        <select
          value={localFilters.genres}
          onChange={(e) => handleChange('genres', e.target.value)}
          className="filter-select"
        >
          <option value="">All Genres</option>
          {genres.map(genre => (
            <option key={genre.id} value={genre.slug}>
              {genre.name}
            </option>
          ))}
        </select>

        <select
          value={localFilters.platforms}
          onChange={(e) => handleChange('platforms', e.target.value)}
          className="filter-select"
        >
          <option value="">All Platforms</option>
          {platforms.map(platform => (
            <option key={platform.id} value={platform.id}>
              {platform.name}
            </option>
          ))}
        </select>
      </div>

      <div className="filter-actions">
        <button onClick={handleSearch} className="btn-search">
          Search
        </button>
        <button onClick={handleReset} className="btn-reset">
          Reset
        </button>
      </div>
    </div>
  );
}

export default FilterBar;
