import { useEffect, useState } from 'react';
import { getSummary, getTimeline, getCo2Ranking, getDashboardKpis } from '../../services/api';

export default function ExterneHomePage() {
  const [summary, setSummary] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [ranking, setRanking] = useState([]);
  const [kpis, setKpis] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resSummary, resTimeline, resRanking, resKpis] = await Promise.all([
          getSummary(), getTimeline(), getCo2Ranking(), getDashboardKpis()
        ]);
        setSummary(resSummary.data);
        setTimeline(resTimeline.data);
        setRanking(resRanking.data);
        setKpis(resKpis.data);
      } catch (error) {
        console.error(error);
      }
    };
    fetchData();
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      
      {/* KPI */}
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ border: '1px solid #ccc', padding: '20px' }}>
          <h3>🚆 Trains</h3>
          <p>{summary?.total_trains || 0}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '20px' }}>
          <h3>🌙 Nuit</h3>
          <p>{summary?.total_night_trains || 0}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '20px' }}>
          <h3>☀️ Jour</h3>
          <p>{summary?.total_day_trains || 0}</p>
        </div>
        <div style={{ border: '1px solid #ccc', padding: '20px' }}>
          <h3>🇪🇺 Pays</h3>
          <p>{kpis?.total_countries || 0}</p>
        </div>
      </div>

      {/* Timeline */}
      <h3>📈 Évolution</h3>
      <table border="1">
        <thead>
          <tr><th>Année</th><th>Passagers</th><th>CO₂</th><th>Trains nuit</th></tr>
        </thead>
        <tbody>
          {timeline.map(item => (
            <tr key={item.year}>
              <td>{item.year}</td>
              <td>{item.passengers?.toLocaleString()}</td>
              <td>{item.co2_emissions?.toLocaleString()}</td>
              <td>{item.night_trains_count}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Classement CO₂ */}
      <h3>🌍 Classement CO₂ (meilleurs pays)</h3>
      <ul>
        {ranking.map(item => (
          <li key={item.country_code}>
            {item.country_name} : {item.avg_co2_per_passenger} kg CO₂/passager
          </li>
        ))}
      </ul>
    </div>
  );
};