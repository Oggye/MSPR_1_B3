// fichier : platform/front/app/src/services/api.js     (ajouter les nouvelles fonctions)


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

export const getCo2Ranking = (limit = null) => {
  const params = {};

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/statistics/co2-ranking', { params });
};

export const getDashboardKpis = () => {
  return api.get('/dashboard/kpis');
};

// Carte
export const getNightTrains = (skip = 0, limit = null, filters = {}) => {
  const params = { skip, ...filters };

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/night-trains', { params });
};

export const getNightTrainsOnly = (filters = {}) => {
  const params = { ...filters };

  if (params.limit === undefined) {
    delete params.limit;
  }

  return api.get('/night-trains/night', { params });
};

export const getDayTrainsOnly = (filters = {}) => {
  const params = { ...filters };

  if (params.limit === undefined) {
    delete params.limit;
  }

  return api.get('/night-trains/day', { params });
};

export const getGeographicCoverage = () => {
  return api.get('/geographic/coverage');
};

// Liste des trajets
export const getAllTrains = (skip = 0, limit = null, filters = {}) => {
  const params = { skip, ...filters };

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/night-trains', { params });
};

export const getTrainsByCountry = (countryCode, skip = 0, limit = null) => {
  const params = { country_code: countryCode, skip };

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/night-trains', { params });
};

export const getTrainsByOperator = (operatorName, skip = 0, limit = null) => {
  const params = { operator_name: operatorName, skip };

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/night-trains', { params });
};

export const getTrainsByYear = (year, skip = 0, limit = null) => {
  const params = { year, skip };

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/night-trains', { params });
};

export const getCountries = (skip = 0, limit = null) => {
  const params = { skip };

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/countries', { params });
};

// Statistiques avancées
export const getTrainTypeComparison = () => {
  return api.get('/analysis/train-types-comparison');
};

export const getPolicyRecommendations = () => {
  return api.get('/analysis/policy-recommendations');
};

export const getOperatorStats = (operatorId) => {
  return api.get(`/operators/${operatorId}/stats`);
};

export const getCountryStats = (filters = {}, skip = 0, limit = null) => {
  const params = { skip, ...filters };

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/countries/stats', { params });
};

// Opérateurs
export const getOperators = (skip = 0, limit = null) => {
  const params = { skip };

  if (limit !== null) {
    params.limit = limit;
  }

  return api.get('/operators', { params });
};

export const getOperatorById = (id) => {
  return api.get(`/operators/${id}/stats`);
};

// Prédictions IA — Classification (déclin ferroviaire)
// payload : { country, year, co2_emissions, co2_per_passenger, co2_lag1, passengers_lag1, passengers_lag2 }
export const predictClassification = (payload) => {
  return api.post('/predict/classification', payload);
};

// Prédictions IA — Régression (volume de passagers)
// payload : identique à predictClassification
export const predictRegression = (payload) => {
  return api.post('/predict/regression', payload);
};

export const getHealth = () => {
  return api.get('/health');
};

export default api;
