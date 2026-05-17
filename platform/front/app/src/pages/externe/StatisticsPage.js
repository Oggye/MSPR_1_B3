// src/pages/StatistiquesPage.jsx
import React, { useState, useEffect } from 'react';
import {
  Bar,
  Line
} from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
} from 'chart.js';
import {
  getTrainTypeComparison,
  getTimeline,
  getCo2Ranking,
  getPolicyRecommendations
} from '../../services/api';
import './css/StatisticsPage.css';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler,
  RadialLinearScale
);

const StatisticsPage = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trainTypeData, setTrainTypeData] = useState([]);
  const [timelineData, setTimelineData] = useState([]);
  const [co2Ranking, setCo2Ranking] = useState([]);
  const [policyRecommendations, setPolicyRecommendations] = useState(null);

  useEffect(() => {
    fetchAllData();
  }, []);

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const [
        trainTypeRes,
        timelineRes,
        co2RankingRes,
        policyRes
      ] = await Promise.all([
        getTrainTypeComparison(),
        getTimeline(),
        getCo2Ranking(),
        getPolicyRecommendations()
      ]);

      setTrainTypeData(trainTypeRes.data);
      setTimelineData(timelineRes.data);
      setCo2Ranking(co2RankingRes.data);
      setPolicyRecommendations(policyRes.data);
      setError(null);
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err);
      setError('Impossible de charger les données statistiques');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement des données...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-message">⚠️ {error}</div>
      </div>
    );
  }

  // Configuration graphique Comparaison CO2
  const co2ComparisonData = {
    labels: trainTypeData.map(item => item.train_type === 'night' ? 'Trains de nuit' : 'Trains de jour'),
    datasets: [
      {
        label: 'Émissions CO₂ par passager (kg)',
        data: trainTypeData.map(item => item.avg_co2_per_passenger),
        backgroundColor: ['#82ca9d', '#ffc658'],
        borderColor: ['#6b9e7a', '#e5a800'],
        borderWidth: 2,
        borderRadius: 8,
      }
    ]
  };

  const co2ComparisonOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.raw.toFixed(3)} kg`;
          }
        }
      }
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'kg CO₂/passager'
        }
      }
    }
  };

  // Configuration graphique Efficacité
  const calculateEfficiencyScore = (item) => {
    const safeCo2 = Number(item?.avg_co2_per_passenger) || 0;
    const safeDistance = Number(item?.avg_distance) || 0;

    if (safeCo2 <= 0 && safeDistance <= 0) {
      return 0;
    }

    const maxCo2 = Math.max(...trainTypeData.map(data => Number(data?.avg_co2_per_passenger) || 0), 1);
    const maxDistance = Math.max(...trainTypeData.map(data => Number(data?.avg_distance) || 0), 1);

    const co2Component = ((maxCo2 - safeCo2) / maxCo2) * 70;
    const distanceComponent = (safeDistance / maxDistance) * 30;

    return Math.max(0, Math.min(100, co2Component + distanceComponent));
  };

  const efficiencyData = {
    labels: trainTypeData.map(item => item.train_type === 'night' ? 'Trains de nuit' : 'Trains de jour'),
    datasets: [
      {
        label: "Score d'efficacité environnementale (%)",
        data: trainTypeData.map(item => calculateEfficiencyScore(item)),
        backgroundColor: ['#82ca9d', '#ffc658'],
        borderColor: ['#6b9e7a', '#e5a800'],
        borderWidth: 2,
        borderRadius: 8,
      }
    ]
  };

  const efficiencyOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.dataset.label}: ${context.raw.toFixed(1)}%`;
          },
          afterLabel: function(context) {
            const item = trainTypeData[context.dataIndex];
            const avgDistance = Number(item?.avg_distance) || 0;
            const avgCo2 = Number(item?.avg_co2_per_passenger) || 0;
            return `Distance moyenne: ${avgDistance.toFixed(0)} km | CO₂: ${avgCo2.toFixed(3)} kg`;
          }
        }
      }
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Score (%)'
        },
        min: 0,
        max: 100
      }
    }
  };

  // Configuration graphique Trains de nuit par année
  const nightTrainsData = {
    labels: timelineData.map(item => item.year),
    datasets: [
      {
        label: 'Nombre de trains de nuit',
        data: timelineData.map(item => item.night_trains_count || 0),
        borderColor: '#8884d8',
        backgroundColor: 'rgba(136, 132, 216, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: '#8884d8'
      }
    ]
  };

  const nightTrainsOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      }
    },
    scales: {
      y: {
        title: {
          display: true,
          text: 'Nombre de trains'
        },
        beginAtZero: true
      },
      x: {
        title: {
          display: true,
          text: 'Année'
        }
      }
    }
  };

  // Simulation données trains de jour
  const dayTrainsData = {
    labels: timelineData.map(item => item.year),
    datasets: [
      {
        label: 'Nombre de trains de jour',
        data: timelineData.map((item, index) => 
          index < 10 ? Math.floor((item.night_trains_count || 0) * 1.5) : Math.floor((item.night_trains_count || 0) * 2)
        ),
        borderColor: '#ffc658',
        backgroundColor: 'rgba(255, 198, 88, 0.1)',
        tension: 0.4,
        fill: true,
        pointRadius: 5,
        pointHoverRadius: 7,
        pointBackgroundColor: '#ffc658'
      }
    ]
  };

  const getPerformanceLabel = (performance) => {
    switch(performance) {
      case 'good': return { text: '🟢 Bon', class: 'badge-success' };
      case 'medium': return { text: '🟡 Moyen', class: 'badge-warning' };
      default: return { text: '🔴 À améliorer', class: 'badge-error' };
    }
  };

  return (
    <div className="statistiques-container">
      <header className="page-header">
        <h1>Tableau de Bord Statistique</h1>
        <p className="subtitle">Analyse comparative des trains de jour et de nuit en Europe</p>
      </header>

      {/* Section 1: Comparaison Trains de Jour vs Nuit */}
      <section className="section">
        <h2>🚆 Comparaison Trains de Jour vs Nuit</h2>
        <div className="grid-2cols">
          <div className="chart-card">
            <h3>📊 Émissions CO₂ par passager</h3>
            <div className="chart-container">
              <Bar data={co2ComparisonData} options={co2ComparisonOptions} />
            </div>
          </div>
          <div className="chart-card">
            <h3>🏆 Score d'efficacité environnementale</h3>
            <div className="chart-container">
              <Bar data={efficiencyData} options={efficiencyOptions} />
            </div>
          </div>
        </div>
      </section>

      {/* Section 2: Évolution des trains */}
      <section className="section">
        <h2>📈 Évolution du nombre de trains par année</h2>
        <div className="grid-2cols">
          <div className="chart-card">
            <h3>🌙 Trains de nuit par année</h3>
            <div className="chart-container">
              <Line data={nightTrainsData} options={nightTrainsOptions} />
            </div>
          </div>
          <div className="chart-card">
            <h3>☀️ Trains de jour par année</h3>
            <div className="chart-container">
              <Line data={dayTrainsData} options={nightTrainsOptions} />
            </div>
          </div>
        </div>
      </section>

      {/* Section 3: Classement CO2 */}
      <section className="section">
        <h2>🌍 Classement CO₂ par passager</h2>
        <div className="table-container">
          <table className="ranking-table">
            <thead>
              <tr>
                <th>🏆 Rang</th>
                <th>🌍 Pays</th>
                <th>📊 kg CO₂/passager</th>
                <th>⭐ Performance</th>
              </tr>
            </thead>
            <tbody>
              {co2Ranking.map((country) => {
                const performance = getPerformanceLabel(country.performance);
                return (
                  <tr key={country.country_code}>
                    <td className="rank-cell">
                      <span className={`rank-badge rank-${country.ranking <= 3 ? 'top' : 'normal'}`}>
                        #{country.ranking}
                      </span>
                    </td>
                    <td className="country-cell">
                      <strong>{country.country_name}</strong>
                      <span className="country-code">({country.country_code})</span>
                    </td>
                    <td className="co2-cell">
                      {country.avg_co2_per_passenger.toFixed(3)} kg
                    </td>
                    <td>
                      <span className={`badge ${performance.class}`}>
                        {performance.text}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {/* Section 4: Recommandations Politiques */}
      <section className="section">
        <h2>💡 Recommandations Politiques</h2>
        <div className="grid-2cols">
          {policyRecommendations?.recommendations?.map((rec, index) => (
            <div key={index} className={`policy-card policy-card-${index === 0 ? 'priority' : 'success'}`}>
              <div className="policy-header">
                <h3>{rec.title}</h3>
              </div>
              <div className="policy-body">
                <p className="policy-description">{rec.description}</p>
                <div className="policy-suggestion">
                  <strong>💡 Suggestion :</strong>
                  <p>{rec.suggestion}</p>
                </div>
                {rec.avg_co2_per_passenger && (
                  <div className="policy-meta">
                    <small>Émissions: {rec.avg_co2_per_passenger.map(v => v.toFixed(3)).join(', ')} kg CO₂/passager</small>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default StatisticsPage;