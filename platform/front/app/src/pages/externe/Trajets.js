// src/pages/TrainSearchPage.jsx
import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';
import { getNightTrains, getCountries, getOperators } from '../../services/api';
import './TrajetsPage.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const TrainPage = () => {
  const [trains, setTrains] = useState([]);
  const [filteredTrains, setFilteredTrains] = useState([]);
  const [selectedItinerary, setSelectedItinerary] = useState(null);
  const [countries, setCountries] = useState([]);
  const [operators, setOperators] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchParams, setSearchParams] = useState({
    country_depart: '',
    country_arrival: '',
    train_type: 'all',
    operator_id: ''
  });

  useEffect(() => {
    fetchInitialData();
  }, []);

  useEffect(() => {
    if (trains.length > 0) {
      performSearch();
    }
  }, [searchParams, trains]);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [trainsRes, countriesRes, operatorsRes] = await Promise.all([
        getNightTrains({ limit: 1000 }),
        getCountries(),
        getOperators()
      ]);
      
      setTrains(trainsRes.data);
      setCountries(countriesRes.data);
      setOperators(operatorsRes.data);
    } catch (error) {
      console.error("Erreur lors du chargement:", error);
    } finally {
      setLoading(false);
    }
  };

  const performSearch = () => {
    let filtered = [...trains];
    
    // Filtre par pays de départ
    if (searchParams.country_depart) {
      filtered = filtered.filter(train => 
        train.country_code === searchParams.country_depart
      );
    }
    
    // Filtre par pays d'arrivée (simulation - dans une vraie API, vous auriez un champ arrival_country)
    if (searchParams.country_arrival && searchParams.country_arrival !== searchParams.country_depart) {
      // Simulation : on garde les trains d'un pays différent
      filtered = filtered.filter(train => 
        train.country_code !== searchParams.country_arrival
      );
    }
    
    // Filtre par type de train
    if (searchParams.train_type === 'night') {
      filtered = filtered.filter(train => train.is_night === true);
    } else if (searchParams.train_type === 'day') {
      filtered = filtered.filter(train => train.is_night === false);
    }
    
    // Filtre par opérateur
    if (searchParams.operator_id) {
      filtered = filtered.filter(train => 
        train.operator_id === parseInt(searchParams.operator_id)
      );
    }
    
    setFilteredTrains(filtered);
  };

  const handleSearchChange = (key, value) => {
    setSearchParams(prev => ({ ...prev, [key]: value }));
    setSelectedItinerary(null);
  };

  const handleSelectTrain = (train) => {
    setSelectedItinerary(train);
  };

  const resetSearch = () => {
    setSearchParams({
      country_depart: '',
      country_arrival: '',
      train_type: 'all',
      operator_id: ''
    });
    setSelectedItinerary(null);
  };

  // Formater la durée
  const formatDuration = (minutes) => {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours === 0) return `${mins} min`;
    return `${hours}h ${mins > 0 ? `${mins}min` : ''}`;
  };

  // Formater la distance
  const formatDistance = (km) => {
    if (!km) return 'N/A';
    return `${km.toLocaleString()} km`;
  };

  // Statistiques des résultats
  const stats = {
    total: filteredTrains.length,
    night: filteredTrains.filter(t => t.is_night).length,
    day: filteredTrains.filter(t => !t.is_night).length,
    avgDistance: filteredTrains.reduce((acc, t) => acc + (t.distance_km || 0), 0) / (filteredTrains.length || 1),
    avgDuration: filteredTrains.reduce((acc, t) => acc + (t.duration_min || 0), 0) / (filteredTrains.length || 1)
  };

  // Données pour le graphique de distribution
  const distributionData = {
    labels: ['Trains disponibles', 'Trains sélectionnés'],
    datasets: [
      {
        label: 'Trains de Nuit',
        data: [
          trains.filter(t => t.is_night).length,
          filteredTrains.filter(t => t.is_night).length
        ],
        backgroundColor: ['rgba(156, 39, 176, 0.7)', 'rgba(156, 39, 176, 0.3)'],
        borderColor: 'rgba(156, 39, 176, 1)',
        borderWidth: 2,
      },
      {
        label: 'Trains de Jour',
        data: [
          trains.filter(t => !t.is_night).length,
          filteredTrains.filter(t => !t.is_night).length
        ],
        backgroundColor: ['rgba(33, 150, 243, 0.7)', 'rgba(33, 150, 243, 0.3)'],
        borderColor: 'rgba(33, 150, 243, 1)',
        borderWidth: 2,
      }
    ]
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { position: 'top' },
      tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${ctx.raw} trains` } }
    },
    scales: {
      y: { beginAtZero: true, title: { display: true, text: 'Nombre de trains' }, ticks: { stepSize: 1 } }
    }
  };

  return (
    <div className="train-search-page">
      <header className="search-header">
        <h1>🚆 Recherche d'Itinéraires Ferroviaires</h1>
        <p>Trouvez le trajet idéal entre deux pays européens</p>
      </header>

      <div className="search-layout">
        {/* Panneau de recherche */}
        <div className="search-panel">
          <div className="search-form">
            <h2>📋 Critères de recherche</h2>
            
            <div className="form-group">
              <label>🚉 Pays de départ :</label>
              <select
                value={searchParams.country_depart}
                onChange={(e) => handleSearchChange('country_depart', e.target.value)}
                className="form-select"
              >
                <option value="">Sélectionnez un pays</option>
                {countries.map(country => (
                  <option key={country.country_code} value={country.country_code}>
                    {country.country_name}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>🏁 Pays d'arrivée :</label>
              <select
                value={searchParams.country_arrival}
                onChange={(e) => handleSearchChange('country_arrival', e.target.value)}
                className="form-select"
                disabled={!searchParams.country_depart}
              >
                <option value="">Sélectionnez un pays</option>
                {countries
                  .filter(c => c.country_code !== searchParams.country_depart)
                  .map(country => (
                    <option key={country.country_code} value={country.country_code}>
                      {country.country_name}
                    </option>
                  ))}
              </select>
            </div>

            <div className="form-group">
              <label>🌙 Type de train :</label>
              <div className="radio-group">
                <label className="radio-label">
                  <input
                    type="radio"
                    value="all"
                    checked={searchParams.train_type === 'all'}
                    onChange={(e) => handleSearchChange('train_type', e.target.value)}
                  />
                  Tous
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    value="night"
                    checked={searchParams.train_type === 'night'}
                    onChange={(e) => handleSearchChange('train_type', e.target.value)}
                  />
                  🌙 Nuit
                </label>
                <label className="radio-label">
                  <input
                    type="radio"
                    value="day"
                    checked={searchParams.train_type === 'day'}
                    onChange={(e) => handleSearchChange('train_type', e.target.value)}
                  />
                  ☀️ Jour
                </label>
              </div>
            </div>

            <div className="form-group">
              <label>🏢 Opérateur :</label>
              <select
                value={searchParams.operator_id}
                onChange={(e) => handleSearchChange('operator_id', e.target.value)}
                className="form-select"
              >
                <option value="">Tous les opérateurs</option>
                {operators.map(operator => (
                  <option key={operator.operator_id} value={operator.operator_id}>
                    {operator.operator_name}
                  </option>
                ))}
              </select>
            </div>

            <button onClick={resetSearch} className="reset-btn">
              🔄 Réinitialiser
            </button>
          </div>

          {/* Résultats de recherche */}
          <div className="search-results">
            <h3>📊 Résultats ({filteredTrains.length} trajets)</h3>
            <div className="stats-mini">
              <div className="stat-mini">
                <span className="stat-mini-value">{stats.night}</span>
                <span className="stat-mini-label">Trains de nuit</span>
              </div>
              <div className="stat-mini">
                <span className="stat-mini-value">{stats.day}</span>
                <span className="stat-mini-label">Trains de jour</span>
              </div>
              <div className="stat-mini">
                <span className="stat-mini-value">{Math.round(stats.avgDistance)} km</span>
                <span className="stat-mini-label">Distance moyenne</span>
              </div>
            </div>

            <div className="trains-list">
              {filteredTrains.length > 0 ? (
                filteredTrains.map((train, index) => (
                  <div
                    key={train.fact_id || index}
                    className={`train-card ${selectedItinerary?.fact_id === train.fact_id ? 'selected' : ''}`}
                    onClick={() => handleSelectTrain(train)}
                  >
                    <div className="train-card-header">
                      <span className={`train-type-badge ${train.is_night ? 'night' : 'day'}`}>
                        {train.is_night ? '🌙 Nuit' : '☀️ Jour'}
                      </span>
                      <span className="train-operator">{train.operator_name}</span>
                    </div>
                    <div className="train-card-body">
                      <div className="train-route">
                        <span className="route-point">{train.country_name}</span>
                        <span className="route-arrow">→</span>
                        <span className="route-point">Destination</span>
                      </div>
                      <div className="train-details">
                        <span>📏 {formatDistance(train.distance_km)}</span>
                        <span>⏱️ {formatDuration(train.duration_min)}</span>
                        <span>📅 {train.year}</span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="no-results">
                  <p>Aucun trajet trouvé</p>
                  <p className="no-results-hint">Modifiez vos critères de recherche</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Panneau d'itinéraire */}
        <div className="itinerary-panel">
          {selectedItinerary ? (
            <div className="itinerary-container">
              <h2>🗺️ Itinéraire détaillé</h2>
              
              {/* Header du trajet */}
              <div className="itinerary-header">
                <div className="train-info-large">
                  <span className={`train-type-large ${selectedItinerary.is_night ? 'night' : 'day'}`}>
                    {selectedItinerary.is_night ? '🌙 Train de Nuit' : '☀️ Train de Jour'}
                  </span>
                  <span className="operator-name">{selectedItinerary.operator_name}</span>
                </div>
              </div>

              {/* Timeline du trajet */}
              <div className="journey-timeline">
                <div className="timeline-start">
                  <div className="timeline-dot start"></div>
                  <div className="timeline-content">
                    <div className="city-name">
                      {selectedItinerary.country_name}
                      <span className="country-code">({selectedItinerary.country_code})</span>
                    </div>
                  </div>
                </div>

                <div className="timeline-line">
                  <div className="timeline-progress"></div>
                </div>

                <div className="timeline-middle">
                  <div className="timeline-dot middle"></div>
                  <div className="timeline-content">
                    <div className="journey-info">
                      <div className="info-item">
                        <span className="info-icon">📏</span>
                        <span className="info-label">Distance totale</span>
                        <span className="info-value">{formatDistance(selectedItinerary.distance_km)}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-icon">⏱️</span>
                        <span className="info-label">Durée du trajet</span>
                        <span className="info-value">{formatDuration(selectedItinerary.duration_min)}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-icon">⚡</span>
                        <span className="info-label">Vitesse moyenne</span>
                        <span className="info-value">
                          {selectedItinerary.distance_km && selectedItinerary.duration_min
                            ? `${Math.round(selectedItinerary.distance_km / (selectedItinerary.duration_min / 60))} km/h`
                            : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="timeline-line">
                  <div className="timeline-progress"></div>
                </div>

                <div className="timeline-end">
                  <div className="timeline-dot end"></div>
                  <div className="timeline-content">
                    <div className="city-name">
                      Destination
                      <span className="country-code">(Arrivée)</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Informations supplémentaires */}
              <div className="additional-info">
                <h3>ℹ️ Informations complémentaires</h3>
                <div className="info-grid">
                  <div className="info-card">
                    <span className="info-card-icon">🎫</span>
                    <div>
                      <div className="info-card-label">Année</div>
                      <div className="info-card-value">{selectedItinerary.year}</div>
                    </div>
                  </div>
                  <div className="info-card">
                    <span className="info-card-icon">🚆</span>
                    <div>
                      <div className="info-card-label">Type de train</div>
                      <div className="info-card-value">
                        {selectedItinerary.night_train || (selectedItinerary.is_night ? 'Nightjet' : 'Regional Express')}
                      </div>
                    </div>
                  </div>
                  <div className="info-card">
                    <span className="info-card-icon">🌍</span>
                    <div>
                      <div className="info-card-label">Région</div>
                      <div className="info-card-value">Europe</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="no-itinerary">
              <div className="no-itinerary-icon">🗺️</div>
              <h3>Aucun itinéraire sélectionné</h3>
              <p>Cliquez sur un trajet dans la liste de gauche pour voir les détails</p>
              <p className="hint">Sélectionnez un pays de départ et d'arrivée pour commencer</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainPage;