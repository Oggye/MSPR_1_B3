import { useEffect, useState, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import MarkerClusterGroup from 'react-leaflet-markercluster';
import L from 'leaflet';
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
import { Bar } from 'react-chartjs-2';
import { getNightTrains, getCountries } from '../../services/api';
import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import './css/MapPage.css';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

// Correction des icônes Leaflet par défaut
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Icônes personnalisées pour les différents types de trains
const nightTrainIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-violet.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const dayTrainIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const MAX_TRAINS_TOTAL = 1000;
const MAX_TRAINS_PER_TYPE = 500;

// Composant pour recentrer la carte
function ChangeView({ center, zoom }) {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}

// Coordonnées centrales par pays (utilisées pour le clustering)
const countryCoords = {
  'FR': [46.603354, 1.888334],
  'DE': [51.165691, 10.451526],
  'IT': [41.87194, 12.56738],
  'ES': [40.463667, -3.74922],
  'GB': [55.378051, -3.435973],
  'CH': [46.818188, 8.227512],
  'AT': [47.516231, 14.550072],
  'PL': [51.919438, 19.145136],
  'UA': [48.379433, 31.16558],
  'RO': [45.943161, 24.96676],
  'NL': [52.132633, 5.291266],
  'BE': [50.503887, 4.469936],
  'SE': [60.128161, 18.643501],
  'NO': [60.472024, 8.468946],
  'DK': [56.26392, 9.501785],
  'CZ': [49.817492, 15.472962],
  'HU': [47.162494, 19.503304],
  'SK': [48.669026, 19.699024],
  'SI': [46.151241, 14.995463],
  'HR': [45.1, 15.2]
};

const MapPage = () => {
  const [trains, setTrains] = useState([]);
  const [filteredTrains, setFilteredTrains] = useState([]);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    trainType: 'all', // 'all', 'night', 'day'
    country: 'all',
    year: 'all'
  });
  const [availableYears, setAvailableYears] = useState([]);
  const mapCenter = [48.8566, 2.3522]; // Paris
  const mapZoom = 5;

  const applyFilters = useCallback(() => {
    let filtered = [...trains];
    
    if (filters.trainType === 'night') {
      filtered = filtered.filter(train => train.is_night === true);
    } else if (filters.trainType === 'day') {
      filtered = filtered.filter(train => train.is_night === false);
    }
    
    if (filters.country !== 'all') {
      filtered = filtered.filter(train => train.country_code === filters.country);
    }
    
    if (filters.year !== 'all') {
      filtered = filtered.filter(train => train.year === parseInt(filters.year));
    }

    if (filters.trainType === 'night') {
      filtered = filtered.slice(0, MAX_TRAINS_PER_TYPE);
    } else if (filters.trainType === 'day') {
      filtered = filtered.slice(0, MAX_TRAINS_PER_TYPE);
    } else {
      const nightTrains = filtered.filter(train => train.is_night).slice(0, MAX_TRAINS_PER_TYPE);
      const dayTrains = filtered.filter(train => !train.is_night).slice(0, MAX_TRAINS_PER_TYPE);
      const combined = [...nightTrains, ...dayTrains];

      if (combined.length < MAX_TRAINS_TOTAL) {
        const remainingNeeded = MAX_TRAINS_TOTAL - combined.length;
        const remainingNight = filtered.filter(train => train.is_night).slice(MAX_TRAINS_PER_TYPE);
        const remainingDay = filtered.filter(train => !train.is_night).slice(MAX_TRAINS_PER_TYPE);
        filtered = [...combined, ...remainingNight, ...remainingDay].slice(0, combined.length + remainingNeeded);
      } else {
        filtered = combined.slice(0, MAX_TRAINS_TOTAL);
      }
    }

    setFilteredTrains(filtered);
  }, [trains, filters]);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [filters, trains, applyFilters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [trainsRes, countriesRes] = await Promise.all([
        getNightTrains(),
        getCountries()
      ]);
      
      setTrains(trainsRes.data);
      setFilteredTrains(trainsRes.data);
      setCountries(countriesRes.data);
      
      // Extraire les années disponibles
      const years = [...new Set(trainsRes.data.map(train => train.year))].sort();
      setAvailableYears(years);
      
    } catch (error) {
      console.error("Erreur lors du chargement des données:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters({
      trainType: 'all',
      country: 'all',
      year: 'all'
    });
  };

  // Préparer les données pour le graphique à barres
  const getBarChartData = () => {
    const countryCounts = {};
    filteredTrains.forEach(train => {
      const countryName = train.country_name;
      if (!countryCounts[countryName]) {
        countryCounts[countryName] = { night: 0, day: 0, total: 0 };
      }
      if (train.is_night) {
        countryCounts[countryName].night++;
      } else {
        countryCounts[countryName].day++;
      }
      countryCounts[countryName].total++;
    });
    
    const sortedCountries = Object.keys(countryCounts).sort();
    
    return {
      labels: sortedCountries,
      datasets: [
        {
          label: 'Trains de Nuit',
          data: sortedCountries.map(c => countryCounts[c].night),
          backgroundColor: 'rgba(156, 39, 176, 0.7)',
          borderColor: 'rgba(156, 39, 176, 1)',
          borderWidth: 1,
          borderRadius: 5,
        },
        {
          label: 'Trains de Jour',
          data: sortedCountries.map(c => countryCounts[c].day),
          backgroundColor: 'rgba(33, 150, 243, 0.7)',
          borderColor: 'rgba(33, 150, 243, 1)',
          borderWidth: 1,
          borderRadius: 5,
        }
      ]
    };
  };

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 12 }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            let value = context.raw;
            return `${label}: ${value} train(s)`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Nombre de trains',
          font: { size: 12 }
        },
        ticks: {
          stepSize: 1
        }
      },
      x: {
        title: {
          display: true,
          text: 'Pays',
          font: { size: 12 }
        },
        ticks: {
          rotate: 45,
          autoSkip: true,
          maxRotation: 45,
          minRotation: 45
        }
      }
    }
  };

  // Calculer les statistiques
  const stats = {
    total: filteredTrains.length,
    night: filteredTrains.filter(t => t.is_night).length,
    day: filteredTrains.filter(t => !t.is_night).length,
    countries: new Set(filteredTrains.map(t => t.country_code)).size
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement de la carte et des données...</p>
      </div>
    );
  }

  return (
    <div className="train-map-page">
      <header className="map-header">
        <h1>🗺️ Carte Interactive des Trains Européens</h1>
        <p>Visualisez tous les trains de jour et de nuit à travers l'Europe</p>
      </header>

      {/* Section Filtres */}
      <div className="filters-section">
        <div className="filters-container">
          <div className="filter-group-map">
            <label>🚆 Type de train :</label>
            <select 
              value={filters.trainType}
              onChange={(e) => handleFilterChange('trainType', e.target.value)}
              className="filter-select"
            >
              <option value="all">Tous les trains</option>
              <option value="night">🌙 Trains de nuit</option>
              <option value="day">☀️ Trains de jour</option>
            </select>
          </div>

          <div className="filter-group-map">
            <label>🌍 Pays :</label>
            <select 
              value={filters.country}
              onChange={(e) => handleFilterChange('country', e.target.value)}
              className="filter-select"
            >
              <option value="all">Tous les pays</option>
              {countries.map(country => (
                <option key={country.country_code} value={country.country_code}>
                  {country.country_name}
                </option>
              ))}
            </select>
          </div>

          <div className="filter-group-map">
            <label>📅 Année :</label>
            <select 
              value={filters.year}
              onChange={(e) => handleFilterChange('year', e.target.value)}
              className="filter-select"
            >
              <option value="all">Toutes les années</option>
              {availableYears.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>

          <button onClick={resetFilters} className="reset-btn">
            🔄 Réinitialiser
          </button>
        </div>

        {/* Statistiques des filtres */}
        <div className="stats-cards">
          <div className="stat-card">
            <span className="stat-icon">🚆</span>
            <div className="stat-info">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label-map">Trains trouvés</div>
            </div>
          </div>
          <div className="stat-card night">
            <span className="stat-icon">🌙</span>
            <div className="stat-info">
              <div className="stat-value">{stats.night}</div>
              <div className="stat-label-map">Trains de nuit</div>
            </div>
          </div>
          <div className="stat-card day">
            <span className="stat-icon">☀️</span>
            <div className="stat-info">
              <div className="stat-value">{stats.day}</div>
              <div className="stat-label-map">Trains de jour</div>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">🌍</span>
            <div className="stat-info">
              <div className="stat-value">{stats.countries}</div>
              <div className="stat-label-map">Pays couverts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Carte Interactive avec clustering */}
      <div className="map-container">
        <MapContainer 
          center={mapCenter} 
          zoom={mapZoom} 
          style={{ height: '500px', width: '100%', borderRadius: '10px' }}
        >
          <ChangeView center={mapCenter} zoom={mapZoom} />
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />
          
          <MarkerClusterGroup chunkedLoading>
            {filteredTrains.map((train) => {
              const coords = countryCoords[train.country_code] || [48.8566, 2.3522];
              return (
                <Marker 
                  key={train.fact_id}
                  position={coords}
                  icon={train.is_night ? nightTrainIcon : dayTrainIcon}
                >
                  <Popup>
                    <div className="popup-content">
                      <h3>{train.country_name}</h3>
                      <p><strong>Opérateur :</strong> {train.operator_name}</p>
                      <p><strong>Type :</strong> {train.is_night ? '🌙 Train de nuit' : '☀️ Train de jour'}</p>
                      <p><strong>Année :</strong> {train.year}</p>
                      {train.distance_km && <p><strong>Distance :</strong> {train.distance_km} km</p>}
                      {train.duration_min && (
                        <p><strong>Durée :</strong> {Math.floor(train.duration_min / 60)}h {train.duration_min % 60}m</p>
                      )}
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MarkerClusterGroup>
        </MapContainer>
        
        <div className="map-legend">
          <div className="legend-item">
            <div className="legend-marker night-marker"></div>
            <span>Train de nuit</span>
          </div>
          <div className="legend-item">
            <div className="legend-marker day-marker"></div>
            <span>Train de jour</span>
          </div>
        </div>
      </div>

      {/* Graphique à barres */}
      <div className="chart-section">
        <h2>📊 Nombre de trains par pays</h2>
        <div className="chart-container">
          {filteredTrains.length > 0 ? (
            <Bar data={getBarChartData()} options={barChartOptions} />
          ) : (
            <div className="no-data-message">
              <p>Aucun train ne correspond aux filtres sélectionnés</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapPage;