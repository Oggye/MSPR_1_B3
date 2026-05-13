import React, { useState, useEffect, useCallback } from 'react';
import {
  getNightTrains,
  getNightTrainsOnly,
  getDayTrainsOnly,
  getCountries
} from '../../services/api';
import './css/TrajetsPage.css';

const TrainPage = () => {
  // États pour les filtres
  const [countries, setCountries] = useState([]);
  const [trains, setTrains] = useState([]);
  const [filteredTrains, setFilteredTrains] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // États des sélections
  const [operatorSearch, setOperatorSearch] = useState('');
  const [departureCountry, setDepartureCountry] = useState('');
  const [arrivalCountry, setArrivalCountry] = useState('');
  const [trainType, setTrainType] = useState('all'); // 'all', 'night', 'day'
  
  // État pour l'itinéraire sélectionné
  const [selectedRoute, setSelectedRoute] = useState(null);

  const loadCountries = useCallback(async () => {
    try {
      const response = await getCountries();
      setCountries(response.data || []);
    } catch (err) {
      console.error('Erreur chargement pays:', err);
      setError('Impossible de charger la liste des pays');
    }
  }, []);

  const loadTrains = useCallback(async () => {
    setLoading(true);
    try {
      let response;
      if (trainType === 'night') {
        response = await getNightTrainsOnly();
      } else if (trainType === 'day') {
        response = await getDayTrainsOnly();
      } else {
        response = await getNightTrains();
      }
      
      let trainsData = response.data || [];
      
      // Ajout de données simulées pour l'exemple (car votre API semble avoir des trajets par pays)
      // Dans une vraie implémentation, vous feriez une requête plus spécifique
      trainsData = trainsData.map(train => ({
        ...train,
        // Simulation de données d'itinéraire basées sur le pays
        estimated_duration: Math.floor(Math.random() * 600) + 60, // minutes
        estimated_distance: Math.floor(Math.random() * 1500) + 100, // km
        departure_station: `${train.country_name} Centrale`,
        arrival_station: `Gare Principale`,
        intermediate_stops: [
          { city: `Ville 1`, duration_min: 45, distance_km: 80 },
          { city: `Ville 2`, duration_min: 60, distance_km: 120 }
        ]
      }));
      
      setTrains(trainsData);
      setError(null);
    } catch (err) {
      console.error('Erreur chargement trains:', err);
      setError('Erreur lors du chargement des trains');
    } finally {
      setLoading(false);
    }
  }, [trainType]);

  const filterTrains = useCallback(() => {
    let filtered = [...trains];
    
    // Filtre par pays de départ
    if (departureCountry) {
      filtered = filtered.filter(train => 
        train.country_code === departureCountry || 
        train.country_name?.toLowerCase().includes(departureCountry.toLowerCase())
      );
    }
    
    // Filtre par pays d'arrivée
    if (arrivalCountry) {
      filtered = filtered.filter(train =>
        train.arrival_country === arrivalCountry ||
        train.country_name?.toLowerCase().includes(arrivalCountry.toLowerCase())
      );
    }
    
    // Filtre par nom d'operateur
    if (operatorSearch) {
      filtered = filtered.filter(train =>
        train.operator_name?.toLowerCase().includes(operatorSearch.toLowerCase())
      );
    }

    // Filtre par type de train
    if (trainType !== 'all') {
      filtered = filtered.filter(train => train.train_type === trainType);
    }
    
    setFilteredTrains(filtered);
  }, [trains, departureCountry, arrivalCountry, trainType, operatorSearch]);

  // Chargement des pays au montage
  useEffect(() => {
    loadCountries();
  }, [loadCountries]);

  useEffect(() => {
    loadTrains();
  }, [loadTrains]);

  // Filtrage des trains quand les critères changent
  useEffect(() => {
    filterTrains();
  }, [filterTrains]);

  const handleSelectRoute = (train) => {
    setSelectedRoute(train);
  };

  const formatDuration = (minutes) => {
    if (!minutes) return 'N/A';
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}min`;
  };

  const formatDistance = (km) => {
    if (!km) return 'N/A';
    return `${km} km`;
  };

  return (
    <div className="train-search-container">
      <h1>Recherche d'itinéraires ferroviaires</h1>
      
      {/* Panneau de filtres */}
      <div className="filters-panel">
        <div className="filter-group">
          <label>Operateur:</label>
          <input
            type="text"
            placeholder="Ecrire un operateur..."
            value={operatorSearch}
            onChange={(e) => setOperatorSearch(e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label>Pays de départ:</label>
          <select value={departureCountry} onChange={(e) => setDepartureCountry(e.target.value)}>
            <option value="">Tous les pays</option>
            {countries.map(country => (
              <option key={country.country_id} value={country.country_code}>
                {country.country_name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Pays d'arrivée:</label>
          <select value={arrivalCountry} onChange={(e) => setArrivalCountry(e.target.value)}>
            <option value="">Tous les pays</option>
            {countries.map(country => (
              <option key={country.country_id} value={country.country_code}>
                {country.country_name}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Type de train:</label>
          <div className="radio-group">
            <label>
              <input
                type="radio"
                value="all"
                checked={trainType === 'all'}
                onChange={(e) => setTrainType(e.target.value)}
              />
              Tous
            </label>
            <label>
              <input
                type="radio"
                value="night"
                checked={trainType === 'night'}
                onChange={(e) => setTrainType(e.target.value)}
              />
              Train de nuit
            </label>
            <label>
              <input
                type="radio"
                value="day"
                checked={trainType === 'day'}
                onChange={(e) => setTrainType(e.target.value)}
              />
              Train de jour
            </label>
          </div>
        </div>

        <button onClick={loadTrains} className="refresh-btn">
          🔄 Actualiser
        </button>
      </div>

      {/* Résultats de recherche */}
      <div className="results-container">
        <div className="trains-list">
          <h2>Trajets disponibles ({filteredTrains.length})</h2>
          {loading && <div className="loading">Chargement...</div>}
          {error && <div className="error">{error}</div>}
          
          {!loading && !error && filteredTrains.length === 0 && (
            <div className="no-results">Aucun trajet trouvé</div>
          )}
          
          <div className="train-cards">
            {filteredTrains.map(train => (
              <div 
                key={train.fact_id} 
                className={`train-card ${selectedRoute?.fact_id === train.fact_id ? 'selected' : ''}`}
                onClick={() => handleSelectRoute(train)}
              >
                <div className="train-header">
                  <span className="train-type-badge" data-type={train.train_type}>
                    {train.train_type === 'night' ? '🌙 Nuit' : '☀️ Jour'}
                  </span>
                  <span className="train-id">ID: {train.fact_id}</span>
                </div>
                <div className="train-body">
                  <div className="train-info">
                    <strong>{train.operator_name}</strong>
                    <div>📍 {train.country_name}</div>
                    <div>📅 Année: {train.year}</div>
                  </div>
                  <div className="route-preview">
                    <div>🚆 Distance: {formatDistance(train.estimated_distance)}</div>
                    <div>⏱️ Durée: {formatDuration(train.estimated_duration)}</div>
                  </div>
                </div>
                <button className="select-btn">Voir l'itinéraire</button>
              </div>
            ))}
          </div>
        </div>

        {/* Affichage de l'itinéraire détaillé */}
        <div className="route-details">
          {selectedRoute ? (
            <div className="itinerary">
              <h2>🗺️ Itinéraire détaillé</h2>
              <div className="route-summary">
                <div className="summary-item">
                  <span className="label">Train:</span>
                  <span className="value">{selectedRoute.operator_name}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Type:</span>
                  <span className="value">{selectedRoute.train_type === 'night' ? 'Train de nuit' : 'Train de jour'}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Pays:</span>
                  <span className="value">{selectedRoute.country_name}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Distance totale:</span>
                  <span className="value">{formatDistance(selectedRoute.estimated_distance)}</span>
                </div>
                <div className="summary-item">
                  <span className="label">Durée totale:</span>
                  <span className="value">{formatDuration(selectedRoute.estimated_duration)}</span>
                </div>
              </div>

              {/* Informations supplémentaires */}
              <div className="additional-info">
                <h3>ℹ️ Informations supplémentaires</h3>
                <div className="info-grid">
                  <div className="info-item">
                    <strong>Opérateur:</strong> {selectedRoute.operator_name}
                  </div>
                  <div className="info-item">
                    <strong>Année de service:</strong> {selectedRoute.year}
                  </div>
                  {selectedRoute.distance_km && (
                    <div className="info-item">
                      <strong>Distance officielle:</strong> {formatDistance(selectedRoute.distance_km)}
                    </div>
                  )}
                  {selectedRoute.duration_min && (
                    <div className="info-item">
                      <strong>Durée officielle:</strong> {formatDuration(selectedRoute.duration_min)}
                    </div>
                  )}
                </div>
              </div>
            </div>
          ) : (
            <div className="no-route-selected">
              <div className="placeholder-icon">🚆</div>
              <p>Sélectionnez un trajet dans la liste<br/>pour voir l'itinéraire détaillé</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default TrainPage;
