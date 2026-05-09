// App.js
import './App.css';
import { BrowserRouter } from 'react-router-dom';
// Import des pages
import AppRoutes from './routes/index';

function App() {
  return (
    <BrowserRouter>
        <AppRoutes />
    </BrowserRouter>
  );
}

export default App;
