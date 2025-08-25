import { api } from './apiService';

class AuthService {
  /**
   * Login user with email and password
   */
  async login(email, password) {
    try {
      const response = await api.auth.login({ email, password });
      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  }

  /**
   * Register new user
   */
  async register(userData) {
    try {
      const response = await api.auth.register(userData);
      return response.data;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout() {
    try {
      await api.auth.logout();
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      return true;
    } catch (error) {
      console.error('Logout failed:', error);
      // Even if API call fails, clear local storage
      localStorage.removeItem('auth_token');
      localStorage.removeItem('refresh_token');
      return false;
    }
  }

  /**
   * Get current user profile
   */
  async me() {
    try {
      const response = await api.auth.me();
      return response.data;
    } catch (error) {
      console.error('Failed to get user profile:', error);
      throw error;
    }
  }

  /**
   * Send forgot password email
   */
  async forgotPassword(email) {
    try {
      const response = await api.auth.forgotPassword(email);
      return response.data;
    } catch (error) {
      console.error('Forgot password failed:', error);
      throw error;
    }
  }

  /**
   * Reset password with token
   */
  async resetPassword(token, password) {
    try {
      const response = await api.auth.resetPassword(token, password);
      return response.data;
    } catch (error) {
      console.error('Password reset failed:', error);
      throw error;
    }
  }

  /**
   * Update user profile
   */
  async updateProfile(profileData) {
    try {
      const response = await api.auth.updateProfile(profileData);
      return response.data;
    } catch (error) {
      console.error('Profile update failed:', error);
      throw error;
    }
  }

  /**
   * Refresh access token
   */
  async refreshToken() {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await api.auth.refresh(refreshToken);
      const { accessToken, refreshToken: newRefreshToken } = response.data;

      localStorage.setItem('auth_token', accessToken);
      if (newRefreshToken) {
        localStorage.setItem('refresh_token', newRefreshToken);
      }

      return response.data;
    } catch (error) {
      console.error('Token refresh failed:', error);
      throw error;
    }
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    const token = localStorage.getItem('auth_token');
    return !!token;
  }

  /**
   * Get stored auth token
   */
  getToken() {
    return localStorage.getItem('auth_token');
  }

  /**
   * Set auth token
   */
  setToken(token) {
    localStorage.setItem('auth_token', token);
  }

  /**
   * Clear all auth data
   */
  clearAuthData() {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('refresh_token');
  }
}

export const authService = new AuthService();