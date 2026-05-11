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
  Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { getSummary, getTimeline, getDashboardKpis } from '../../services/api';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function ExterneHomePage() {
  const [summary, setSummary] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [kpis, setKpis] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resSummary, resTimeline, resKpis] = await Promise.all([
          getSummary(), getTimeline(), getDashboardKpis()
        ]);
        setSummary(resSummary.data);
        setTimeline(resTimeline.data);
        setKpis(resKpis.data);
      } catch (error) {
        console.error(error);
      }
    };
    fetchData();
  }, []);

  // Préparer les données pour Chart.js
  const years = timeline.map(item => item.year);
  const passengers = timeline.map(item => (item.passengers || 0) / 1000000); // Convertir en millions
  const co2Emissions = timeline.map(item => (item.co2_emissions || 0) / 1000); // Convertir en milliers de tonnes

  const chartData = {
    labels: years,
    datasets: [
      {
        label: 'Passagers (millions)',
        data: passengers,
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        borderWidth: 3,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: '#3498db',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        tension: 0.4,
        fill: true,
        yAxisID: 'y',
      },
      {
        label: 'Émissions CO₂ (milliers de tonnes)',
        data: co2Emissions,
        borderColor: '#2ecc71',
        backgroundColor: 'rgba(46, 204, 113, 0.1)',
        borderWidth: 3,
        borderDash: [8, 4],
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: '#2ecc71',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        tension: 0.4,
        fill: true,
        yAxisID: 'y1',
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function(context) {
            let label = context.dataset.label || '';
            let value = context.raw;
            if (context.dataset.label.includes('Passagers')) {
              return `${label}: ${value.toFixed(1)} millions`;
            } else {
              return `${label}: ${value.toFixed(0)} milliers de tonnes`;
            }
          }
        }
      },
      legend: {
        position: 'bottom',
        labels: {
          usePointStyle: true,
          padding: 20,
          font: {
            size: 12
          }
        }
      },
      title: {
        display: false
      }
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: {
          display: true,
          text: 'Passagers (millions)',
          color: '#3498db',
          font: {
            weight: 'bold',
            size: 12
          }
        },
        ticks: {
          callback: function(value) {
            return value.toFixed(0) + 'M';
          }
        },
        grid: {
          drawOnChartArea: true,
          color: '#e0e0e0',
          borderDash: [5, 5]
        }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        title: {
          display: true,
          text: 'Émissions CO₂ (milliers de tonnes)',
          color: '#2ecc71',
          font: {
            weight: 'bold',
            size: 12
          }
        },
        ticks: {
          callback: function(value) {
            return value.toFixed(0) + 'k';
          }
        },
        grid: {
          drawOnChartArea: false,
        }
      },
      x: {
        title: {
          display: true,
          text: 'Année',
          font: {
            weight: 'bold',
            size: 12
          }
        },
        grid: {
          color: '#e0e0e0',
          borderDash: [5, 5]
        }
      }
    },
    elements: {
      line: {
        fill: true,
      },
      point: {
        hoverRadius: 8,
      }
    }
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto', padding: '20px' }}>
      <h1 style={{ color: '#333', marginBottom: '30px' }}>Dashboard</h1>
      
      {/* KPI Cards */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(4, 1fr)', 
        gap: '20px',
        marginBottom: '40px'
      }}>
        <div style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '10px',
          padding: '20px',
          color: 'white',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          transition: 'transform 0.3s ease',
          cursor: 'pointer'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>🚆 Trains</h3>
          <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>{summary?.total_trains?.toLocaleString() || 0}</p>
        </div>
        <div style={{ 
          background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
          borderRadius: '10px',
          padding: '20px',
          color: 'white',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          transition: 'transform 0.3s ease',
          cursor: 'pointer'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>🌙 Nuit</h3>
          <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>{summary?.total_night_trains?.toLocaleString() || 0}</p>
        </div>
        <div style={{ 
          background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
          borderRadius: '10px',
          padding: '20px',
          color: 'white',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          transition: 'transform 0.3s ease',
          cursor: 'pointer'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>☀️ Jour</h3>
          <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>{summary?.total_day_trains?.toLocaleString() || 0}</p>
        </div>
        <div style={{ 
          background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
          borderRadius: '10px',
          padding: '20px',
          color: 'white',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)',
          transition: 'transform 0.3s ease',
          cursor: 'pointer'
        }}
        onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-5px)'}
        onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}>
          <h3 style={{ margin: '0 0 10px 0', fontSize: '14px', opacity: 0.9 }}>🌍 Pays</h3>
          <p style={{ margin: 0, fontSize: '32px', fontWeight: 'bold' }}>{kpis?.total_countries?.toLocaleString() || 0}</p>
        </div>
      </div>
{/* Statistiques supplémentaires */}
<div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(2, 1fr)',
        gap: '20px',
        marginTop: '20px'
      }}>
        <div style={{
          background: 'white',
          borderRadius: '10px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ color: '#333', marginBottom: '15px' }}>📊 Indicateurs Clés</h3>
          <div style={{ marginBottom: '15px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>CO₂ moyen par passager</span>
            <p style={{ margin: '5px 0 0 0', fontSize: '24px', fontWeight: 'bold', color: '#2ecc71' }}>
              {kpis?.avg_co2_per_passenger?.toFixed(3) || 0} kg
            </p>
          </div>
          <div style={{ marginBottom: '15px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Total passagers</span>
            <p style={{ margin: '5px 0 0 0', fontSize: '24px', fontWeight: 'bold', color: '#3498db' }}>
              {(kpis?.total_passengers / 1000000)?.toFixed(1) || 0} millions
            </p>
          </div>
          <div>
            <span style={{ color: '#666', fontSize: '14px' }}>Total émissions CO₂</span>
            <p style={{ margin: '5px 0 0 0', fontSize: '24px', fontWeight: 'bold', color: '#e67e22' }}>
              {(kpis?.total_co2_emissions / 1000)?.toFixed(0) || 0} kt
            </p>
          </div>
        </div>

        <div style={{
          background: 'white',
          borderRadius: '10px',
          padding: '20px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <h3 style={{ color: '#333', marginBottom: '15px' }}>📅 Période couverte</h3>
          <div>
            <span style={{ color: '#666', fontSize: '14px' }}>Années d'analyse</span>
            <p style={{ margin: '5px 0 0 0', fontSize: '24px', fontWeight: 'bold', color: '#9b59b6' }}>
              {kpis?.years_covered || '2010-2024'}
            </p>
          </div>
          <div style={{ marginTop: '15px' }}>
            <span style={{ color: '#666', fontSize: '14px' }}>Opérateurs</span>
            <p style={{ margin: '5px 0 0 0', fontSize: '24px', fontWeight: 'bold', color: '#e74c3c' }}>
              {kpis?.total_operators?.toLocaleString() || 0}
            </p>
          </div>
        </div>
      </div>
      {/* Graphique Évolution temporelle avec Chart.js */}
      <div style={{ 
        marginBottom: '40px',
        background: 'white',
        borderRadius: '10px',
        padding: '20px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <h1 style={{ color: '#333', marginBottom: '10px' }}>📈 Évolution temporelle</h1>
        <h3 style={{ color: '#666', marginBottom: '30px', fontSize: '16px', fontWeight: 'normal' }}>
          Évolution des passagers et émissions CO₂
        </h3>
        
        <div style={{ height: '500px' }}>
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
}