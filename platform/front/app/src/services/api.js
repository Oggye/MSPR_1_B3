import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// dashboard
export const getSummary = () => {
  return api.get('/night-trains/summary');
};

export const getTimeline = () => {
  return api.get('/statistics/timeline');
};

export const getCo2Ranking = (limit = 10) => {
  return api.get('/statistics/co2-ranking', { params: { limit } });
};

export const getDashboardKpis = () => {
  return api.get('/dashboard/kpis');
};

// Carte
export const getNightTrains = (filters = {}) => {
  return api.get('/night-trains', { params: filters });
};

export const getNightTrainsOnly = (filters = {}) => {
  return api.get('/night-trains/night', { params: filters });
};

export const getDayTrainsOnly = (filters = {}) => {
  return api.get('/night-trains/day', { params: filters });
};

export const getGeographicCoverage = () => {
  return api.get('/geographic/coverage');
};

// Liste des trajets
export const getAllTrains = (skip = 0, limit = 20, filters = {}) => {
  return api.get('/night-trains', { 
    params: { skip, limit, ...filters } 
  });
};

export const getTrainsByCountry = (countryCode, skip = 0, limit = 20) => {
  return api.get('/night-trains', { 
    params: { country_code: countryCode, skip, limit } 
  });
};

export const getTrainsByOperator = (operatorName, skip = 0, limit = 20) => {
  return api.get('/night-trains', { 
    params: { operator_name: operatorName, skip, limit } 
  });
};

export const getTrainsByYear = (year, skip = 0, limit = 20) => {
  return api.get('/night-trains', { 
    params: { year, skip, limit } 
  });
};

export const getCountries = () => {
  return api.get('/countries');
};

// Statistiques avancées
export const getTrainTypeComparison = () => {
  return api.get('/analysis/train-types-comparison');
};

export const getOperatorStats = (operatorId) => {
  return api.get(`/operators/${operatorId}/stats`);
};

export const getCountryStats = (filters = {}) => {
  return api.get('/countries/stats', { params: filters });
};

// Opérateurs
export const getOperators = (skip = 0, limit = 100) => {
  return api.get('/operators', { params: { skip, limit } });
};

export const getOperatorById = (id) => {
  return api.get(`/operators/${id}/stats`);
};

export const getHealth = () => {
  return api.get('/health');
};

export default api;