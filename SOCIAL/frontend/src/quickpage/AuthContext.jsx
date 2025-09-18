import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) ? import.meta.env.VITE_API_URL : (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL) ? process.env.REACT_APP_API_URL : 'https://agentic-u5lx.onrender.com';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(null);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const savedToken = localStorage.getItem('auth_token') || localStorage.getItem('token') || localStorage.getItem('authToken');
        
        if (savedToken) {
          setToken(savedToken);
          
          try {
            const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
              headers: { 'Authorization': `Bearer ${savedToken}`, 'Content-Type': 'application/json' },
              timeout: 10000
            });
            
            if (response.ok) {
              const data = await response.json();
              if (data.success && data.user) {
                setUser(data.user);
                setIsAuthenticated(true);
                console.log('User authenticated:', data.user.email);
              } else {
                clearTokens();
              }
            } else {
              clearTokens();
            }
          } catch (apiError) {
            console.warn('Auth API check failed, using cached token:', apiError.message);
            // In case of network error, allow cached token for offline functionality
            const cachedUser = localStorage.getItem('cached_user');
            if (cachedUser) {
              try {
                const userData = JSON.parse(cachedUser);
                setUser(userData);
                setIsAuthenticated(true);
                console.log('Using cached user data');
              } catch (parseError) {
                clearTokens();
              }
            } else {
              clearTokens();
            }
          }
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        clearTokens();
      } finally {
        setLoading(false);
      }
    };

    const clearTokens = () => {
      ['auth_token', 'token', 'authToken', 'cached_user'].forEach(key => localStorage.removeItem(key));
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      
      if (data.success && data.token) {
        const authToken = data.token;
        const userData = { id: data.user_id, email: data.email, name: data.name, reddit_connected: data.reddit_connected, reddit_username: data.reddit_username };
        
        setToken(authToken);
        setUser(userData);
        setIsAuthenticated(true);
        
        localStorage.setItem('auth_token', authToken);
        localStorage.setItem('cached_user', JSON.stringify(userData));
        
        return { success: true, user: data };
      } else {
        return { success: false, error: data.message || data.error || 'Login failed' };
      }
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: 'Login failed: ' + error.message };
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();
      
      if (data.success && data.token) {
        const authToken = data.token;
        const userData = { id: data.user_id, email: data.email, name: data.name, reddit_connected: false, reddit_username: null };
        
        setToken(authToken);
        setUser(userData);
        setIsAuthenticated(true);
        
        localStorage.setItem('auth_token', authToken);
        localStorage.setItem('cached_user', JSON.stringify(userData));
        
        return { success: true, user: data };
      } else {
        return { success: false, error: data.message || data.error || 'Registration failed' };
      }
    } catch (error) {
      console.error('Registration failed:', error);
      return { success: false, error: 'Registration failed: ' + error.message };
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    ['auth_token', 'token', 'authToken', 'cached_user', 'reddit_username', 'reddit_session_id'].forEach(key => localStorage.removeItem(key));
  };

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }));
    if (userData && typeof userData === 'object') {
      localStorage.setItem('cached_user', JSON.stringify({ ...user, ...userData }));
    }
  };

  const makeAuthenticatedRequest = async (endpoint, options = {}) => {
    if (!token) {
      throw new Error('No authentication token');
    }

    const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json', ...(options.headers || {}) };
    const requestOptions = { ...options, headers };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions);

      if (response.status === 401) {
        logout();
        throw new Error('Authentication expired');
      }

      return response;
    } catch (error) {
      if (error.message === 'Authentication expired') {
        throw error;
      }
      console.error('API request failed:', error);
      throw new Error('Network request failed: ' + error.message);
    }
  };

  const value = { isAuthenticated, user, token, loading, login, register, logout, updateUser, makeAuthenticatedRequest };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};