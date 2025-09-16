import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

// Use import.meta.env for Vite, or window._env_ for other setups
const API_BASE_URL =
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL)
    ? import.meta.env.VITE_API_URL
    : (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL)
      ? process.env.REACT_APP_API_URL
      : 'https://agentic-u5lx.onrender.com';

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

  // Initialize auth state from localStorage
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check multiple possible token storage keys
        const savedToken = localStorage.getItem('auth_token') || 
                           localStorage.getItem('token') || 
                           localStorage.getItem('authToken');
        
        if (savedToken) {
          setToken(savedToken);
          
          // Verify token with backend
          const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
            headers: {
              'Authorization': `Bearer ${savedToken}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const data = await response.json();
            if (data.success) {
              setUser(data.user);
              setIsAuthenticated(true);
              console.log('✅ User authenticated:', data.user.email);
            } else {
              // Invalid token, clear all possible tokens
              localStorage.removeItem('auth_token');
              localStorage.removeItem('token');
              localStorage.removeItem('authToken');
              setToken(null);
              console.log('❌ Invalid token, cleared from storage');
            }
          } else {
            // Token expired or invalid
            localStorage.removeItem('auth_token');
            localStorage.removeItem('token');
            localStorage.removeItem('authToken');
            setToken(null);
            console.log('❌ Token expired, cleared from storage');
          }
        } else {
          console.log('ℹ️ No auth token found in storage');
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        // Clear all possible tokens on error
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token');
        localStorage.removeItem('authToken');
        setToken(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      
      if (data.success) {
        const authToken = data.token;
        setToken(authToken);
        setUser({
          id: data.user_id,
          email: data.email,
          name: data.name,
          reddit_connected: data.reddit_connected,
          reddit_username: data.reddit_username
        });
        setIsAuthenticated(true);
        
        // Store token in localStorage
        localStorage.setItem('auth_token', authToken);
        
        return { success: true, user: data };
      } else {
        return { success: false, error: data.message || data.error };
      }
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: 'Login failed: ' + error.message };
    }
  };

  const register = async (name, email, password) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();
      
      if (data.success) {
        const authToken = data.token;
        setToken(authToken);
        setUser({
          id: data.user_id,
          email: data.email,
          name: data.name,
          reddit_connected: false,
          reddit_username: null
        });
        setIsAuthenticated(true);
        
        // Store token in localStorage
        localStorage.setItem('auth_token', authToken);
        
        return { success: true, user: data };
      } else {
        return { success: false, error: data.message || data.error };
      }
    } catch (error) {
      console.error('Registration failed:', error);
      return { success: false, error: 'Registration failed: ' + error.message };
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    localStorage.removeItem('auth_token');
    
    // Clear any Reddit-related data
    localStorage.removeItem('reddit_username');
    localStorage.removeItem('reddit_session_id');
  };

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }));
  };

  // FIXED: Helper function to make authenticated API requests
  const makeAuthenticatedRequest = async (endpoint, options = {}) => {
    if (!token) {
      throw new Error('No authentication token');
    }

    // FIXED: Properly merge headers - this was the bug!
    const headers = {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      ...(options.headers || {})  // Merge any additional headers
    };

    // FIXED: Properly merge options
    const requestOptions = {
      ...options,
      headers  // Use the properly merged headers
    };

    const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions);

    if (response.status === 401) {
      // Token expired, logout user
      logout();
      throw new Error('Authentication expired');
    }

    return response;
  };

  const value = {
    isAuthenticated,
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUser,
    makeAuthenticatedRequest
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};