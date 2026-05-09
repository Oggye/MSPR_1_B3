import { Link, Outlet } from 'react-router-dom';

export default function LayoutExterne() {
  return (
    <div style={{ display: 'flex' }}>
      {/* MENU LATÉRAL CLIENT */}
      <aside style={{ 
        width: 260,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        padding: '24px 16px',
        minHeight: '100vh',
        boxShadow: '2px 0 8px rgba(0,0,0,0.1)'
      }}>
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <h2 style={{ margin: 0, fontSize: 24 }}>🚆 ObRail</h2>
          <p style={{ fontSize: 12, opacity: 0.8, marginTop: 8 }}>Espace Client</p>
        </div>
        
        <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
          <li style={{ marginBottom: 12 }}>
            <Link to="/externe/HomePage" style={{ 
              color: 'white', 
              textDecoration: 'none',
              display: 'block',
              padding: '10px 16px',
              borderRadius: 8,
            }}>
              📊 Dashboard
            </Link>
          </li>
          <li style={{ marginBottom: 12 }}>
            <Link to="/externe/Trajets" style={{ 
              color: 'white', 
              textDecoration: 'none',
              display: 'block',
              padding: '10px 16px',
              borderRadius: 8
            }}>
              📋 Trajets
            </Link>
          </li>
          <li style={{ marginBottom: 12 }}>
            <Link to="/externe/Map" style={{ 
              color: 'white', 
              textDecoration: 'none',
              display: 'block',
              padding: '10px 16px',
              borderRadius: 8
            }}>
              🗺️ Carte
            </Link>
          </li>
          <li style={{ marginBottom: 12 }}>
            <Link to="/externe/Statistique" style={{ 
              color: 'white', 
              textDecoration: 'none',
              display: 'block',
              padding: '10px 16px',
              borderRadius: 8
            }}>
              📈 Statistiques
            </Link>
          </li>
          <li style={{ marginBottom: 12 }}>
            <Link to="/externe/Operateur" style={{ 
              color: 'white', 
              textDecoration: 'none',
              display: 'block',
              padding: '10px 16px',
              borderRadius: 8
            }}>
              🏢 Opérateurs
            </Link>
          </li>
        </ul>
      </aside>

      {/* CONTENU PRINCIPAL */}
      <main style={{ flex: 1, padding: 24, background: '#f5f7fa' }}>
        <Outlet />
      </main>
    </div>
  );
}
