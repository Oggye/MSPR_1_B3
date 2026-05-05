import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router';
import HomePage from './pages/HomePage';
import ExterneHomePage from './pages/externe/HomePage';
import InterneHomePage from './pages/interne/HomePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/externe/HomePage" element={<ExterneHomePage />} />
        <Route path="/interne/HomePage" element={<InterneHomePage />} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;
