import { useState, useEffect, useCallback } from 'react';
import { authService } from '../services/authService';

export const useAuth = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Memoized functions to prevent infinite loops
  const checkAuthStatus = useCallback(async () => {
    try {
      const token = localStorage.getItem('auth_token');
      if (token) {
        const userData = await authService.validateToken(token);
        if (userData) {
          setUser(userData);
        } else {
          // Token invalid, remove it
          localStorage.removeItem('auth_token');
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
      setUser(null);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, []); // No dependencies to prevent loops

  const login = useCallback(async (credentials) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.login(credentials);
      if (response.token && response.user) {
        localStorage.setItem('auth_token', response.token);
        setUser(response.user);
        return response;
      }
      throw new Error('Invalid login response');
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(async (userData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.register(userData);
      if (response.token && response.user) {
        localStorage.setItem('auth_token', response.token);
        setUser(response.user);
        return response;
      }
      throw new Error('Invalid registration response');
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('auth_token');
      setUser(null);
      setError(null);
    }
  }, []);

  const forgotPassword = useCallback(async (email) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authService.forgotPassword(email);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  // Check auth status only once on mount
  useEffect(() => {
    checkAuthStatus();
  }, []); // Empty dependency array - runs only once

  return {
    user,
    loading,
    error,
    login,
    register,
    logout,
    forgotPassword,
    isAuthenticated: !!user,
    clearError: () => setError(null)
  };
};