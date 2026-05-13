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

  useEffect(function () {
    getSummary()
      .then(function (response) {
        setSummary(response.data);
      })
      .catch(function (error) {
        console.log(error);
      });

    getTimeline()
      .then(function (response) {
        setTimeline(response.data);
      })
      .catch(function (error) {
        console.log(error);
      });

    getDashboardKpis()
      .then(function (response) {
        setKpis(response.data);
      })
      .catch(function (error) {
        console.log(error);
      });
  }, []);

  const years = timeline.map(function (item) {
    return item.year;
  });

  const passengers = timeline.map(function (item) {
    if (item.passengers) {
      return item.passengers / 1000000;
    }

    return 0;
  });

  const co2Emissions = timeline.map(function (item) {
    if (item.co2_emissions) {
      return item.co2_emissions / 1000;
    }

    return 0;
  });

  let totalTrains = 0;
  let totalNightTrains = 0;
  let totalDayTrains = 0;
  let totalCountries = 0;
  let avgCo2 = 0;
  let totalPassengers = 0;
  let totalCo2 = 0;
  let yearsCovered = '2010-2024';
  let totalOperators = 0;

  if (summary !== null) {
    if (summary.total_trains) {
      totalTrains = summary.total_trains;
    }

    if (summary.total_night_trains) {
      totalNightTrains = summary.total_night_trains;
    }

    if (summary.total_day_trains) {
      totalDayTrains = summary.total_day_trains;
    }
  }

  if (kpis !== null) {
    if (kpis.total_countries) {
      totalCountries = kpis.total_countries;
    }

    if (kpis.avg_co2_per_passenger) {
      avgCo2 = kpis.avg_co2_per_passenger;
    }

    if (kpis.total_passengers) {
      totalPassengers = kpis.total_passengers;
    }

    if (kpis.total_co2_emissions) {
      totalCo2 = kpis.total_co2_emissions;
    }

    if (kpis.years_covered) {
      yearsCovered = kpis.years_covered;
    }

    if (kpis.total_operators) {
      totalOperators = kpis.total_operators;
    }
  }

  const chartData = {
    labels: years,
    datasets: [
      {
        label: 'Passagers (millions)',
        data: passengers,
        borderColor: '#1769aa',
        backgroundColor: 'rgba(23, 105, 170, 0.1)',
        borderWidth: 3,
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: '#1769aa',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        tension: 0.4,
        fill: true,
        yAxisID: 'y'
      },
      {
        label: 'Emissions CO2 (milliers de tonnes)',
        data: co2Emissions,
        borderColor: '#20a464',
        backgroundColor: 'rgba(32, 164, 100, 0.1)',
        borderWidth: 3,
        borderDash: [8, 4],
        pointRadius: 6,
        pointHoverRadius: 8,
        pointBackgroundColor: '#20a464',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        tension: 0.4,
        fill: true,
        yAxisID: 'y1'
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: {
      mode: 'index',
      intersect: false
    },
    plugins: {
      tooltip: {
        callbacks: {
          label: function (context) {
            const label = context.dataset.label;
            const value = context.raw;

            if (label.includes('Passagers')) {
              return label + ': ' + value.toFixed(1) + ' millions';
            }

            return label + ': ' + value.toFixed(0) + ' milliers de tonnes';
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
          color: '#1769aa',
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
          text: 'Emissions CO2 (milliers de tonnes)',
          color: '#20a464',
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
          drawOnChartArea: false
        }
      },
      x: {
        title: {
          display: true,
          text: 'Annee',
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
        fill: true
      },
      point: {
        hoverRadius: 8
      }
    }
  };

  return (
    <div className="homepage-container">
      <h1 className="homepage-title">Dashboard</h1>

      <div className="kpi-grid">
        <div className="kpi-card kpi-card-purple">
          <h3 className="kpi-card-title">Trains</h3>
          <p className="kpi-card-value">{totalTrains.toLocaleString()}</p>
        </div>

        <div className="kpi-card kpi-card-pink">
          <h3 className="kpi-card-title">Nuit</h3>
          <p className="kpi-card-value">{totalNightTrains.toLocaleString()}</p>
        </div>

        <div className="kpi-card kpi-card-blue">
          <h3 className="kpi-card-title">Jour</h3>
          <p className="kpi-card-value">{totalDayTrains.toLocaleString()}</p>
        </div>

        <div className="kpi-card kpi-card-green">
          <h3 className="kpi-card-title">Pays</h3>
          <p className="kpi-card-value">{totalCountries.toLocaleString()}</p>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <h3 className="stat-card-title">Indicateurs cles</h3>

          <div className="stat-item">
            <span className="stat-label">CO2 moyen par passager</span>
            <p className="stat-value stat-value-green">
              {avgCo2.toFixed(3)} kg
            </p>
          </div>

          <div className="stat-item">
            <span className="stat-label">Total passagers</span>
            <p className="stat-value stat-value-blue">
              {(totalPassengers / 1000000).toFixed(1)} millions
            </p>
          </div>

          <div>
            <span className="stat-label">Total emissions CO2</span>
            <p className="stat-value stat-value-orange">
              {(totalCo2 / 1000).toFixed(0)} kt
            </p>
          </div>
        </div>

        <div className="stat-card">
          <h3 className="stat-card-title">Periode couverte</h3>

          <div>
            <span className="stat-label">Annees d'analyse</span>
            <p className="stat-value stat-value-purple">
              {yearsCovered}
            </p>
          </div>

          <div className="stat-item-top">
            <span className="stat-label">Operateurs</span>
            <p className="stat-value stat-value-red">
              {totalOperators.toLocaleString()}
            </p>
          </div>
        </div>
      </div>

      <div className="chart-container">
        <h1 className="chart-title">Evolution temporelle</h1>
        <h3 className="chart-subtitle">
          Evolution des passagers et emissions CO2
        </h3>

        <div className="chart-wrapper">
          <Line data={chartData} options={chartOptions} />
        </div>
      </div>
    </div>
  );
}
