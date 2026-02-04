import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Navbar.css';

function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/dashboard" className="navbar-brand">
          <h2>GameScout</h2>
        </Link>

        <div className="navbar-links">
          <Link 
            to="/dashboard" 
            className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
          >
            Discover
          </Link>
          <Link 
            to="/dashboard/recommendations" 
            className={`nav-link ${isActive('/dashboard/recommendations') ? 'active' : ''}`}
          >
            Recommendations
          </Link>
          <Link 
            to="/dashboard/wishlist" 
            className={`nav-link ${isActive('/dashboard/wishlist') ? 'active' : ''}`}
          >
            Collection
          </Link>
        </div>

        <div className="navbar-user">
          <span className="username">👤 {user?.username}</span>
          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
