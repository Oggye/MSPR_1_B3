import { Link, Outlet } from 'react-router-dom';
import { useState, useEffect } from 'react';

export default function LayoutExterne() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth >= 768) {
        setIsMobileMenuOpen(false);
      }
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const menuItems = [
    { path: "/externe/HomePage", label: "📊 Dashboard", icon: "📊" },
    { path: "/externe/Trajets", label: "📋 Trajets", icon: "📋" },
    { path: "/externe/Map", label: "🗺️ Carte", icon: "🗺️" },
    { path: "/externe/Statistique", label: "📈 Statistiques", icon: "📈" },
    { path: "/externe/Operateur", label: "🏢 Opérateurs", icon: "🏢" }
  ];

  const sidebarStyles = {
    position: isMobile ? 'fixed' : 'relative',
    width: isMobile ? (isMobileMenuOpen ? '260px' : '0px') : '260px',
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    color: 'white',
    padding: isMobile ? (isMobileMenuOpen ? '24px 16px' : '0px') : '24px 16px',
    minHeight: '100vh',
    boxShadow: '2px 0 8px rgba(0,0,0,0.1)',
    transition: 'all 0.3s ease',
    overflow: 'hidden',
    zIndex: 1000,
    left: 0,
    top: 0
  };

  const overlayStyles = {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0,0,0,0.5)',
    zIndex: 999,
    display: isMobile && isMobileMenuOpen ? 'block' : 'none'
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      {/* Overlay pour mobile */}
      <div style={overlayStyles} onClick={() => setIsMobileMenuOpen(false)} />
      
      {/* MENU LATÉRAL CLIENT */}
      <aside style={sidebarStyles}>
        <div style={{ 
          textAlign: 'center', 
          marginBottom: 32,
          opacity: isMobile && !isMobileMenuOpen ? 0 : 1,
          transition: 'opacity 0.2s ease'
        }}>
          <h2 style={{ margin: 0, fontSize: 24 }}>🚆 ObRail</h2>
          <p style={{ fontSize: 12, opacity: 0.8, marginTop: 8 }}>Espace Client</p>
        </div>
        
        <ul style={{ 
          listStyle: 'none', 
          padding: 0, 
          margin: 0,
          opacity: isMobile && !isMobileMenuOpen ? 0 : 1,
          transition: 'opacity 0.2s ease 0.1s'
        }}>
          {menuItems.map((item, index) => (
            <li key={index} style={{ marginBottom: 12 }}>
              <Link 
                to={item.path} 
                onClick={() => isMobile && setIsMobileMenuOpen(false)}
                style={{ 
                  color: 'white', 
                  textDecoration: 'none',
                  display: 'block',
                  padding: '10px 16px',
                  borderRadius: 8,
                  transition: 'background 0.2s ease',
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(255,255,255,0.1)'}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </aside>

      {/* CONTENU PRINCIPAL */}
      <main style={{ 
        flex: 1, 
        padding: isMobile ? '16px' : '24px', 
        background: '#f5f7fa',
        width: '100%',
        overflowX: 'auto'
      }}>
        {/* Bouton menu mobile */}
        {isMobile && (
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            style={{
              position: 'fixed',
              top: '16px',
              left: '16px',
              zIndex: 1001,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              border: 'none',
              borderRadius: '8px',
              color: 'white',
              padding: '10px 12px',
              cursor: 'pointer',
              fontSize: '20px',
              boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
            }}
          >
            ☰
          </button>
        )}
        
        <div style={{ 
          marginTop: isMobile ? '50px' : '0',
          overflowX: 'auto'
        }}>
          <Outlet />
        </div>
      </main>

      <style>{`
        @media (max-width: 768px) {
          aside a {
            white-space: nowrap;
          }
        }
        
        @media (max-width: 480px) {
          main {
            padding: 12px !important;
          }
        }
        
        /* Amélioration du scroll sur mobile */
        ::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        
        ::-webkit-scrollbar-track {
          background: #f1f1f1;
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb {
          background: #888;
          border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
          background: #555;
        }
      `}</style>
    </div>
  );
}
