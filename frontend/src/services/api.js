import axios from 'axios';

// Mobile Safari compatible backend URL detection
const getBackendURL = () => {
  // Try multiple methods to get environment variable (mobile Safari compatible)
  let envBackendUrl;
  
  try {
    // Method 1: Check if process exists (Node.js environments)
    if (typeof process !== 'undefined' && process.env) {
      envBackendUrl = process.env.REACT_APP_BACKEND_URL;
    }
  } catch (e) {
    // Process not available in mobile Safari
  }
  
  try {
    // Method 2: Vite/modern bundlers
    if (typeof import.meta !== 'undefined' && import.meta.env) {
      envBackendUrl = envBackendUrl || import.meta.env.REACT_APP_BACKEND_URL;
    }
  } catch (e) {
    // import.meta not available
  }
  
  try {
    // Method 3: Check window object for injected env vars (mobile Safari fallback)
    if (typeof window !== 'undefined' && window.__ENV) {
      envBackendUrl = envBackendUrl || window.__ENV.REACT_APP_BACKEND_URL;
    }
  } catch (e) {
    // Window env not available
  }
  
  // If environment variable found, use it
  if (envBackendUrl && envBackendUrl !== 'undefined') {
    console.log('Using environment backend URL:', envBackendUrl);
    return envBackendUrl;
  }
  
  // Mobile Safari fallback: construct from current location
  const currentProtocol = typeof window !== 'undefined' ? window.location.protocol : 'http:';
  const currentHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
  
  // Check if we're in development (localhost)
  if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    const backendUrl = 'http://localhost:8001';
    console.log('Using localhost backend URL:', backendUrl);
    return backendUrl;
  }
  
  // Production fallback: same domain with HTTPS
  const backendUrl = `${currentProtocol}//${currentHost}`;
  console.log('Using production backend URL:', backendUrl);
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