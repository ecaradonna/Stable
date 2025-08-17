import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

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