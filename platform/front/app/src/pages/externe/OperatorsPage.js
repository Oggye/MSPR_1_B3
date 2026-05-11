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

  // Calculer le score d'efficacité
  const calculateEfficiencyScore = (details) => {
    if (!details) return 0;
    let score = 50; // Score de base
    if (details.avg_co2_per_passenger_kg < 0.05) score += 30;
    else if (details.avg_co2_per_passenger_kg < 0.1) score += 15;
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
          backgroundColor: ['#4facfe', '#f093fb'],
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
          backgroundColor: ['#43e97b', '#e0e0e0'],
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
          borderColor: '#f093fb',
          backgroundColor: 'rgba(240, 147, 251, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: '#f093fb',
        },
        {
          label: 'Trains de Jour',
          data: dayCounts,
          borderColor: '#4facfe',
          backgroundColor: 'rgba(79, 172, 254, 0.1)',
          tension: 0.4,
          fill: true,
          pointRadius: 5,
          pointHoverRadius: 7,
          pointBackgroundColor: '#4facfe',
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
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '1400px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ color: '#333', marginBottom: '30px' }}>🚆 Opérateurs Ferroviaires</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '30px' }}>
        
        {/* Colonne gauche - Liste des opérateurs */}
        <div style={{ 
          background: 'white',
          borderRadius: '10px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          overflow: 'hidden',
          height: 'fit-content'
        }}>
          <div style={{ padding: '20px', borderBottom: '1px solid #e0e0e0' }}>
            <h3 style={{ margin: 0, marginBottom: '15px', color: '#555' }}>🔍 Rechercher un opérateur</h3>
            <input
              type="text"
              placeholder="Nom de l'opérateur..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                width: '100%',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '5px',
                fontSize: '14px',
                boxSizing: 'border-box'
              }}
            />
          </div>
          
          <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
              <thead style={{ position: 'sticky', top: 0, background: '#f8f9fa' }}>
                <tr style={{ borderBottom: '2px solid #e9ecef' }}>
                  <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#666' }}>ID</th>
                  <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#666' }}>Nom</th>
                 </tr>
              </thead>
              <tbody>
                {filteredOperators.map((operator, index) => (
                  <tr
                    key={operator.operator_id || index}
                    onClick={() => handleSelectOperator(operator.operator_id, operator.operator_name)}
                    style={{
                      cursor: 'pointer',
                      background: selectedOperator?.id === operator.operator_id ? '#e3f2fd' : 'white',
                      transition: 'background 0.2s',
                      borderBottom: '1px solid #f0f0f0'
                    }}
                    onMouseEnter={(e) => {
                      if (selectedOperator?.id !== operator.operator_id) {
                        e.currentTarget.style.background = '#f5f5f5';
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (selectedOperator?.id !== operator.operator_id) {
                        e.currentTarget.style.background = 'white';
                      }
                    }}
                  >
                    <td style={{ padding: '12px', fontSize: '14px', color: '#666' }}>
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
              <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
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
              borderRadius: '10px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              padding: '60px',
              textAlign: 'center',
              color: '#999'
            }}>
              <span style={{ fontSize: '48px' }}>👈</span>
              <p style={{ marginTop: '20px', fontSize: '16px' }}>
                Sélectionnez un opérateur dans la liste de gauche
              </p>
            </div>
          ) : loading ? (
            <div style={{
              background: 'white',
              borderRadius: '10px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              padding: '60px',
              textAlign: 'center'
            }}>
              <div style={{ 
                display: 'inline-block',
                width: '40px',
                height: '40px',
                border: '4px solid #f3f3f3',
                borderTop: '4px solid #3498db',
                borderRadius: '50%',
                animation: 'spin 1s linear infinite'
              }}></div>
              <p style={{ marginTop: '20px', color: '#666' }}>Chargement des données...</p>
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
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                borderRadius: '10px',
                padding: '25px',
                color: 'white',
                marginBottom: '20px'
              }}>
                <h2 style={{ margin: 0, fontSize: '28px' }}>
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
                gridTemplateColumns: 'repeat(3, 1fr)',
                gap: '15px',
                marginBottom: '20px'
              }}>
                <div style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  borderRadius: '10px',
                  padding: '20px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>🚆 TOTAL TRAINS</h4>
                  <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold' }}>
                    {formatNumber(operatorDetails?.total_trains)}
                  </p>
                </div>
                <div style={{
                  background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
                  borderRadius: '10px',
                  padding: '20px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>🌙 TRAINS DE NUIT</h4>
                  <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold' }}>
                    {formatNumber(operatorDetails?.night_trains)}
                  </p>
                </div>
                <div style={{
                  background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
                  borderRadius: '10px',
                  padding: '20px',
                  color: 'white',
                  textAlign: 'center'
                }}>
                  <h4 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>☀️ TRAINS JOUR</h4>
                  <p style={{ margin: 0, fontSize: '28px', fontWeight: 'bold' }}>
                    {formatNumber(operatorDetails?.day_trains)}
                  </p>
                </div>
              </div>
              
              {/* Évolution temporelle */}
              {getTimelineData() && (
                <div style={{
                  background: 'white',
                  borderRadius: '10px',
                  padding: '20px',
                  marginBottom: '20px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
                }}>
                  <h3 style={{ margin: '0 0 15px 0', color: '#333', fontSize: '16px', textAlign: 'center' }}>
                    📈 Évolution du nombre de trains (2020-2024)
                  </h3>
                  <div style={{ height: '300px' }}>
                    <Line data={getTimelineData()} options={timelineOptions} />
                  </div>
                </div>
              )}
              
              {/* Indicateurs de performance */}
              <div style={{
                background: 'white',
                borderRadius: '10px',
                padding: '20px',
                marginBottom: '20px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ margin: '0 0 15px 0', color: '#333' }}>📊 INDICATEURS DE PERFORMANCE</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '15px' }}>
                  <div>
                    <div style={{ fontSize: '12px', color: '#999', marginBottom: '5px' }}>Distance totale parcourue</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333' }}>
                      {formatDistance(operatorDetails?.distance_totale_km)}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#999', marginBottom: '5px' }}>Durée moyenne des trajets</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333' }}>
                      {formatDuration(operatorDetails?.duree_moyenne_min / 60)}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#999', marginBottom: '5px' }}>Pays desservis</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#333' }}>
                      {operatorDetails?.countries_count || 0}
                    </div>
                  </div>
                  <div>
                    <div style={{ fontSize: '12px', color: '#999', marginBottom: '5px' }}>CO₂ moyen par passager</div>
                    <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#28a745' }}>
                      {operatorDetails?.avg_co2_per_passenger?.toFixed(3) || 'N/A'} kg
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Liste des trajets */}
              <div style={{
                background: 'white',
                borderRadius: '10px',
                padding: '20px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
              }}>
                <h3 style={{ margin: '0 0 15px 0', color: '#333' }}>🚆 LISTE DES TRAJETS {selectedOperator.name}</h3>
                <div style={{ overflowX: 'auto', maxHeight: '400px', overflowY: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <thead style={{ position: 'sticky', top: 0, background: '#f8f9fa' }}>
                      <tr style={{ borderBottom: '2px solid #e9ecef' }}>
                        <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#666' }}>Pays</th>
                        <th style={{ padding: '12px', textAlign: 'left', fontSize: '12px', color: '#666' }}>Opérateur</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontSize: '12px', color: '#666' }}>Type</th>
                        <th style={{ padding: '12px', textAlign: 'right', fontSize: '12px', color: '#666' }}>Distance</th>
                        <th style={{ padding: '12px', textAlign: 'right', fontSize: '12px', color: '#666' }}>Durée</th>
                        <th style={{ padding: '12px', textAlign: 'center', fontSize: '12px', color: '#666' }}>Année</th>
                      </tr>
                    </thead>
                    <tbody>
                      {operatorTrains.map((train, index) => (
                        <tr key={train.fact_id || index} style={{ borderBottom: '1px solid #f0f0f0' }}>
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
                              background: train.is_night ? '#f093fb20' : '#4facfe20',
                              color: train.is_night ? '#f5576c' : '#4facfe'
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
                  <div style={{ padding: '40px', textAlign: 'center', color: '#999' }}>
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