import axios from 'axios';
import { toast } from 'react-hot-toast';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api',
  timeout: 30000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request timestamp for debugging
    config.metadata = { startTime: new Date() };
    
    return config;
  },
  (error) => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and token refresh
apiClient.interceptors.response.use(
  (response) => {
    // Calculate request duration
    const duration = new Date() - response.config.metadata.startTime;
    
    // Log slow requests in development
    if (import.meta.env.DEV && duration > 5000) {
      console.warn(`Slow API request: ${response.config.url} took ${duration}ms`);
    }
    
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message);
      toast.error('Network error. Please check your connection.');
      return Promise.reject(error);
    }

    const { status, data } = error.response;

    // Handle different error types
    switch (status) {
      case 401:
        // Unauthorized - token expired or invalid
        if (!originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            // Try to refresh the token
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post('/auth/refresh', {
                refreshToken
              });
              
              const newToken = response.data.accessToken;
              localStorage.setItem('auth_token', newToken);
              
              // Retry the original request with new token
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return apiClient(originalRequest);
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
          }
        }
        
        // If refresh fails, redirect to login
        localStorage.removeItem('auth_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        toast.error('Session expired. Please login again.');
        break;

      case 403:
        // Forbidden
        toast.error('Access denied. You do not have permission for this action.');
        break;

      case 404:
        // Not found
        if (!originalRequest.url.includes('/health')) {
          toast.error('Resource not found.');
        }
        break;

      case 429:
        // Rate limited
        toast.error('Too many requests. Please wait and try again.');
        break;

      case 500:
        // Server error
        toast.error('Server error. Our team has been notified.');
        break;

      case 503:
        // Service unavailable
        toast.error('Service temporarily unavailable. Please try again later.');
        break;

      default:
        // Generic error handling
        const errorMessage = data?.message || error.message || 'An unexpected error occurred';
        
        if (status >= 400 && status < 500) {
          // Client errors
          console.error('Client error:', { status, url: originalRequest.url, data });
          if (!originalRequest._silent) {
            toast.error(errorMessage);
          }
        } else if (status >= 500) {
          // Server errors
          console.error('Server error:', { status, url: originalRequest.url, data });
          if (!originalRequest._silent) {
            toast.error('Server error occurred. Please try again.');
          }
        }
    }

    return Promise.reject(error);
  }
);

// API helper methods
export const api = {
  // Health check
  health: () => apiClient.get('/health'),

  // Authentication endpoints
  auth: {
    login: (credentials) => apiClient.post('/auth/login', credentials),
    register: (userData) => apiClient.post('/auth/register', userData),
    logout: () => apiClient.post('/auth/logout'),
    refresh: (refreshToken) => apiClient.post('/auth/refresh', { refreshToken }),
    me: () => apiClient.get('/auth/me'),
    forgotPassword: (email) => apiClient.post('/auth/forgot-password', { email }),
    resetPassword: (token, password) => apiClient.post('/auth/reset-password', { token, password }),
    updateProfile: (profileData) => apiClient.put('/auth/profile', profileData),
  },

  // 🔥 NEW: OAuth endpoints for auto-posting
  oauth: {
    getAuthUrl: (platform, options) => apiClient.post('/oauth/auth-url', { platform, ...options }),
    handleCallback: (platform, callbackData) => apiClient.post('/oauth/callback', { platform, ...callbackData }),
    getConnectedPlatforms: () => apiClient.get('/oauth/connected-platforms'),
    getPlatformStatus: (platform) => apiClient.get(`/oauth/platform/${platform}/status`),
    disconnect: (platform) => apiClient.delete(`/oauth/platform/${platform}/disconnect`),
    refreshToken: (platform) => apiClient.post(`/oauth/platform/${platform}/refresh-token`),
    testConnection: (platform) => apiClient.post(`/oauth/platform/${platform}/test`),
    updateSettings: (platform, settings) => apiClient.put(`/oauth/platform/${platform}/settings`, settings),
  },

  // 🔥 NEW: Auto-posting endpoints
  autoPosting: {
    getStatus: () => apiClient.get('/auto-posting/status'),
    start: () => apiClient.post('/auto-posting/start'),
    pause: () => apiClient.post('/auto-posting/pause'),
    stop: () => apiClient.post('/auto-posting/stop'),
    getStats: (timeframe) => apiClient.get('/auto-posting/stats', { params: { timeframe } }),
    getRecentPosts: (limit) => apiClient.get('/auto-posting/recent-posts', { params: { limit } }),
    getScheduled: () => apiClient.get('/auto-posting/scheduled'),
    updateSettings: (settings) => apiClient.put('/auto-posting/settings', settings),
    getSettings: () => apiClient.get('/auto-posting/settings'),
    forcePost: (data) => apiClient.post('/auto-posting/force-post', data),
    getLogs: (page, limit) => apiClient.get('/auto-posting/logs', { params: { page, limit } }),
  },

  // 🔥 NEW: Content generation endpoints
  content: {
    generate: (request) => apiClient.post('/content/generate', request),
    getRecent: (limit, page) => apiClient.get('/content/recent', { params: { limit, page } }),
    update: (id, content) => apiClient.put(`/content/${id}`, content),
    delete: (id) => apiClient.delete(`/content/${id}`),
    schedule: (data) => apiClient.post('/content/schedule', data),
    postNow: (data) => apiClient.post('/content/post-now', data),
    generateFromPrompt: (data) => apiClient.post('/content/generate-prompt', data),
    getTemplates: (domain) => apiClient.get('/content/templates', { params: { domain } }),
    generateHashtags: (data) => apiClient.post('/content/generate-hashtags', data),
    optimizeForPlatform: (data) => apiClient.post('/content/optimize', data),
    getTrending: (domain, platform) => apiClient.get('/content/trending', { params: { domain, platform } }),
  },

  // 🔥 NEW: Scheduler endpoints
  scheduler: {
    getSettings: () => apiClient.get('/scheduler/settings'),
    updateSettings: (settings) => apiClient.put('/scheduler/settings', settings),
    generateOptimalTimes: () => apiClient.post('/scheduler/generate-optimal-times'),
    getAnalytics: () => apiClient.get('/scheduler/analytics'),
    getPreview: (settings, days) => apiClient.post('/scheduler/preview', { settings, days }),
    getBestTimes: (platform, timeframe) => apiClient.get('/scheduler/best-times', { params: { platform, timeframe } }),
  },

  // Existing endpoints...
  platforms: {
    list: () => apiClient.get('/platforms'),
    connect: (platformData) => apiClient.post('/platforms/connect', platformData),
    disconnect: (platformId) => apiClient.delete(`/platforms/${platformId}`),
    test: (platformId) => apiClient.post(`/platforms/${platformId}/test`),
  },

  domains: {
    list: () => apiClient.get('/domains'),
    update: (domainData) => apiClient.put('/domains', domainData),
  },

  analytics: {
    getOverview: (timeframe) => apiClient.get('/analytics/overview', { params: { timeframe } }),
    getPlatformStats: (platform, timeframe) => apiClient.get(`/analytics/platform/${platform}`, { params: { timeframe } }),
    getEngagement: (timeframe) => apiClient.get('/analytics/engagement', { params: { timeframe } }),
    exportData: (format, timeframe) => apiClient.get('/analytics/export', { params: { format, timeframe } }),
  },

  billing: {
    getSubscription: () => apiClient.get('/billing/subscription'),
    getPlans: () => apiClient.get('/billing/plans'),
    subscribe: (planId, paymentMethod) => apiClient.post('/billing/subscribe', { planId, paymentMethod }),
    updatePaymentMethod: (paymentMethod) => apiClient.put('/billing/payment-method', paymentMethod),
    getInvoices: () => apiClient.get('/billing/invoices'),
    getUsage: () => apiClient.get('/billing/usage'),
  },

  settings: {
    get: () => apiClient.get('/settings'),
    update: (settings) => apiClient.put('/settings', settings),
    updatePassword: (passwordData) => apiClient.put('/settings/password', passwordData),
    deleteAccount: () => apiClient.delete('/settings/account'),
  },
};

// Export default axios instance for custom requests
export default apiClient;