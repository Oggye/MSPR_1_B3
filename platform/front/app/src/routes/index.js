// J'importe les outils de navigation de React Router
import { Routes, Route } from 'react-router-dom';

// IMPORT DES LAYOUTS
import LayoutExterne from '../layouts/LayoutExterne';
import LayoutInterne from '../layouts/LayoutInterne';

// IMPORT Page d'acceuil
import HomePage from '../pages/HomePage';

// IMPORT DES PAGES EXTERNES (partenaire)
import ExterneHomePage from '../pages/externe/HomePage';
import MapPage from '../pages/externe/MapPage';
import TrainPage from '../pages/externe/TrajetsPage';
import StatisticsPage from '../pages/externe/StatisticsPage';
import OperatorsPage from '../pages/externe/OperatorsPage';

// IMPORT DES PAGES INTERNES (admin)
import InterneHomePage from '../pages/interne/HomePage';

// Je crée un composant qui contient toutes les routes
export default function AppRoutes() {
  return (
    // <Routes> = conteneur qui contient toutes les routes
    <Routes>
        {/* path = l'URL, element = la page à afficher */}
        {/* Page d'accueil */}
        <Route path="/" element={<HomePage />} />

        {/* ROUTES EXTERNES (avec LayoutExterne) */}
        <Route path="/externe" element={<LayoutExterne />}>
            <Route path="HomePage" element={<ExterneHomePage />} />
            <Route path="Map" element={<MapPage />} />
            <Route path="Trajets" element={<TrainPage />} />
            <Route path="Statistique" element={<StatisticsPage />} />
            <Route path="Operateur" element={<OperatorsPage />} />
        </Route>

        {/* ROUTES INTERNES (avec LayoutInterne) */}
        <Route path="/interne" element={<LayoutInterne />}>
            <Route path="HomePage" element={<InterneHomePage />} />
        </Route>
    </Routes>
  );
}