import { useEffect, useState } from 'react';
import { getGeographicCoverage, getNightTrainsOnly, getDayTrainsOnly } from '../../services/api';

export default function MapPage() {
  const [coverage, setCoverage] = useState(null);
  const [nightTrains, setNightTrains] = useState([]);
  const [dayTrains, setDayTrains] = useState([]);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resCoverage, resNight, resDay] = await Promise.all([
          getGeographicCoverage(), getNightTrainsOnly(), getDayTrainsOnly()
        ]);
        setCoverage(resCoverage.data);
        setNightTrains(resNight.data);
        setDayTrains(resDay.data);
      } catch (error) {
        console.error(error);
      }
    };
    fetchData();
  }, []);
  
  return (
    <div>
      <h1>🗺️ Carte des trains</h1>  
      <h3>Pays couverts : {coverage?.total_countries_covered || 0}</h3>
        
      <div style={{ display: 'flex', gap: '40px' }}>
        {/* Trains de nuit */}
        <div>
          <h3>🌙 Trains de nuit ({nightTrains.length})</h3>
          <ul>
            {nightTrains.slice(0, 20).map(train => (
              <li key={train.fact_id}>
                {train.route_id} - {train.operator_name} ({train.country_name})
              </li>
            ))}
          </ul>
        </div>
  
        {/* Trains de jour */}
        <div>
          <h3>☀️ Trains de jour ({dayTrains.length})</h3>
          <ul>
            {dayTrains.slice(0, 20).map(train => (
              <li key={train.fact_id}>
                {train.route_id} - {train.operator_name} ({train.country_name})
              </li>
            ))}
          </ul>
        </div>
      </div>
  
      {/* Liste pays avec nombre de trains */}
      <h3>Détail par pays</h3>
      <ul>
        {coverage?.coverage_by_country?.map(country => (
          <li key={country.country_code}>
            {country.country_name} : {country.train_count} trains
          </li>
        ))}
      </ul>
    </div>
  );
};
  
  