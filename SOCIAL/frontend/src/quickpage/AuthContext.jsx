import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL) 
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

  useEffect(() => {
    const initAuth = async () => {
      try {
        const savedToken = localStorage.getItem('auth_token') || localStorage.getItem('token') || localStorage.getItem('authToken');
        
        if (savedToken) {
          setToken(savedToken);
          
          try {
            // Get user from multiple possible storage keys
            let cachedUser = localStorage.getItem('user') || localStorage.getItem('cached_user');
            
            if (cachedUser) {
              try {
                const userData = JSON.parse(cachedUser);
                console.log('🔧 Restored user from localStorage:', userData);
                setUser(userData);
                setIsAuthenticated(true);
                console.log('✅ User authenticated:', userData.email);
              } catch (parseError) {
                console.error('Error parsing cached user:', parseError);
                clearTokens();
              }
            } else {
              clearTokens();
            }
          } catch (apiError) {
            console.warn('Auth check failed:', apiError.message);
            clearTokens();
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
      ['auth_token', 'token', 'authToken', 'cached_user', 'user', 'reddit_username', 'reddit_session_id'].forEach(key => localStorage.removeItem(key));
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    setLoading(true);
    try {
      console.log('🔧 Login attempt:', { email, apiUrl: API_BASE_URL });
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ email, password })
      });

      console.log('🔧 Login response status:', response.status);
      
      let data;
      try {
        data = await response.json();
        console.log('🔧 Login response data:', data);
      } catch (parseError) {
        console.error('Failed to parse login response:', parseError);
        throw new Error('Invalid response from server');
      }
      
      if (response.ok && data.success) {
        // Your backend returns: { success: true, message: "Login successful", user: { user_id, email, name, platforms_connected } }
        const userData = {
          user_id: data.user.user_id,
          email: data.user.email,
          name: data.user.name,
          platforms_connected: data.user.platforms_connected || []
        };
        
        setUser(userData);
        setIsAuthenticated(true);
        
        // Create a proper token
        const userToken = `token_${userData.user_id}_${Date.now()}`;
        setToken(userToken);
        
        // Store user data in BOTH locations for compatibility
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('cached_user', JSON.stringify(userData));
        localStorage.setItem('auth_token', userToken);
        localStorage.setItem('token', userToken);
        
        console.log('✅ Login successful');
        console.log('✅ User stored:', JSON.stringify(userData));
        console.log('✅ Token stored:', userToken);
        
        return { success: true, user: userData };
      } else {
        console.error('❌ Login failed:', data);
        return { success: false, error: data.error || data.message || 'Login failed' };
      }
    } catch (error) {
      console.error('❌ Login error:', error);
      return { success: false, error: 'Login failed: ' + error.message };
    } finally {
      setLoading(false);
    }
  };




const register = async (name, email, password) => {
  setLoading(true);
  try {
    console.log('🔧 Registration attempt:', { email, name, apiUrl: API_BASE_URL });
    
    // Test backend connection first
    const healthResponse = await fetch(`${API_BASE_URL}/health`);
    const healthData = await healthResponse.json();
    console.log('🔧 Backend health:', healthData);

    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ 
        name: name, 
        email: email, 
        password: password 
      })
    });

    console.log('🔧 Registration response status:', response.status);
    
    const data = await response.json();
    console.log('🔧 Registration response data:', data);
    
    if (response.ok && data.success) {
      // Auto-login after successful registration
      if (data.user) {
        const userData = {
          user_id: data.user.user_id,
          email: data.user.email,
          name: data.user.name,
          platforms_connected: data.user.platforms_connected || []
        };
        
        setUser(userData);
        setIsAuthenticated(true);
        
        // Create a proper token
        const userToken = `token_${userData.user_id}_${Date.now()}`;
        setToken(userToken);
        
        // Store in localStorage
        localStorage.setItem('user', JSON.stringify(userData));
        localStorage.setItem('cached_user', JSON.stringify(userData));
        localStorage.setItem('auth_token', userToken);
        localStorage.setItem('token', userToken);
        
        console.log('✅ Registration and auto-login successful');
        return { success: true, user: userData, message: data.message };
      }
      
      console.log('✅ Registration successful');
      return { success: true, message: data.message };
    } else {
      console.error('❌ Registration failed:', data);
      return { success: false, error: data.error || data.message || 'Registration failed' };
    }
  } catch (error) {
    console.error('❌ Registration error:', error);
    return { success: false, error: 'Registration failed: ' + error.message };
  } finally {
    setLoading(false);
  }
};

  const logout = () => {
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    ['auth_token', 'token', 'authToken', 'cached_user', 'user', 'reddit_username', 'reddit_session_id'].forEach(key => localStorage.removeItem(key));
    console.log('✅ User logged out');
  };

  const updateUser = (userData) => {
    const updatedUser = { ...user, ...userData };
    setUser(updatedUser);
    // Update both storage locations
    localStorage.setItem('user', JSON.stringify(updatedUser));
    localStorage.setItem('cached_user', JSON.stringify(updatedUser));
  };

  const makeAuthenticatedRequest = async (endpoint, options = {}) => {
    const headers = { 
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
      ...(options.headers || {}) 
    };
    
    const requestOptions = { ...options, headers };

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions);
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      throw new Error('Network request failed: ' + error.message);
    }
  };

  // Debug function to check auth state
  const debugAuth = () => {
    console.log('🔧 Auth Debug State:');
    console.log('- isAuthenticated:', isAuthenticated);
    console.log('- user:', user);
    console.log('- token:', token);
    console.log('- localStorage user:', localStorage.getItem('user'));
    console.log('- localStorage cached_user:', localStorage.getItem('cached_user'));
    console.log('- localStorage token:', localStorage.getItem('token'));
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
    makeAuthenticatedRequest,
    debugAuth
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};