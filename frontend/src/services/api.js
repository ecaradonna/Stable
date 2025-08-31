import axios from 'axios';

// Force localhost backend for AI to work properly
const getBackendURL = () => {
  // ALWAYS use localhost:8001 for development to ensure AI works
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      console.log('Using hardcoded localhost backend URL for AI compatibility');
      return 'http://localhost:8001';
    }
  }
  
  // Try environment variables for production
  let envBackendUrl;
  
  try {
    if (typeof process !== 'undefined' && process.env) {
      envBackendUrl = process.env.REACT_APP_BACKEND_URL;
    }
  } catch (e) {}
  
  try {
    if (typeof import.meta !== 'undefined' && import.meta.env) {
      envBackendUrl = envBackendUrl || import.meta.env.REACT_APP_BACKEND_URL;
    }
  } catch (e) {}
  
  // Only use env var if it's localhost or a valid URL
  if (envBackendUrl && (envBackendUrl.includes('localhost:8001') || envBackendUrl.startsWith('https://'))) {
    console.log('Using environment backend URL:', envBackendUrl);
    return envBackendUrl;
  }
  
  // Final fallback to localhost
  const backendUrl = 'http://localhost:8001';
  console.log('Using fallback backend URL:', backendUrl);
  return backendUrl;
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