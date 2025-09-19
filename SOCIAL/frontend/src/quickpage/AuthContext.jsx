import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();
const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'https://agentic-u5lx.onrender.com';

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
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
        const savedToken = localStorage.getItem('auth_token') || localStorage.getItem('token');
        const cachedUser = localStorage.getItem('user') || localStorage.getItem('cached_user');
        
        if (savedToken && cachedUser) {
          try {
            const userData = JSON.parse(cachedUser);
            setUser(userData); setToken(savedToken); setIsAuthenticated(true);
            console.log('User restored:', userData.email);
          } catch (parseError) {
            console.error('Parse error:', parseError);
            clearTokens();
          }
        } else { clearTokens(); }
      } catch (error) {
        console.error('Auth init failed:', error);
        clearTokens();
      } finally { setLoading(false); }
    };

    const clearTokens = () => {
      ['auth_token', 'token', 'authToken', 'cached_user', 'user'].forEach(key => localStorage.removeItem(key));
      setToken(null); setUser(null); setIsAuthenticated(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      console.log('Login attempt:', { email, apiUrl: API_BASE_URL });
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      console.log('Login response:', data);
      
      if (response.ok && data.success) {
        // Extract real JWT token from backend response
        const realToken = data.token;
        const userData = { user_id: data.user_id, id: data.user_id, email: data.email, name: data.name };
        
        setUser(userData); setIsAuthenticated(true); setToken(realToken);
        
        // Store real backend data
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('cached_user', JSON.stringify(userData));
        localStorage.setItem('auth_token', realToken);
        localStorage.setItem('token', realToken);
        
        console.log('Login successful with real token');
        return { success: true, user: userData };
      } else {
        console.error('Login failed:', data);
        return { success: false, error: data.error || data.message || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Login failed: ' + error.message };
    } finally { setLoading(false); }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      console.log('Registration attempt:', { email, name });
      
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();
      console.log('Registration response:', data);
      
      if (response.ok && data.success) {
        // Auto-login with real token from registration
        if (data.token) {
          const userData = { user_id: data.user_id, id: data.user_id, email: data.email, name: data.name };
          
          setUser(userData); setIsAuthenticated(true); setToken(data.token);
          
          localStorage.setItem('user', JSON.stringify(userData));
          localStorage.setItem('cached_user', JSON.stringify(userData));
          localStorage.setItem('auth_token', data.token);
          localStorage.setItem('token', data.token);
          
          console.log('Registration and auto-login successful');
          return { success: true, user: userData, message: data.message };
        }
        return { success: true, message: data.message };
      } else {
        return { success: false, error: data.error || data.message || 'Registration failed' };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { success: false, error: 'Registration failed: ' + error.message };
    } finally { setLoading(false); }
  };

  const logout = () => {
    setToken(null); setUser(null); setIsAuthenticated(false);
    ['auth_token', 'token', 'authToken', 'cached_user', 'user'].forEach(key => localStorage.removeItem(key));
    console.log('User logged out');
  };

  const updateUser = (userData) => {
    const updatedUser = { ...user, ...userData };
    setUser(updatedUser);
    localStorage.setItem('user', JSON.stringify(updatedUser));
    localStorage.setItem('cached_user', JSON.stringify(updatedUser));
  };

  const makeAuthenticatedRequest = async (endpoint, options = {}) => {
    const headers = { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}`, ...(options.headers || {}) };
    const requestOptions = { ...options, headers };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions);
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw new Error('Network request failed: ' + error.message);
    }
  };

  const value = { isAuthenticated, user, token, loading, login, register, logout, updateUser, makeAuthenticatedRequest };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};