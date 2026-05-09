import { useEffect, useState } from 'react';
import { getTrainTypeComparison, getTimeline, getCo2Ranking, getCountryStats } from '../../services/api';

export default function StatistiquePage() {
    const [comparison, setComparison] = useState([]);
    const [timeline, setTimeline] = useState([]);
    const [ranking, setRanking] = useState([]);
    const [countryStats, setCountryStats] = useState([]);
  
    useEffect(() => {
      const fetchData = async () => {
        try {
          const [resComp, resTime, resRank, resCountry] = await Promise.all([
            getTrainTypeComparison(), getTimeline(), getCo2Ranking(), getCountryStats()
          ]);
          setComparison(resComp.data);
          setTimeline(resTime.data);
          setRanking(resRank.data);
          setCountryStats(resCountry.data);
        } catch (error) {
          console.error(error);
        }
      };
      fetchData();
    }, []);
  
    const nightData = comparison.find(c => c.train_type === 'night');
    const dayData = comparison.find(c => c.train_type === 'day');
  
    return (
      <div>
        <h1>📊 Statistiques</h1>
  
        {/* Comparaison Jour vs Nuit */}
        <h2>Comparaison Jour vs Nuit</h2>
        <div style={{ display: 'flex', gap: '30px' }}>
          <div style={{ border: '1px solid #333', padding: '15px' }}>
            <h3>🌙 Nuit</h3>
            <p>Passagers moyens: {nightData?.avg_passengers?.toLocaleString() || 0}</p>
            <p>CO₂/passager: {nightData?.avg_co2_per_passenger || 0} kg</p>
            <p>Efficacité: {nightData?.efficiency_score || 0}%</p>
          </div>
          <div style={{ border: '1px solid #333', padding: '15px' }}>
            <h3>☀️ Jour</h3>
            <p>Passagers moyens: {dayData?.avg_passengers?.toLocaleString() || 0}</p>
            <p>CO₂/passager: {dayData?.avg_co2_per_passenger || 0} kg</p>
            <p>Efficacité: {dayData?.efficiency_score || 0}%</p>
          </div>
        </div>
  
        {/* Classement CO₂ */}
        <h2>Classement CO₂ par pays</h2>
        <table border="1">
          <thead><tr><th>Rang</th><th>Pays</th><th>CO₂/passager (kg)</th></tr></thead>
          <tbody>
            {ranking.map((item, idx) => (
              <tr key={item.country_code}>
                <td>{idx + 1}</td>
                <td>{item.country_name}</td>
                <td>{item.avg_co2_per_passenger}</td>
              </tr>
            ))}
          </tbody>
        </table>
  
        {/* Évolution */}
        <h2>Évolution temporelle</h2>
        <table border="1">
          <thead><tr><th>Année</th><th>Passagers</th><th>CO₂</th><th>Trains nuit</th></tr></thead>
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
      </div>
    );
  };
  