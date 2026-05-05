import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // à adapter selon ton backend

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getTrajets = (filters = {}) => {
  return api.get('/trajets', { params: filters });
};

export const getTrajetById = (id) => {
  return api.get(`/trajets/${id}`);
};

export const getStatsVolumes = () => {
  return api.get('/stats/volumes');
};

export const getHealth = () => {
  return api.get('/health');
};