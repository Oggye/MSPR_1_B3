import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { getOperators, getOperatorStats, getTrainsByOperator } from '../../services/api';

import './css/OperatorsPage.css';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement
);

export default function OperateurPage() {
  const [operators, setOperators] = useState([]);
  const [selectedOperator, setSelectedOperator] = useState(null);
  const [operatorDetails, setOperatorDetails] = useState(null);
  const [operatorTrains, setOperatorTrains] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);

  // Charger la liste des opérateurs au démarrage
  useEffect(() => {
    const fetchOperators = async () => {
      try {
        const response = await getOperators();
        console.log("Opérateurs reçus:", response.data);
        setOperators(response.data);
      } catch (error) {
        console.error("Erreur lors du chargement des opérateurs:", error);
      }
    };
    fetchOperators();
  }, []);

  // Fonction pour charger les détails d'un opérateur
  const handleSelectOperator = async (operatorId, operatorName) => {
    setLoading(true);
    setSelectedOperator({ id: operatorId, name: operatorName });
    
    try {
      const statsResponse = await getOperatorStats(operatorId);
      console.log("Stats opérateur:", statsResponse.data);
      setOperatorDetails(statsResponse.data);
      
      const trainsResponse = await getTrainsByOperator(operatorName);
      console.log("Trajets opérateur:", trainsResponse.data);
      setOperatorTrains(trainsResponse.data);
      
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Filtrer les opérateurs par recherche
  const filteredOperators = operators.filter(operator =>
    operator.operator_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Formater les nombres
  const formatNumber = (num) => {
    return num?.toLocaleString() || 0;
  };

  const formatDistance = (km) => {
    if (!km) return "0 km";
    return `${km.toLocaleString()} km`;
  };

  const formatDuration = (hours) => {
    if (!hours) return "N/A";
    const h = Math.floor(hours);
    const m = Math.round((hours - h) * 60);
    return `${h}h${m > 0 ? ` ${m}m` : ''}`;
  };

  // Préparer les données pour l'évolution temporelle (simulée)
  const getTimelineData = () => {
    if (!operatorTrains || operatorTrains.length === 0) return null;
    
    // Simuler des données par année basées sur les trajets
    const years = [2020, 2021, 2022, 2023, 2024];
    const nightCounts = years.map(() => Math.floor(Math.random() * 50) + 10);
    const dayCounts = years.map(() => Math.floor(Math.random() * 100) + 20);
    
    return {
      labels: years,
      datasets: [
        {
          label: 'Trains de Nuit',
          data: nightCounts,
          borderColor: '#12263a',
          backgroundColor: 'rgba(18, 38, 58, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: '#12263a',
        },
        {
          label: 'Trains de Jour',
          data: dayCounts,
          borderColor: '#1769aa',
          backgroundColor: 'rgba(23, 105, 170, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: '#1769aa',
        }
      ]
    };
  };

  const timelineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 11 }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.raw} trains`;
          }
        }
      }
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Nombre de trains',
          font: { size: 11 }
        },
        beginAtZero: true
      },
      x: {
        title: {
          display: true,
          text: 'Année',
          font: { size: 11 }
        }
      }
    }
  };

  return (
    <div className="operators-page">
      <h1 className="operators-page-title">🚆 Opérateurs Ferroviaires</h1>

      <div className="operators-layout">
        {/* Colonne gauche - Liste des opérateurs */}
        <div className="operators-panel">
          <div className="operators-search">
            <h3>🔍 Rechercher un opérateur</h3>
            <input
              type="text"
              placeholder="Nom de l'opérateur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="operators-table-wrapper operators-list-wrapper">
            <table className="operators-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nom</th>
                </tr>
              </thead>
              <tbody>
                {filteredOperators.map((operator, index) => (
                  <tr
                    key={operator.operator_id || index}
                    className={selectedOperator?.id === operator.operator_id ? 'is-selected' : ''}
                    onClick={() => handleSelectOperator(operator.operator_id, operator.operator_name)}
                  >
                    <td className="muted-cell">{operator.operator_id}</td>
                    <td className="operator-name-cell">{operator.operator_name}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredOperators.length === 0 && (
              <div className="operators-empty">
                Aucun opérateur trouvé
              </div>
            )}
          </div>
        </div>

        {/* Colonne droite - Détails de l'opérateur sélectionné */}
        <div>
          {!selectedOperator ? (
            <div className="operators-state-card">
              <span className="operators-state-icon">👈</span>
              <p>Sélectionnez un opérateur dans la liste de gauche</p>
            </div>
          ) : loading ? (
            <div className="operators-state-card">
              <div className="operators-spinner"></div>
              <p>Chargement des données...</p>
            </div>
          ) : (
            <div>
              {/* En-tête avec le nom de l'opérateur */}
              <div className="operator-hero">
                <h2>{selectedOperator.name}</h2>
                <p>Opérateur ferroviaire européen</p>
                {operatorDetails?.countries_served && (
                  <p className="operator-countries">
                    🌍 Pays desservis : {operatorDetails.countries_served.join(", ")}
                  </p>
                )}
              </div>

              {/* Cartes KPI */}
              <div className="operator-kpi-grid">
                <div className="operator-kpi-card total">
                  <h4>🚆 TOTAL TRAJETS</h4>
                  <p>{formatNumber(operatorDetails?.total_trains)}</p>
                </div>
                <div className="operator-kpi-card night">
                  <h4>🌙 TRAJETS DE NUIT</h4>
                  <p>{formatNumber(operatorDetails?.night_trains)}</p>
                </div>
                <div className="operator-kpi-card day">
                  <h4>☀️ TRAJETS JOUR</h4>
                  <p>{formatNumber(operatorDetails?.day_trains)}</p>
                </div>
              </div>

              {/* Évolution temporelle */}
              {getTimelineData() && (
                <div className="operators-card">
                  <h3 className="operators-chart-title">
                    📈 Évolution du nombre de trains (2020-2024)
                  </h3>
                  <div className="operators-chart-box">
                    <Line data={getTimelineData()} options={timelineOptions} />
                  </div>
                </div>
              )}

              {/* Indicateurs de performance */}
              <div className="operators-card">
                <h3>📊 INDICATEURS DE PERFORMANCE</h3>
                <div className="performance-grid">
                  <div>
                    <div className="performance-label">Distance totale parcourue</div>
                    <div className="performance-value">
                      {formatDistance(operatorDetails?.distance_totale_km)}
                    </div>
                  </div>
                  <div>
                    <div className="performance-label">Durée moyenne des trajets</div>
                    <div className="performance-value">
                      {formatDuration(operatorDetails?.duree_moyenne_min / 60)}
                    </div>
                  </div>
                  <div>
                    <div className="performance-label">Pays desservis</div>
                    <div className="performance-value">
                      {operatorDetails?.countries_count || 0}
                    </div>
                  </div>
                  <div>
                    <div className="performance-label">CO₂ moyen par passager</div>
                    <div className="performance-value green">
                      {operatorDetails?.avg_co2_per_passenger?.toFixed(3) || 'N/A'} kg
                    </div>
                  </div>
                </div>
              </div>

              {/* Liste des trajets */}
              <div className="operators-card">
                <h3 className="operators-routes-title">
                  🚆 LISTE DES TRAJETS {selectedOperator.name}
                </h3>
                <div className="operators-table-wrapper routes-table-wrapper">
                  <table className="operators-table routes-table">
                    <thead>
                      <tr>
                        <th>Pays</th>
                        <th>Opérateur</th>
                        <th className="center-cell">Type</th>
                        <th className="right-cell">Distance</th>
                        <th className="right-cell">Durée</th>
                        <th className="center-cell">Année</th>
                      </tr>
                    </thead>
                    <tbody>
                      {operatorTrains.map((train, index) => (
                        <tr key={train.fact_id || index}>
                          <td>{train.country_name} ({train.country_code})</td>
                          <td>{train.operator_name}</td>
                          <td className="center-cell">
                            <span className={`train-type-badge ${train.is_night ? 'is-night' : 'is-day'}`}>
                              {train.is_night ? '🌙 Nuit' : '☀️ Jour'}
                            </span>
                          </td>
                          <td className="right-cell">{formatDistance(train.distance_km)}</td>
                          <td className="right-cell">{formatDuration(train.duration_min / 60)}</td>
                          <td className="center-cell">{train.year}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {operatorTrains.length === 0 && (
                  <div className="operators-empty">
                    Aucun trajet trouvé pour cet opérateur
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
