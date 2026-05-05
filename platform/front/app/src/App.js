import './App.css';
import { BrowserRouter, Routes, Route } from 'react-router';
import HomePage from './pages/HomePage';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/externe/HomePage" element={<h1>Page client</h1>} />
        <Route path="/interne/HomePage" element={<h1>Page admin</h1>} />
      </Routes>
    </BrowserRouter>
  );
}
export default App;
