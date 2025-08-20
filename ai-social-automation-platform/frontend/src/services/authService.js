const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
const USE_MOCK_AUTH = import.meta.env.VITE_USE_MOCK_AUTH !== 'false'; // Default to true for development

class AuthService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.useMockAuth = USE_MOCK_AUTH;
  }

  // Mock user data for development
  mockUsers = [
    {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      password: 'password123'
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@example.com',
      password: 'password123'
    }
  ];

  // Helper method to simulate API delay
  async delay(ms = 1000) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Mock authentication methods
  async mockLogin(credentials) {
    await this.delay(1500); // Simulate network delay
    
    const user = this.mockUsers.find(
      u => u.email === credentials.email && u.password === credentials.password
    );
    
    if (!user) {
      throw new Error('Invalid email or password');
    }
    
    const token = `mock_token_${user.id}_${Date.now()}`;
    const { password, ...userWithoutPassword } = user;
    
    return {
      token,
      user: userWithoutPassword,
      message: 'Login successful'
    };
  }

  async mockRegister(userData) {
    await this.delay(1500);
    
    // Check if user already exists
    const existingUser = this.mockUsers.find(u => u.email === userData.email);
    if (existingUser) {
      throw new Error('User already exists with this email');
    }
    
    // Create new user
    const newUser = {
      id: this.mockUsers.length + 1,
      name: userData.name,
      email: userData.email,
      password: userData.password
    };
    
    this.mockUsers.push(newUser);
    
    const token = `mock_token_${newUser.id}_${Date.now()}`;
    const { password, ...userWithoutPassword } = newUser;
    
    return {
      token,
      user: userWithoutPassword,
      message: 'Registration successful'
    };
  }

  async mockValidateToken(token) {
    await this.delay(500);
    
    if (!token || !token.startsWith('mock_token_')) {
      return null;
    }
    
    // Extract user ID from token
    const tokenParts = token.split('_');
    const userId = parseInt(tokenParts[2]);
    
    const user = this.mockUsers.find(u => u.id === userId);
    if (!user) {
      return null;
    }
    
    const { password, ...userWithoutPassword } = user;
    return userWithoutPassword;
  }

  async mockForgotPassword(email) {
    await this.delay(1500);
    
    const user = this.mockUsers.find(u => u.email === email);
    if (!user) {
      throw new Error('No user found with this email');
    }
    
    return {
      message: 'Password reset instructions sent to your email'
    };
  }

  // Real API methods
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const token = localStorage.getItem('auth_token');
    
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(token && { Authorization: `Bearer ${token}` }),
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error('Server is not responding with JSON. Is the backend running?');
      }
      
      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || `HTTP error! status: ${response.status}`);
      }

      return data;
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      
      // If it's a network error and we're in development, suggest using mock auth
      if (error.name === 'TypeError' || error.message.includes('Failed to fetch')) {
        console.warn('🔧 Backend not available. Using mock authentication for development.');
        throw new Error('Backend server not available. Using mock authentication.');
      }
      
      throw error;
    }
  }

  // Login user (with fallback to mock)
  async login(credentials) {
    if (this.useMockAuth) {
      console.log('🔧 Using mock authentication for development');
      return this.mockLogin(credentials);
    }
    
    try {
      const response = await this.makeRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
      });
      return response;
    } catch (error) {
      // Fallback to mock if real API fails
      console.warn('🔧 Real API failed, falling back to mock authentication');
      return this.mockLogin(credentials);
    }
  }

  // Register user (with fallback to mock)
  async register(userData) {
    if (this.useMockAuth) {
      console.log('🔧 Using mock authentication for development');
      return this.mockRegister(userData);
    }
    
    try {
      const response = await this.makeRequest('/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      });
      return response;
    } catch (error) {
      // Fallback to mock if real API fails
      console.warn('🔧 Real API failed, falling back to mock authentication');
      return this.mockRegister(userData);
    }
  }

  // Validate token (with fallback to mock)
  async validateToken(token) {
    if (!token) {
      return null;
    }

    if (this.useMockAuth || token.startsWith('mock_token_')) {
      return this.mockValidateToken(token);
    }

    try {
      const response = await this.makeRequest('/auth/me', {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      return response.user;
    } catch (error) {
      console.error('Token validation failed:', error);
      // Try mock validation as fallback
      return this.mockValidateToken(token);
    }
  }

  // Logout user
  async logout() {
    if (this.useMockAuth) {
      console.log('🔧 Mock logout');
      return Promise.resolve();
    }
    
    try {
      await this.makeRequest('/auth/logout', {
        method: 'POST',
      });
    } catch (error) {
      console.error('Logout request failed:', error);
      // Don't throw error for logout - always clear local storage
    }
  }

  // Forgot password (with fallback to mock)
  async forgotPassword(email) {
    if (this.useMockAuth) {
      console.log('🔧 Using mock forgot password');
      return this.mockForgotPassword(email);
    }
    
    try {
      const response = await this.makeRequest('/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email }),
      });
      return response;
    } catch (error) {
      // Fallback to mock if real API fails
      console.warn('🔧 Real API failed, falling back to mock forgot password');
      return this.mockForgotPassword(email);
    }
  }

  // Reset password
  async resetPassword(token, newPassword) {
    try {
      const response = await this.makeRequest('/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ token, password: newPassword }),
      });
      return response;
    } catch (error) {
      throw new Error(error.message || 'Password reset failed');
    }
  }

  // Get current user
  async getCurrentUser() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      return null;
    }
    return this.validateToken(token);
  }

  // Check if user is authenticated
  isAuthenticated() {
    const token = localStorage.getItem('auth_token');
    return !!token;
  }

  // Get auth token
  getToken() {
    return localStorage.getItem('auth_token');
  }

  // Set auth token
  setToken(token) {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }
}

export const authService = new AuthService();