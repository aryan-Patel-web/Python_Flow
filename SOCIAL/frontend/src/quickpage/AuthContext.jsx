import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';

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

  // Clear all tokens helper
  const clearAllTokens = useCallback(() => {
    ['auth_token', 'token', 'authToken', 'cached_user', 'user'].forEach(key => 
      localStorage.removeItem(key)
    );
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    console.log('All tokens cleared');
  }, []);

  // Initialize authentication on app load
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Check for any existing token (multiple possible keys for compatibility)
        const savedToken = localStorage.getItem('authToken') || 
                          localStorage.getItem('auth_token') || 
                          localStorage.getItem('token');
        
        const cachedUser = localStorage.getItem('cached_user') || 
                          localStorage.getItem('user');
        
        if (savedToken && cachedUser) {
          try {
            const userData = JSON.parse(cachedUser);
            
            // Validate token format - should be JWT or backend format
            if (savedToken.length > 20) {
              // Test token with backend
              const testResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
                headers: {
                  'Authorization': `Bearer ${savedToken}`,
                  'Content-Type': 'application/json'
                }
              });
              
              if (testResponse.ok) {
                const validatedUser = await testResponse.json();
                if (validatedUser.success) {
                  setUser(userData);
                  setToken(savedToken);
                  setIsAuthenticated(true);
                  
                  // Ensure token is stored with correct key
                  localStorage.setItem('authToken', savedToken);
                  console.log('User restored:', userData.email);
                  setLoading(false);
                  return;
                }
              }
            }
            
            // If we reach here, token is invalid
            throw new Error('Invalid token');
          } catch (parseError) {
            console.error('Token validation failed:', parseError);
            clearAllTokens();
          }
        } else {
          clearAllTokens();
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        clearAllTokens();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, [clearAllTokens]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      console.log('Login attempt:', { email, apiUrl: API_BASE_URL });
      
      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Accept': 'application/json' 
        },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      console.log('Login response status:', response.status);
      console.log('Login response data:', data);
      
      if (response.ok && data.success && data.token) {
        // Create user object
        const userData = { 
          user_id: data.user_id, 
          id: data.user_id, 
          email: data.email, 
          name: data.name,
          platforms_connected: data.platforms_connected || []
        };
        
        // Set state
        setUser(userData);
        setIsAuthenticated(true);
        setToken(data.token);
        
        // Store with correct key (authToken is what makeAuthenticatedRequest uses)
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('cached_user', JSON.stringify(userData));
        
        // Clean up old keys
        localStorage.removeItem('auth_token');
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        
        console.log('Login successful - token stored as authToken');
        return { success: true, user: userData };
      } else {
        console.error('Login failed:', data);
        return { 
          success: false, 
          error: data.error || data.message || `HTTP ${response.status}: Login failed` 
        };
      }
    } catch (error) {
      console.error('Login network error:', error);
      return { 
        success: false, 
        error: 'Network error: ' + error.message 
      };
    } finally {
      setLoading(false);
    }
  };

  const register = async (name, email, password) => {
    setLoading(true);
    try {
      console.log('Registration attempt:', { email, name });
      
      const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json', 
          'Accept': 'application/json' 
        },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();
      console.log('Registration response:', data);
      
      if (response.ok && data.success) {
        // Auto-login after successful registration
        if (data.token) {
          const userData = { 
            user_id: data.user_id, 
            id: data.user_id, 
            email: data.email, 
            name: data.name,
            platforms_connected: []
          };
          
          setUser(userData);
          setIsAuthenticated(true);
          setToken(data.token);
          
          localStorage.setItem('authToken', data.token);
          localStorage.setItem('cached_user', JSON.stringify(userData));
          
          console.log('Registration and auto-login successful');
          return { success: true, user: userData, message: data.message };
        }
        return { success: true, message: data.message };
      } else {
        return { 
          success: false, 
          error: data.error || data.message || 'Registration failed' 
        };
      }
    } catch (error) {
      console.error('Registration error:', error);
      return { 
        success: false, 
        error: 'Registration failed: ' + error.message 
      };
    } finally {
      setLoading(false);
    }
  };

  const logout = useCallback(() => {
    clearAllTokens();
    console.log('User logged out');
  }, [clearAllTokens]);

  const updateUser = useCallback((userData) => {
    const updatedUser = { ...user, ...userData };
    setUser(updatedUser);
    localStorage.setItem('cached_user', JSON.stringify(updatedUser));
  }, [user]);

  // Fixed makeAuthenticatedRequest function
  const makeAuthenticatedRequest = useCallback(async (endpoint, options = {}) => {
    // Use state token first, fallback to localStorage
    const authToken = token || localStorage.getItem('authToken');
    
    if (!authToken) {
      console.error('No authentication token available');
      logout();
      throw new Error('No authentication token found');
    }

    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authToken}`,
      ...(options.headers || {})
    };

    const requestOptions = {
      ...options,
      headers,
      credentials: 'include'
    };

    try {
      console.log(`Making request to: ${API_BASE_URL}${endpoint}`);
      const response = await fetch(`${API_BASE_URL}${endpoint}`, requestOptions);
      
      if (response.status === 401) {
        console.error('401 Unauthorized - token expired or invalid');
        logout();
        throw new Error('Authentication failed - please log in again');
      }
      
      return response;
    } catch (error) {
      console.error('API request failed:', error);
      if (error.message.includes('Authentication failed')) {
        throw error; // Re-throw auth errors
      }
      throw new Error('Network request failed: ' + error.message);
    }
  }, [token, logout]);

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

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};