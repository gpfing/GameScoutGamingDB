import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import './Dashboard.css';

function Dashboard() {
  return (
    <div className="dashboard">
      <Navbar />
      <main className="dashboard-content">
        <Outlet />
      </main>
    </div>
  );
}

export default Dashboard;
