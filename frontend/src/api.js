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

export const runReport = async (reportId, params = {}, outputFormat = 'xlsx') => {
  const response = await api.post(`/api/reports/${reportId}/run`, { 
    params,
    output_format: outputFormat,
  });
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

export const subscribeToRunStatus = (runId, onStatusUpdate) => {
  /**
   * Subscribe to real-time status updates via SSE.
   * Returns an unsubscribe function.
   */
  const eventSource = new EventSource(`${API_URL}/api/runs/${runId}/stream`);
  
  eventSource.addEventListener('status_update', (event) => {
    const data = JSON.parse(event.data);
    onStatusUpdate(data);
    
    // Auto-close when terminal state
    if (data.status === 'completed' || data.status === 'failed') {
      eventSource.close();
    }
  });
  
  eventSource.onerror = (error) => {
    console.error('SSE connection error:', error);
    eventSource.close();
  };
  
  return () => eventSource.close();
};

export default api;
