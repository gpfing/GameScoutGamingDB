import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './PreferenceBar.css';

function PreferenceBar({ user, onPreferencesUpdate }) {
  const { updatePreferences } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  
  const genres = ['Action', 'Adventure', 'RPG', 'Shooter', 'Strategy', 'Indie', 'Simulation', 'Sports', 'Racing', 'Platformer'];
  const platforms = ['PC', 'PlayStation 5', 'PlayStation 4', 'Xbox Series X/S', 'Xbox One', 'Nintendo Switch'];
  
  // Helper function to capitalize first letter
  const capitalize = (str) => str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  
  // Initialize with valid limits and normalize case: max 2 genres, 1 platform
  const initGenres = (user?.favorite_genres || []).map(g => {
    // Try to match with proper capitalization
    const normalized = capitalize(g);
    return genres.find(genre => genre.toLowerCase() === g.toLowerCase()) || normalized;
  }).slice(0, 2);
  
  const initPlatforms = (user?.favorite_platforms || []).slice(0, 1);
  
  const [selectedGenres, setSelectedGenres] = useState(initGenres);
  const [selectedPlatforms, setSelectedPlatforms] = useState(initPlatforms);
  const [saving, setSaving] = useState(false);

  const toggleGenre = (genre) => {
    setSelectedGenres(prev => {
      if (prev.includes(genre)) {
        return prev.filter(g => g !== genre);
      } else if (prev.length < 2) {
        return [...prev, genre];
      }
      return prev; // Max 2 genres
    });
  };

  const selectPlatform = (platform) => {
    setSelectedPlatforms([platform]); // Only one platform
  };

  const handleSave = async () => {
    setSaving(true);
    await updatePreferences(selectedGenres, selectedPlatforms);
    setSaving(false);
    setIsEditing(false);
    // Refresh recommendations after saving
    if (onPreferencesUpdate) {
      onPreferencesUpdate();
    }
  };

  const handleCancel = () => {
    // Reset to current limited preferences with normalized case
    const initGenres = (user?.favorite_genres || []).map(g => {
      const normalized = capitalize(g);
      return genres.find(genre => genre.toLowerCase() === g.toLowerCase()) || normalized;
    }).slice(0, 2);
    const initPlatforms = (user?.favorite_platforms || []).slice(0, 1);
    setSelectedGenres(initGenres);
    setSelectedPlatforms(initPlatforms);
    setIsEditing(false);
  };

  if (!isEditing) {
    return (
      <div className="preference-bar">
        <div className="preference-display">
          <div>
            <strong>Genres:</strong>{' '}
            {user?.favorite_genres && user.favorite_genres.length > 0
              ? user.favorite_genres.join(', ')
              : 'None selected'}
          </div>
          <div>
            <strong>Platforms:</strong>{' '}
            {user?.favorite_platforms && user.favorite_platforms.length > 0
              ? user.favorite_platforms.join(', ')
              : 'None selected'}
          </div>
        </div>
        <button onClick={() => setIsEditing(true)} className="btn-edit">
          Edit Preferences
        </button>
      </div>
    );
  }

  return (
    <div className="preference-bar editing">
      <div className="preference-section">
        <label>Favorite Genres (Choose up to 2)</label>
        <div className="chips-container">
          {genres.map(genre => (
            <button
              key={genre}
              type="button"
              className={`chip ${selectedGenres.includes(genre) ? 'selected' : ''}`}
              onClick={() => toggleGenre(genre)}
              disabled={!selectedGenres.includes(genre) && selectedGenres.length >= 2}
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      <div className="preference-section">
        <label>Favorite Platform (Choose 1)</label>
        <div className="chips-container">
          {platforms.map(platform => (
            <button
              key={platform}
              type="button"
              className={`chip ${selectedPlatforms.includes(platform) ? 'selected' : ''}`}
              onClick={() => selectPlatform(platform)}
            >
              {platform}
            </button>
          ))}
        </div>
      </div>

      <div className="preference-actions">
        <button onClick={handleSave} className="btn-save" disabled={saving}>
          {saving ? 'Saving...' : 'Save'}
        </button>
        <button onClick={handleCancel} className="btn-cancel" disabled={saving}>
          Cancel
        </button>
      </div>
    </div>
  );
}

export default PreferenceBar;
