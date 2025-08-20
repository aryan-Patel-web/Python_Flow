// frontend/src/services/authService.js
import api from './api'

class AuthService {
  constructor() {
    this.listeners = []
    this.token = this.getStoredToken()
    this.user = this.getCurrentUser()
  }

  // Initialize auth service
  init() {
    // Set up axios interceptors
    this.setupInterceptors()
    return () => {
      // Cleanup function
      this.listeners = []
    }
  }

  // Set up axios interceptors for token handling
  setupInterceptors() {
    // Request interceptor
    api.interceptors.request.use(
      (config) => {
        const token = this.getStoredToken()
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    // Response interceptor
    api.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          this.logout()
        }
        return Promise.reject(error)
      }
    )
  }

  // Get stored token
  getStoredToken() {
    return localStorage.getItem('auth_token')
  }

  // Store token
  setStoredToken(token) {
    if (token) {
      localStorage.setItem('auth_token', token)
    } else {
      localStorage.removeItem('auth_token')
    }
    this.token = token
  }

  // Get current user
  getCurrentUser() {
    try {
      const userStr = localStorage.getItem('auth_user')
      return userStr ? JSON.parse(userStr) : null
    } catch {
      return null
    }
  }

  // Store user
  setCurrentUser(user) {
    if (user) {
      localStorage.setItem('auth_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('auth_user')
    }
    this.user = user
    this.notifyListeners(user, this.token)
  }

  // Add listener for auth state changes
  addListener(callback) {
    this.listeners.push(callback)
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback)
    }
  }

  // Notify all listeners
  notifyListeners(user, token) {
    this.listeners.forEach(callback => callback(user, token))
  }

  // Login
  async login(credentials) {
    try {
      const response = await api.post('/auth/login', credentials)
      const { token, user } = response.data

      this.setStoredToken(token)
      this.setCurrentUser(user)

      return { token, user }
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Login failed')
    }
  }

  // Register
  async register(userData) {
    try {
      const response = await api.post('/auth/register', userData)
      const { token, user } = response.data

      this.setStoredToken(token)
      this.setCurrentUser(user)

      return { token, user }
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Registration failed')
    }
  }

  // Logout
  async logout() {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      // Continue with logout even if API call fails
      console.warn('Logout API call failed:', error)
    } finally {
      this.setStoredToken(null)
      this.setCurrentUser(null)
    }
  }

  // Forgot password
  async forgotPassword(email) {
    try {
      await api.post('/auth/forgot-password', { email })
      return true
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to send reset email')
    }
  }

  // Reset password
  async resetPassword(token, password) {
    try {
      await api.post('/auth/reset-password', { token, password })
      return true
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to reset password')
    }
  }

  // Verify email
  async verifyEmail(token) {
    try {
      const response = await api.post('/auth/verify-email', { token })
      if (response.data.user) {
        this.setCurrentUser(response.data.user)
      }
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Email verification failed')
    }
  }

  // Update profile
  async updateProfile(profileData) {
    try {
      const response = await api.put('/auth/profile', profileData)
      this.setCurrentUser(response.data.user)
      return response.data
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update profile')
    }
  }

  // Change password
  async changePassword(currentPassword, newPassword) {
    try {
      await api.post('/auth/change-password', { currentPassword, newPassword })
      return true
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to change password')
    }
  }

  // Delete account
  async deleteAccount() {
    try {
      await api.delete('/auth/account')
      this.setStoredToken(null)
      this.setCurrentUser(null)
      return true
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete account')
    }
  }

  // Refresh token
  async refreshToken() {
    try {
      const response = await api.post('/auth/refresh')
      const { token, user } = response.data

      this.setStoredToken(token)
      if (user) {
        this.setCurrentUser(user)
      }

      return { token, user }
    } catch (error) {
      this.logout()
      throw new Error('Session expired')
    }
  }

  // Check if authenticated
  isAuthenticated() {
    return !!this.getStoredToken()
  }

  // Check if user has role
  hasRole(role) {
    return this.user?.roles?.includes(role) || false
  }

  // Check if user has permission
  hasPermission(permission) {
    return this.user?.permissions?.includes(permission) || false
  }

  // Check if email is verified
  isEmailVerified() {
    return this.user?.emailVerified || false
  }

  // Check if onboarding is complete
  isOnboardingComplete() {
    return this.user?.onboardingComplete || false
  }

  // Check if token is expiring soon
  isTokenExpiringSoon() {
    const token = this.getStoredToken()
    if (!token) return false

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000
      const now = Date.now()
      const fiveMinutes = 5 * 60 * 1000

      return exp - now < fiveMinutes
    } catch {
      return false
    }
  }

  // Check if session is expired
  isSessionExpired() {
    const token = this.getStoredToken()
    if (!token) return true

    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      return payload.exp * 1000 < Date.now()
    } catch {
      return true
    }
  }

  // Extend session
  extendSession() {
    // Update last activity timestamp
    localStorage.setItem('last_activity', Date.now().toString())
  }
}

// Create and export singleton instance
const authService = new AuthService()
export default authService