import { useEffect, useState } from 'react';
import { getOperators, getOperatorStats } from '../../services/api';

export default function OperateurPage() {
    const [operators, setOperators] = useState([]);
    const [selectedStats, setSelectedStats] = useState(null);
  
    useEffect(() => {
      const fetchOperators = async () => {
        try {
          const res = await getOperators();
          setOperators(res.data);
        } catch (error) {
          console.error(error);
        }
      };
      fetchOperators();
    }, []);
  
    const handleSelectOperator = async (operatorId) => {
      try {
        const res = await getOperatorStats(operatorId);
        setSelectedStats(res.data);
      } catch (error) {
        console.error(error);
      }
    };
  
    return (
      <div>
        <h1>🏢 Opérateurs ferroviaires</h1>
        
        <div style={{ display: 'flex', gap: '30px' }}>
          {/* Liste des opérateurs */}
          <div style={{ border: '1px solid #ccc', padding: '15px', minWidth: '200px' }}>
            <h3>Liste</h3>
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {operators.map(op => (
                <li 
                  key={op.operator_id} 
                  onClick={() => handleSelectOperator(op.operator_id)}
                  style={{ cursor: 'pointer', padding: '8px', borderBottom: '1px solid #eee' }}
                >
                  {op.operator_name}
                </li>
              ))}
            </ul>
          </div>
  
          {/* Détails opérateur sélectionné */}
          <div style={{ border: '1px solid #ccc', padding: '15px', flex: 1 }}>
            <h3>Détails</h3>
            {selectedStats ? (
              <div>
                <p><strong>{selectedStats.operator_name}</strong></p>
                <p>🚆 Total trains : {selectedStats.total_trains}</p>
                <p>🌙 Trains de nuit : {selectedStats.night_trains}</p>
                <p>☀️ Trains de jour : {selectedStats.day_trains}</p>
                <p>📏 Distance totale : {selectedStats.distance_totale_km?.toLocaleString()} km</p>
                <p>⏱️ Durée moyenne : {selectedStats.duree_moyenne_min} min</p>
                <p>🌍 Pays desservis : {selectedStats.countries_served?.join(', ')}</p>
              </div>
            ) : (
              <p>Sélectionnez un opérateur</p>
            )}
          </div>
        </div>
      </div>
    );
  };
  