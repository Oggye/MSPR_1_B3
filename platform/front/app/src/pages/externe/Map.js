import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
} from 'chart.js';
import { Bar, Scatter } from 'react-chartjs-2';
import { getNightTrains, getCountries } from '../../services/api';
import './MapPage.css';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
);

const MapPage = () => {
  const [trains, setTrains] = useState([]);
  const [filteredTrains, setFilteredTrains] = useState([]);
  const [countries, setCountries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    trainType: 'all',
    country: 'all',
    year: 'all'
  });
  const [availableYears, setAvailableYears] = useState([]);

  // Coordonnées approximatives des pays européens
  const countryCoordinates = {
    'FR': { lat: 46.603354, lon: 1.888334, name: 'France' },
    'DE': { lat: 51.165691, lon: 10.451526, name: 'Allemagne' },
    'IT': { lat: 41.87194, lon: 12.56738, name: 'Italie' },
    'ES': { lat: 40.463667, lon: -3.74922, name: 'Espagne' },
    'GB': { lat: 55.378051, lon: -3.435973, name: 'Royaume-Uni' },
    'CH': { lat: 46.818188, lon: 8.227512, name: 'Suisse' },
    'AT': { lat: 47.516231, lon: 14.550072, name: 'Autriche' },
    'PL': { lat: 51.919438, lon: 19.145136, name: 'Pologne' },
    'UA': { lat: 48.379433, lon: 31.16558, name: 'Ukraine' },
    'RO': { lat: 45.943161, lon: 24.96676, name: 'Roumanie' },
    'NL': { lat: 52.132633, lon: 5.291266, name: 'Pays-Bas' },
    'BE': { lat: 50.503887, lon: 4.469936, name: 'Belgique' },
    'SE': { lat: 60.128161, lon: 18.643501, name: 'Suède' },
    'NO': { lat: 60.472024, lon: 8.468946, name: 'Norvège' },
    'DK': { lat: 56.26392, lon: 9.501785, name: 'Danemark' },
    'CZ': { lat: 49.817492, lon: 15.472962, name: 'République Tchèque' },
    'HU': { lat: 47.162494, lon: 19.503304, name: 'Hongrie' },
    'SK': { lat: 48.669026, lon: 19.699024, name: 'Slovaquie' },
    'SI': { lat: 46.151241, lon: 14.995463, name: 'Slovénie' },
    'HR': { lat: 45.1, lon: 15.2, name: 'Croatie' },
    'PT': { lat: 39.399872, lon: -8.224454, name: 'Portugal' },
    'GR': { lat: 39.074208, lon: 21.824312, name: 'Grèce' },
    'BG': { lat: 42.733883, lon: 25.48583, name: 'Bulgarie' },
    'FI': { lat: 61.92411, lon: 25.748151, name: 'Finlande' },
    'IE': { lat: 53.41291, lon: -8.24389, name: 'Irlande' }
  };

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [filters, trains]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [trainsRes, countriesRes] = await Promise.all([
        getNightTrains({ limit: 500 }),
        getCountries()
      ]);
      
      setTrains(trainsRes.data);
      setFilteredTrains(trainsRes.data);
      setCountries(countriesRes.data);
      
      const years = [...new Set(trainsRes.data.map(train => train.year))].sort();
      setAvailableYears(years);
      
    } catch (error) {
      console.error("Erreur:", error);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
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
    
    setFilteredTrains(filtered);
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters({ trainType: 'all', country: 'all', year: 'all' });
  };

  // Préparer les données pour le scatter plot (carte)
  const getScatterData = () => {
    const countryStats = {};
    
    filteredTrains.forEach(train => {
      const code = train.country_code;
      if (!countryStats[code]) {
        countryStats[code] = { night: 0, day: 0, total: 0 };
      }
      if (train.is_night) {
        countryStats[code].night++;
      } else {
        countryStats[code].day++;
      }
      countryStats[code].total++;
    });
    
    const nightData = [];
    const dayData = [];
    
    Object.keys(countryStats).forEach(code => {
      const coords = countryCoordinates[code];
      if (coords) {
        nightData.push({
          x: coords.lon,
          y: coords.lat,
          r: Math.sqrt(countryStats[code].night) * 5,
          count: countryStats[code].night,
          country: coords.name,
          type: 'night'
        });
        dayData.push({
          x: coords.lon,
          y: coords.lat,
          r: Math.sqrt(countryStats[code].day) * 5,
          count: countryStats[code].day,
          country: coords.name,
          type: 'day'
        });
      }
    });
    
    return { nightData, dayData };
  };

  const scatterData = getScatterData();
  
  const chartData = {
    datasets: [
      {
        label: 'Trains de Nuit',
        data: scatterData.nightData,
        backgroundColor: 'rgba(156, 39, 176, 0.7)',
        borderColor: 'rgba(156, 39, 176, 1)',
        borderWidth: 2,
        pointRadius: (ctx) => {
          const value = ctx.raw;
          return value ? Math.min(value.r, 30) : 5;
        },
        pointHoverRadius: (ctx) => {
          const value = ctx.raw;
          return value ? Math.min(value.r + 5, 35) : 10;
        }
      },
      {
        label: 'Trains de Jour',
        data: scatterData.dayData,
        backgroundColor: 'rgba(33, 150, 243, 0.7)',
        borderColor: 'rgba(33, 150, 243, 1)',
        borderWidth: 2,
        pointRadius: (ctx) => {
          const value = ctx.raw;
          return value ? Math.min(value.r, 30) : 5;
        },
        pointHoverRadius: (ctx) => {
          const value = ctx.raw;
          return value ? Math.min(value.r + 5, 35) : 10;
        }
      }
    ]
  };

  const scatterOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      tooltip: {
        callbacks: {
          label: function(context) {
            const dataPoint = context.raw;
            return [
              `${dataPoint.country}`,
              `${context.dataset.label}: ${dataPoint.count} train(s)`,
              `Taille du cercle = ${Math.round(dataPoint.r)} trains`
            ];
          }
        }
      },
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 12 }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Longitude',
          font: { size: 12 }
        },
        min: -15,
        max: 35,
        grid: {
          color: '#e0e0e0',
          borderDash: [5, 5]
        }
      },
      y: {
        title: {
          display: true,
          text: 'Latitude',
          font: { size: 12 }
        },
        min: 35,
        max: 70,
        grid: {
          color: '#e0e0e0',
          borderDash: [5, 5]
        }
      }
    }
  };

  // Données pour le graphique à barres
  const getBarChartData = () => {
    const countryCounts = {};
    filteredTrains.forEach(train => {
      const countryName = train.country_name;
      if (!countryCounts[countryName]) {
        countryCounts[countryName] = { night: 0, day: 0 };
      }
      if (train.is_night) {
        countryCounts[countryName].night++;
      } else {
        countryCounts[countryName].day++;
      }
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
        labels: { usePointStyle: true, padding: 15, font: { size: 12 } }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.raw} train(s)`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'Nombre de trains', font: { size: 12 } },
        ticks: { stepSize: 1 }
      },
      x: {
        title: { display: true, text: 'Pays', font: { size: 12 } },
        ticks: { rotate: 45, autoSkip: true, maxRotation: 45, minRotation: 45 }
      }
    }
  };

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
        <p>Chargement des données...</p>
      </div>
    );
  }

  return (
    <div className="train-map-page">
      <header className="map-header">
        <h1>🗺️ Carte des Trains Européens</h1>
        <p>Visualisation géographique avec des cercles proportionnels</p>
      </header>

      {/* Filtres */}
      <div className="filters-section">
        <div className="filters-container">
          <div className="filter-group">
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

          <div className="filter-group">
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

          <div className="filter-group">
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

        {/* Statistiques */}
        <div className="stats-cards">
          <div className="stat-card">
            <span className="stat-icon">🚆</span>
            <div className="stat-info">
              <div className="stat-value">{stats.total}</div>
              <div className="stat-label">Trains trouvés</div>
            </div>
          </div>
          <div className="stat-card night">
            <span className="stat-icon">🌙</span>
            <div className="stat-info">
              <div className="stat-value">{stats.night}</div>
              <div className="stat-label">Trains de nuit</div>
            </div>
          </div>
          <div className="stat-card day">
            <span className="stat-icon">☀️</span>
            <div className="stat-info">
              <div className="stat-value">{stats.day}</div>
              <div className="stat-label">Trains de jour</div>
            </div>
          </div>
          <div className="stat-card">
            <span className="stat-icon">🌍</span>
            <div className="stat-info">
              <div className="stat-value">{stats.countries}</div>
              <div className="stat-label">Pays couverts</div>
            </div>
          </div>
        </div>
      </div>

      {/* Carte avec Scatter Plot */}
      <div className="map-container">
        <h3>📍 Carte géographique (taille des cercles = nombre de trains)</h3>
        <div className="scatter-chart-container">
          <Scatter data={chartData} options={scatterOptions} />
        </div>
        <div className="map-legend">
          <div className="legend-item">
            <div className="legend-color night"></div>
            <span>Train de nuit</span>
          </div>
          <div className="legend-item">
            <div className="legend-color day"></div>
            <span>Train de jour</span>
          </div>
          <div className="legend-note">
            💡 La taille du cercle représente le nombre de trains
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
              <p>Aucun train ne correspond aux filtres</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MapPage;