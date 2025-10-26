import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const chatAPI = {
  sendMessage: (data) => api.post('/chat/query', data),
  createSession: (data) => api.post('/chat/sessions', data),
  getSession: (sessionId) => api.get(`/chat/sessions/${sessionId}`),
  getMessages: (sessionId) => api.get(`/chat/sessions/${sessionId}/messages`),
  sendVoiceQuery: (formData) => api.post('/voice/voice-query', formData),
  uploadDocument: (formData) => api.post('/documents/upload', formData),
};

export const documentAPI = {
  upload: (formData) => api.post('/documents/upload', formData),
  getAll: () => api.get('/documents/'),
  getById: (id) => api.get(`/documents/${id}`),
  delete: (id) => api.delete(`/documents/${id}`),
  process: (id) => api.post(`/documents/${id}/process`),
};

export const analyticsAPI = {
  getRatios: (data) => api.post('/analytics/ratios', data),
  getForecast: (data) => api.post('/analytics/forecast', data),
  getTrends: (data) => api.post('/analytics/trends', data),
  getKPIs: (data) => api.post('/analytics/kpis', data),
};

export const voiceAPI = {
  speechToText: (formData) => api.post('/voice/speech-to-text', formData),
  textToSpeech: (data) => api.post('/voice/text-to-speech', data),
  processVoiceQuery: (formData) => api.post('/voice/voice-query', formData),
  analyzeSentiment: (formData) => api.post('/voice/voice-sentiment', formData),
  createSummary: (data) => api.post('/voice/voice-summary', data),
  getVoices: () => api.get('/voice/voices'),
  getLanguages: () => api.get('/voice/languages'),
  getStatus: () => api.get('/voice/voice-status'),
};

export const faqAPI = {
  search: (query, category, limit) => api.get('/faq/search', {
    params: { query, category, limit }
  }),
  getById: (id) => api.get(`/faq/${id}`),
  getByCategory: (category) => api.get(`/faq/category/${category}`),
  getAll: () => api.get('/faq/'),
  getCategories: () => api.get('/faq/categories/list'),
  getSuggestions: (context) => api.get('/faq/suggestions/questions', {
    params: { context }
  }),
  add: (data) => api.post('/faq/add', data),
  update: (id, data) => api.put(`/faq/${id}`, data),
  delete: (id) => api.delete(`/faq/${id}`),
  export: () => api.get('/faq/export/json'),
  import: (data) => api.post('/faq/import/json', data),
  getQuickStart: () => api.get('/faq/help/quick-start'),
};

export const healthAPI = {
  check: () => api.get('/health'),
};

export default api;
