import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = Cookies.get('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      Cookies.remove('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Auth API
export const authAPI = {
  register: (data: { email: string; password: string; full_name: string; organization_name?: string }) =>
    api.post('/auth/register', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  getCurrentUser: () =>
    api.get('/auth/me'),
};

// Campaign API
export const campaignAPI = {
  list: (skip = 0, limit = 100) =>
    api.get(`/campaigns/?skip=${skip}&limit=${limit}`),
  get: (id: number) =>
    api.get(`/campaigns/${id}`),
  create: (data: any) =>
    api.post('/campaigns/', data),
  delete: (id: number) =>
    api.delete(`/campaigns/${id}`),
};

// Creative API
export const creativeAPI = {
  upload: (campaignId: number, file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post(`/creatives/upload/${campaignId}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: (campaignId: number) =>
    api.get(`/creatives/campaign/${campaignId}`),
  delete: (id: number) =>
    api.delete(`/creatives/${id}`),
};

// Analytics API
export const analyticsAPI = {
  dashboard: () =>
    api.get('/analytics/dashboard'),
  roiMetrics: (campaignId?: number) =>
    api.get(`/analytics/roi-metrics${campaignId ? `?campaign_id=${campaignId}` : ''}`),
  budgetSimulation: (campaignId: number, newBudget: number) =>
    api.post('/analytics/budget-simulation', { campaign_id: campaignId, new_budget: newBudget }),
};

// ML API
export const mlAPI = {
  predictEngagement: (campaignId: number) =>
    api.post('/ml/predict-engagement', { campaign_id: campaignId }),
  getTrustScore: (creativeId: number) =>
    api.post('/ml/trust-score', { creative_id: creativeId }),
  analyzeCreative: (creativeId: number) =>
    api.post('/ml/analyze-creative', { creative_id: creativeId }),
};

// Documents API (RAG)
export const documentsAPI = {
  upload: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/documents/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  list: () =>
    api.get('/documents/'),
  delete: (id: number) =>
    api.delete(`/documents/${id}`),
  query: (query: string, nResults = 5) =>
    api.post('/documents/query', null, { params: { query, n_results: nResults } }),
};

// Chat API
export const chatAPI = {
  sendMessage: (message: string, useRAG = true, history: any[] = []) =>
    api.post('/chat/message', null, {
      params: { message, use_rag: useRAG },
      data: { conversation_history: history },
    }),
  getQuickInsights: (campaignId?: number) =>
    api.post('/chat/quick-insights', null, {
      params: campaignId ? { campaign_id: campaignId } : {},
    }),
};
