import { useNavigate } from 'react-router';
import './HomePage.css';

export default function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="home-page">
      <div className="home-page__content">
        <p className="home-page__subtitle">Bienvenue sur</p>
        <h1>ObRail Europe</h1>
        <div className="home-page__actions">
          <button type="button" onClick={() => navigate('/externe/HomePage')}>
            Client
          </button>
          <button type="button" onClick={() => navigate('/interne/HomePage')}>
            Admin
          </button>
        </div>
      </div>
    </div>
  );
}
