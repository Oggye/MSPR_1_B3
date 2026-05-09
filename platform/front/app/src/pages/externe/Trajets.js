// pages/TrainsList.jsx
import { useEffect, useState } from 'react';
import { getAllTrains, getCountries, getOperators } from '../../services/api';

const TrainsList = () => {
  const [trains, setTrains] = useState([]);
  const [countries, setCountries] = useState([]);
  const [operators, setOperators] = useState([]);
  const [filters, setFilters] = useState({ country_code: '', operator_name: '', year: '' });

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resTrains, resCountries, resOperators] = await Promise.all([
          getAllTrains(), getCountries(), getOperators()
        ]);
        setTrains(resTrains.data);
        setCountries(resCountries.data);
        setOperators(resOperators.data);
      } catch (error) {
        console.error(error);
      }
    };
    fetchData();
  }, []);

  const formatDuration = (minutes) => {
    if (!minutes) return 'N/A';
    return `${Math.floor(minutes / 60)}h ${minutes % 60}min`;
  };

  return (
    <div>
      <h1>📋 Liste des trajets</h1>

      {/* Filtres simples */}
      <div style={{ display: 'flex', gap: '10px', marginBottom: '20px' }}>
        <select onChange={(e) => setFilters({...filters, country_code: e.target.value})}>
          <option value="">Tous pays</option>
          {countries.map(c => <option key={c.country_code} value={c.country_code}>{c.country_name}</option>)}
        </select>
        <select onChange={(e) => setFilters({...filters, operator_name: e.target.value})}>
          <option value="">Tous opérateurs</option>
          {operators.map(op => <option key={op.operator_id} value={op.operator_name}>{op.operator_name}</option>)}
        </select>
        <select onChange={(e) => setFilters({...filters, year: e.target.value})}>
          <option value="">Toutes années</option>
          <option value="2024">2024</option>
          <option value="2023">2023</option>
        </select>
      </div>

      {/* Tableau des trajets */}
      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Type</th>
            <th>Route</th>
            <th>Opérateur</th>
            <th>Pays</th>
            <th>Année</th>
            <th>Distance</th>
            <th>Durée</th>
          </tr>
        </thead>
        <tbody>
          {trains.filter(train => {
            if (filters.country_code && train.country_code !== filters.country_code) return false;
            if (filters.operator_name && train.operator_name !== filters.operator_name) return false;
            if (filters.year && train.year !== parseInt(filters.year)) return false;
            return true;
          }).map(train => (
            <tr key={train.fact_id}>
              <td>{train.is_night ? '🌙 Nuit' : '☀️ Jour'}</td>
              <td>{train.route_id || '-'}</td>
              <td>{train.operator_name}</td>
              <td>{train.country_name}</td>
              <td>{train.year}</td>
              <td>{train.distance_km ? `${train.distance_km} km` : '-'}</td>
              <td>{formatDuration(train.duration_min)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TrainsList;