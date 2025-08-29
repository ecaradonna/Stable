import axios from 'axios';

// Dynamic backend URL detection
const getBackendURL = () => {
  // Check if we're in development (localhost)
  if (window.location.hostname === 'localhost') {
  if (window.location.hostname === 'localhost') {
    return 'http://localhost:8001';
  }
  // Always use environment variable if available for production
  const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta?.env?.REACT_APP_BACKEND_URL;
  if (envBackendUrl) {
    return envBackendUrl;
  }
  // Use same protocol and hostname as current page
  const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}`;
  }
  
  // For production/preview, use the environment variable first
  const envBackendUrl = process.env.REACT_APP_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL;
  if (envBackendUrl) {
    return envBackendUrl;
  }
  
  // Fallback: construct backend URL from current window location (always use HTTPS in production)
  const protocol = window.location.protocol === 'https:' ? 'https:' : window.location.protocol;
  const hostname = window.location.hostname;
  return `${protocol}//${hostname}`;
};

const BACKEND_URL = getBackendURL();
const API = `${BACKEND_URL}/api`;

console.log('API Service using:', API); // Debug log

// Create axios instance with default config
const api = axios.create({
  baseURL: API,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

// Yield API endpoints
export const yieldsApi = {
  // Get all current yields
  getAllYields: (refresh = false) => 
    api.get('/yields', { params: { refresh } }),
    
  // Get specific stablecoin yield
  getStablecoinYield: (stablecoin) => 
    api.get(`/yields/${stablecoin}`),
    
  // Get historical data
  getHistoricalData: (stablecoin, days = 7) => 
    api.get(`/yields/${stablecoin}/history`, { params: { days } }),
    
  // Get yield summary stats
  getSummary: () => 
    api.get('/yields/stats/summary'),
    
  // Compare two stablecoins
  compareYields: (coin1, coin2) => 
    api.get(`/yields/compare/${coin1}/${coin2}`),
    
  // Refresh yield data
  refreshYields: () => 
    api.post('/yields/refresh'),
};

// User API endpoints
export const usersApi = {
  // Join waitlist
  joinWaitlist: (data) => 
    api.post('/users/waitlist', data),
    
  // Subscribe to newsletter
  subscribeNewsletter: (data) => 
    api.post('/users/newsletter', data),
    
  // Get user data
  getUser: (email) => 
    api.get(`/users/${email}`),
    
  // Update user preferences
  updateUser: (email, data) => 
    api.put(`/users/${email}`, data),
    
  // Get user statistics
  getUserStats: () => 
    api.get('/users/stats/summary'),
    
  // Unsubscribe
  unsubscribe: (email, signupType) => 
    api.delete(`/users/${email}/${signupType}`),
};

// AI API endpoints
export const aiApi = {
  // Chat with AI
  chat: (data) => 
    api.post('/ai/chat', data),
    
  // Get sample queries
  getSamples: () => 
    api.get('/ai/chat/samples'),
    
  // Create alert
  createAlert: (data) => 
    api.post('/ai/alerts', data),
    
  // Get user alerts
  getUserAlerts: (email) => 
    api.get(`/ai/alerts/${email}`),
    
  // Delete alert
  deleteAlert: (alertId, userEmail) => 
    api.delete(`/ai/alerts/${alertId}`, { params: { user_email: userEmail } }),
    
  // Get alert conditions
  getAlertConditions: () => 
    api.get('/ai/alerts/conditions'),
    
  // Check alerts manually
  checkAlerts: () => 
    api.post('/ai/alerts/check'),
};

// Health check
export const healthApi = {
  check: () => api.get('/health'),
  info: () => api.get('/'),
};

export default api;