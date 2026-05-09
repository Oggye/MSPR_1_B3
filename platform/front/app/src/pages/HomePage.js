import { useNavigate } from 'react-router-dom';
import './HomePage.css';
import { useEffect } from 'react';
import { getHealth } from '../services/api';

export default function HomePage() {
  const navigate = useNavigate();
  // useEffect s'exécute une fois au chargement de la page
  useEffect(() => {
    // J'appelle getHealth() qui va checker l'API
    getHealth()
      // Si ça réussit, j'affiche un message vert dans la console
      .then(res => console.log('✅ API connectée :', res.data))
      // Si ça échoue, j'affiche une erreur rouge
      .catch(err => console.error('❌ API indisponible :', err.message));
  }, []); // Le [] vide = "exécute cette fonction une seule fois"

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
