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

import './css/HomePage.css';

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
          getSummary(),
          getTimeline(),
          getDashboardKpis()
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

  const passengers = timeline.map(
    item => (item.passengers || 0) / 1000000
  );

  const co2Emissions = timeline.map(
    item => (item.co2_emissions || 0) / 1000
  );

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
          label: function (context) {
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
          callback: function (value) {
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
          callback: function (value) {
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
    <div className="homepage-container">
      <h1 className="homepage-title">Dashboard</h1>

      {/* KPI Cards */}
      <div className="kpi-grid">

        <div className="kpi-card trains">
          <h3>🚆 Trains</h3>

          <p>
            {summary?.total_trains?.toLocaleString() || 0}
          </p>
        </div>

        <div className="kpi-card night">
          <h3>🌙 Nuit</h3>

          <p>
            {summary?.total_night_trains?.toLocaleString() || 0}
          </p>
        </div>

        <div className="kpi-card day">
          <h3>☀️ Jour</h3>

          <p>
            {summary?.total_day_trains?.toLocaleString() || 0}
          </p>
        </div>

        <div className="kpi-card countries">
          <h3>🌍 Pays</h3>

          <p>
            {kpis?.total_countries?.toLocaleString() || 0}
          </p>
        </div>
      </div>

      {/* Statistiques supplémentaires */}
      <div className="stats-grid">

        <div className="stats-card">
          <h3>📊 Indicateurs Clés</h3>

          <div style={{ marginBottom: '15px' }}>
            <span className="stat-label">
              CO₂ moyen par passager
            </span>

            <p className="stat-value green">
              {kpis?.avg_co2_per_passenger?.toFixed(3) || 0} kg
            </p>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <span className="stat-label">
              Total passagers
            </span>

            <p className="stat-value blue">
              {(kpis?.total_passengers / 1000000)?.toFixed(1) || 0} millions
            </p>
          </div>

          <div>
            <span className="stat-label">
              Total émissions CO₂
            </span>

            <p className="stat-value orange">
              {(kpis?.total_co2_emissions / 1000)?.toFixed(0) || 0} kt
            </p>
          </div>
        </div>

        <div className="stats-card">
          <h3>📅 Période couverte</h3>

          <div>
            <span className="stat-label">
              Années d'analyse
            </span>

            <p className="stat-value purple">
              {kpis?.years_covered || '2010-2024'}
            </p>
          </div>

          <div style={{ marginTop: '15px' }}>
            <span className="stat-label">
              Opérateurs
            </span>

            <p className="stat-value red">
              {kpis?.total_operators?.toLocaleString() || 0}
            </p>
          </div>
        </div>
      </div>

      {/* Graphique */}
      <div className="chart-container-homepage">

        <h1 className="chart-title">
          📈 Évolution temporelle
        </h1>

        <h3 className="chart-subtitle">
          Évolution des passagers et émissions CO₂
        </h3>

        <div className="chart-box">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
}