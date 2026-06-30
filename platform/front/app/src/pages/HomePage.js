// fichier : platform/front/app/src/pages/HomePage.js

import { useNavigate } from 'react-router-dom';
import './HomePage.css';
import { useEffect } from 'react';
import { getHealth } from '../services/api';

export default function HomePage() {
  const navigate = useNavigate();

  useEffect(() => {
    getHealth()
      .then(res => console.log('✅ API connectée :', res.data))
      .catch(err => console.error('❌ API indisponible :', err.message));
  }, []);

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
          <button type="button" className="home-page__btn--ia" onClick={() => navigate('/interne/IA')}>
            IA
          </button>
        </div>
      </div>
    </div>
  );
}