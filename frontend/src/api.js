import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getReports = async () => {
  const response = await api.get('/api/reports');
  return response.data;
};

export const runReport = async (reportId, params = {}) => {
  const response = await api.post(`/api/reports/${reportId}/run`, { params });
  return response.data;
};

export const getRuns = async (limit = 20, offset = 0) => {
  const response = await api.get('/api/runs', { params: { limit, offset } });
  return response.data;
};

export const getRun = async (runId) => {
  const response = await api.get(`/api/runs/${runId}`);
  return response.data;
};

export const downloadReport = (runId) => {
  window.open(`${API_URL}/api/runs/${runId}/download`, '_blank');
};

export default api;
