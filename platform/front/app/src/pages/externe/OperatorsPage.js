import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
  PointElement,
  LineElement
} from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import { getOperators, getOperatorStats, getTrainsByOperator } from '../../services/api';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
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
  const [windowWidth, setWindowWidth] = useState(window.innerWidth);

  const isTablet = windowWidth <= 1024;
  const isMobile = windowWidth <= 768;
  const isSmallMobile = windowWidth <= 480;

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

  useEffect(() => {
    const handleResize = () => {
      setWindowWidth(window.innerWidth);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
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

  // Calculer le score d'efficacité
  const calculateEfficiencyScore = (details) => {
    if (!details) return 0;
    let score = 50; // Score de base
    if (details.avg_co2_per_passenger < 0.05) score += 30;
    else if (details.avg_co2_per_passenger < 0.1) score += 15;
    if (details.night_trains > details.day_trains) score += 10;
    if (details.total_trains > 200) score += 10;
    return Math.min(score, 100);
  };

  // Préparer les données pour le graphique en barres (distribution jour/nuit)
  const getDistributionData = () => {
    if (!operatorDetails) return null;
    return {
      labels: ['Trains de Jour', 'Trains de Nuit'],
      datasets: [
        {
          label: 'Nombre de trains',
          data: [operatorDetails.day_trains || 0, operatorDetails.night_trains || 0],
          backgroundColor: ['#1769aa', '#12263a'],
          borderColor: ['#fff', '#fff'],
          borderWidth: 2,
          borderRadius: 8,
        }
      ]
    };
  };

  // Préparer les données pour le graphique en anneau (efficacité)
  const getEfficiencyData = () => {
    if (!operatorDetails) return null;
    const score = calculateEfficiencyScore(operatorDetails);
    return {
      labels: ['Performance', 'Potentiel d\'amélioration'],
      datasets: [
        {
          data: [score, 100 - score],
          backgroundColor: ['#20a464', '#d8e0e8'],
          borderColor: ['#fff', '#fff'],
          borderWidth: 2,
          cutout: '70%',
        }
      ]
    };
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

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 11 }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            let value = context.raw;
            return `${label}: ${value.toLocaleString()}`;
          }
        }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 15,
          font: { size: 11 }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            return `${context.label}: ${context.raw}%`;
          }
        }
      }
    }
  };

  const timelineOptions = {
    responsive: true,
    maintainAspectRatio: true,
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
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '1400px', margin: '0 auto', padding: isSmallMobile ? '10px' : isMobile ? '14px' : '20px', color: '#17202a' }}>
      <h1 style={{ color: '#12263a', marginBottom: isMobile ? '18px' : '30px', fontSize: isSmallMobile ? '24px' : isMobile ? '28px' : '32px' }}>🚆 Opérateurs Ferroviaires</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: isTablet ? '1fr' : '350px 1fr', gap: isMobile ? '16px' : isTablet ? '20px' : '30px' }}>
        
        {/* Colonne gauche - Liste des opérateurs */}
        <div style={{ 
          background: 'white',
          border: '1px solid #dde5ed',
          borderRadius: '8px',
          boxShadow: '0 1px 2px rgba(18,38,58,0.04)',
          overflow: 'hidden',
          height: 'fit-content'
        }}>
          <div style={{ padding: isMobile ? '14px' : '20px', borderBottom: '1px solid #dde5ed' }}>
            <h3 style={{ margin: 0, marginBottom: '15px', color: '#12263a', fontSize: isMobile ? '16px' : '18px' }}>🔍 Rechercher un opérateur</h3>
            <input
              type="text"
              placeholder="Nom de l'opérateur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #c9d2dc',
                borderRadius: '6px',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            />
          </div>
          
          <div style={{ maxHeight: isTablet ? '280px' : '500px', overflowY: 'auto', overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ position: 'sticky', top: 0, background: '#f4f6f8' }}>
                <tr style={{ borderBottom: '2px solid #dde5ed' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#52616f' }}>ID</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#52616f' }}>Nom</th>
                 </tr>
              </thead>
              <tbody>
                {filteredOperators.map((operator, index) => (
                  <tr
                    key={operator.operator_id || index}
                    onClick={() => handleSelectOperator(operator.operator_id, operator.operator_name)}
                    style={{
                      cursor: 'pointer',
                      background: selectedOperator?.id === operator.operator_id ? '#edf2f7' : 'white',
                      transition: 'background 0.2s',
                      borderBottom: '1px solid #e6edf3'
                    }}
                    onMouseEnter={(e) => {
                      if (selectedOperator?.id !== operator.operator_id) {
                        e.currentTarget.style.background = '#f4f6f8';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (selectedOperator?.id !== operator.operator_id) {
                        e.currentTarget.style.background = 'white';
                      }
                    }}
                  >
                    <td style={{ padding: '12px', fontSize: '14px', color: '#52616f' }}>
                      {operator.operator_id}
                    </td>
                    <td style={{ padding: '12px', fontSize: '14px', fontWeight: '500' }}>
                      {operator.operator_name}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {filteredOperators.length === 0 && (
              <div style={{ padding: '40px', textAlign: 'center', color: '#6f7d89' }}>
                Aucun opérateur trouvé
              </div>
            )}
          </div>
        </div>
        
        {/* Colonne droite - Détails de l'opérateur sélectionné */}
        <div>
          {!selectedOperator ? (
            <div style={{
              background: 'white',
              border: '1px solid #dde5ed',
              borderRadius: '8px',
              boxShadow: '0 1px 2px rgba(18,38,58,0.04)',
              padding: isMobile ? '28px 16px' : '60px',
              textAlign: 'center',
              color: '#6f7d89'
            }}>
              <span style={{ fontSize: isMobile ? '36px' : '48px' }}>👈</span>
              <p style={{ marginTop: '20px', fontSize: isMobile ? '14px' : '16px' }}>
                Sélectionnez un opérateur dans la liste de gauche
              </p>
            </div>
          ) : loading ? (
            <div style={{
              background: 'white',
              border: '1px solid #dde5ed',
              borderRadius: '8px',
              boxShadow: '0 1px 2px rgba(18,38,58,0.04)',
              padding: isMobile ? '28px 16px' : '60px',
              textAlign: 'center'
            }}>
              <div style={{ 
                display: 'inline-block',
                width: '40px',
                height: '40px',
                border: '4px solid #d8e0e8',
                borderTop: '4px solid #1769aa',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
              <p style={{ marginTop: '20px', color: '#52616f' }}>Chargement des données...</p>
              <style>{`
                @keyframes spin {
                  0% { transform: rotate(0deg); }
                  100% { transform: rotate(360deg); }
                }
              `}</style>
            </div>
          ) : (
            <div>
              {/* En-tête avec le nom de l'opérateur */}
              <div style={{
                background: '#12263a',
                borderRadius: '8px',
                padding: isMobile ? '18px' : '25px',
                color: 'white',
                marginBottom: '20px'
              }}>
                <h2 style={{ margin: 0, fontSize: isSmallMobile ? '20px' : isMobile ? '24px' : '28px', overflowWrap: 'anywhere' }}>
                  {selectedOperator.name}
                </h2>
                <p style={{ margin: '10px 0 0 0', opacity: 0.9, fontSize: '14px' }}>
                  Opérateur ferroviaire européen
                </p>
                {operatorDetails?.countries_served && (
                  <p style={{ margin: '5px 0 0 0', opacity: 0.8, fontSize: '12px' }}>
                    🌍 Pays desservis : {operatorDetails.countries_served.join(", ")}
                  </p>
                )}
              </div>
              
              {/* Cartes KPI */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: isMobile ? '1fr' : 'repeat(3, 1fr)',
                gap: isMobile ? '10px' : '15px',
                marginBottom: '20px'
              }}>
                <div style={{
                  background: '#12263a',
                  borderRadius: '8px',
                  padding: isMobile ? '15px' : '20px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>🚆 TOTAL TRAINS</h4>
                  <p style={{ margin: 0, fontSize: isMobile ? '22px' : '28px', fontWeight: 'bold' }}>
                    {formatNumber(operatorDetails?.total_trains)}
                  </p>
                </div>
                <div style={{
                  background: '#1769aa',
                  borderRadius: '8px',
                  padding: isMobile ? '15px' : '20px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>🌙 TRAINS DE NUIT</h4>
                  <p style={{ margin: 0, fontSize: isMobile ? '22px' : '28px', fontWeight: 'bold' }}>
                    {formatNumber(operatorDetails?.night_trains)}
                  </p>
                </div>
                <div style={{
                  background: '#52616f',
                  borderRadius: '8px',
                  padding: isMobile ? '15px' : '20px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>☀️ TRAINS JOUR</h4>
                  <p style={{ margin: 0, fontSize: isMobile ? '22px' : '28px', fontWeight: 'bold' }}>
                    {formatNumber(operatorDetails?.day_trains)}
                  </p>
                </div>
              </div>
              
              {/* Évolution temporelle */}
              {getTimelineData() && (
                <div style={{
                  background: 'white',
                  border: '1px solid #dde5ed',
                  borderRadius: '8px',
                  padding: isMobile ? '14px' : '20px',
                  marginBottom: '20px',
                  boxShadow: '0 1px 2px rgba(18,38,58,0.04)'
                }}>
                  <h3 style={{ margin: '0 0 15px 0', color: '#12263a', fontSize: '16px', textAlign: 'center' }}>
                    📈 Évolution du nombre de trains (2020-2024)
                  </h3>
                  <div style={{ height: isMobile ? '240px' : '300px' }}>
                    <Line data={getTimelineData()} options={timelineOptions} />
                  </div>
                </div>
              )}
              
              {/* Indicateurs de performance */}
              <div style={{
                background: 'white',
                border: '1px solid #dde5ed',
                borderRadius: '8px',
                padding: isMobile ? '14px' : '20px',
                marginBottom: '20px',
                boxShadow: '0 1px 2px rgba(18,38,58,0.04)'
              }}>
                <h3 style={{ margin: '0 0 15px 0', color: '#12263a' }}>📊 INDICATEURS DE PERFORMANCE</h3>
                <div style={{ display: 'grid', gridTemplateColumns: isMobile ? '1fr' : 'repeat(2, 1fr)', gap: isMobile ? '10px' : '15px' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#52616f', marginBottom: '5px' }}>Distance totale parcourue</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#12263a' }}>
                      {formatDistance(operatorDetails?.distance_totale_km)}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#52616f', marginBottom: '5px' }}>Durée moyenne des trajets</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#12263a' }}>
                      {formatDuration(operatorDetails?.duree_moyenne_min / 60)}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#52616f', marginBottom: '5px' }}>Pays desservis</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#12263a' }}>
                      {operatorDetails?.countries_count || 0}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#52616f', marginBottom: '5px' }}>CO₂ moyen par passager</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#0d7a3b' }}>
                      {operatorDetails?.avg_co2_per_passenger?.toFixed(3) || 'N/A'} kg
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Liste des trajets */}
              <div style={{
                background: 'white',
                border: '1px solid #dde5ed',
                borderRadius: '8px',
                padding: isMobile ? '14px' : '20px',
                boxShadow: '0 1px 2px rgba(18,38,58,0.04)'
              }}>
                <h3 style={{ margin: '0 0 15px 0', color: '#12263a', fontSize: isMobile ? '16px' : '18px', overflowWrap: 'anywhere' }}>🚆 LISTE DES TRAJETS {selectedOperator.name}</h3>
                <div style={{ overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead style={{ position: 'sticky', top: 0, background: '#f4f6f8' }}>
                      <tr style={{ borderBottom: '2px solid #dde5ed' }}>
                        <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#52616f' }}>Pays</th>
                        <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#52616f' }}>Opérateur</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontSize: '12px', color: '#52616f' }}>Type</th>
                        <th style={{ padding: '12px', textAlign: 'right', fontSize: '12px', color: '#52616f' }}>Distance</th>
                        <th style={{ padding: '12px', textAlign: 'right', fontSize: '12px', color: '#52616f' }}>Durée</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontSize: '12px', color: '#52616f' }}>Année</th>
                      </tr>
                    </thead>
                    <tbody>
                      {operatorTrains.map((train, index) => (
                        <tr key={train.fact_id || index} style={{ borderBottom: '1px solid #e6edf3' }}>
                          <td style={{ padding: '12px', fontSize: '14px' }}>
                            {train.country_name} ({train.country_code})
                          </td>
                          <td style={{ padding: '12px', fontSize: '14px' }}>{train.operator_name}</td>
                          <td style={{ padding: '12px', textAlign: 'center' }}>
                            <span style={{
                              display: 'inline-block',
                              padding: '4px 12px',
                              borderRadius: '20px',
                              fontSize: '12px',
                              fontWeight: 'bold',
                              background: train.is_night ? '#edf2f7' : '#e5f7ed',
                              color: train.is_night ? '#12263a' : '#0d7a3b'
                            }}>
                              {train.is_night ? '🌙 Nuit' : '☀️ Jour'}
                            </span>
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', fontSize: '14px' }}>
                            {formatDistance(train.distance_km)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'right', fontSize: '14px' }}>
                            {formatDuration(train.duration_min / 60)}
                          </td>
                          <td style={{ padding: '12px', textAlign: 'center', fontSize: '14px' }}>
                            {train.year}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {operatorTrains.length === 0 && (
                  <div style={{ padding: '40px', textAlign: 'center', color: '#6f7d89' }}>
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
