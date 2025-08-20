
// frontend/src/hooks/useAuth.js (UPDATED to match your file)
import { useState, useEffect, useCallback } from 'react'
import authService from '../services/authService'
import useToast from './useToast'

const useAuth = () => {
  const [user, setUser] = useState(authService.getCurrentUser())
  const [token, setToken] = useState(authService.getStoredToken())
  const [loading, setLoading] = useState(false)
  const [isInitialized, setIsInitialized] = useState(false)
  const { success, error: showError } = useToast()

  // Login function
  const login = useCallback(async (credentials) => {
    setLoading(true)
    try {
      const response = await authService.login(credentials)
      setUser(response.user)
      setToken(response.token)
      success('Welcome back!')
      return response
    } catch (error) {
      showError(error.message || 'Login failed')
      throw error
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Register function
  const register = useCallback(async (userData) => {
    setLoading(true)
    try {
      const response = await authService.register(userData)
      setUser(response.user)
      setToken(response.token)
      success('Account created successfully!')
      return response
    } catch (error) {
      showError(error.message || 'Registration failed')
      throw error
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Logout function
  const logout = useCallback(async () => {
    setLoading(true)
    try {
      await authService.logout()
      setUser(null)
      setToken(null)
      success('Logged out successfully')
    } catch (error) {
      showError('Logout failed')
      // Still clear local state even if API call fails
      setUser(null)
      setToken(null)
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Forgot password function
  const forgotPassword = useCallback(async (email) => {
    setLoading(true)
    try {
      await authService.forgotPassword(email)
      success('Password reset email sent!')
      return true
    } catch (error) {
      showError(error.message || 'Failed to send reset email')
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Reset password function
  const resetPassword = useCallback(async (token, password) => {
    setLoading(true)
    try {
      await authService.resetPassword(token, password)
      success('Password reset successfully!')
      return true
    } catch (error) {
      showError(error.message || 'Failed to reset password')
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Verify email function
  const verifyEmail = useCallback(async (token) => {
    setLoading(true)
    try {
      const response = await authService.verifyEmail(token)
      if (response.user) {
        setUser(response.user)
      }
      success('Email verified successfully!')
      return true
    } catch (error) {
      showError(error.message || 'Email verification failed')
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Update profile function
  const updateProfile = useCallback(async (profileData) => {
    setLoading(true)
    try {
      const response = await authService.updateProfile(profileData)
      setUser(response.user)
      success('Profile updated successfully!')
      return response
    } catch (error) {
      showError(error.message || 'Failed to update profile')
      throw error
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Change password function
  const changePassword = useCallback(async (currentPassword, newPassword) => {
    setLoading(true)
    try {
      await authService.changePassword(currentPassword, newPassword)
      success('Password changed successfully!')
      return true
    } catch (error) {
      showError(error.message || 'Failed to change password')
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Delete account function
  const deleteAccount = useCallback(async () => {
    setLoading(true)
    try {
      await authService.deleteAccount()
      setUser(null)
      setToken(null)
      success('Account deleted successfully')
      return true
    } catch (error) {
      showError(error.message || 'Failed to delete account')
      return false
    } finally {
      setLoading(false)
    }
  }, [success, showError])

  // Refresh token function
  const refreshToken = useCallback(async () => {
    try {
      const response = await authService.refreshToken()
      setToken(response.token)
      if (response.user) {
        setUser(response.user)
      }
      return true
    } catch (error) {
      // Token refresh failed, logout user
      setUser(null)
      setToken(null)
      showError('Session expired. Please login again.')
      return false
    }
  }, [showError])

  // Check authentication status
  const isAuthenticated = useCallback(() => {
    return authService.isAuthenticated()
  }, [])

  // Check if user has specific role
  const hasRole = useCallback((role) => {
    return authService.hasRole(role)
  }, [])

  // Check if user has specific permission
  const hasPermission = useCallback((permission) => {
    return authService.hasPermission(permission)
  }, [])

  // Check if email is verified
  const isEmailVerified = useCallback(() => {
    return authService.isEmailVerified()
  }, [])

  // Check if onboarding is complete
  const isOnboardingComplete = useCallback(() => {
    return authService.isOnboardingComplete()
  }, [])

  // Get user subscription info
  const getSubscription = useCallback(() => {
    return user?.subscription || null
  }, [user])

  // Check subscription status
  const hasActiveSubscription = useCallback(() => {
    const subscription = getSubscription()
    return subscription?.status === 'active'
  }, [getSubscription])

  // Check if user is on trial
  const isOnTrial = useCallback(() => {
    const subscription = getSubscription()
    return subscription?.status === 'trial'
  }, [getSubscription])

  // Get trial days remaining
  const getTrialDaysRemaining = useCallback(() => {
    const subscription = getSubscription()
    if (!subscription?.trialEndsAt) return 0
    
    const trialEnd = new Date(subscription.trialEndsAt)
    const today = new Date()
    const diffTime = trialEnd - today
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    return Math.max(0, diffDays)
  }, [getSubscription])

  // Initialize auth service and set up listeners
  useEffect(() => {
    let cleanup = () => {}

    const initialize = async () => {
      try {
        // Initialize auth service
        cleanup = authService.init()
        
        // Set up auth state listener
        const unsubscribe = authService.addListener((newUser, newToken) => {
          setUser(newUser)
          setToken(newToken)
        })

        // Check if token needs refresh
        if (authService.isTokenExpiringSoon() && authService.isAuthenticated()) {
          await refreshToken()
        }

        setIsInitialized(true)
        
        return () => {
          unsubscribe()
          cleanup()
        }
      } catch (error) {
        console.error('Auth initialization error:', error)
        setIsInitialized(true)
      }
    }

    initialize().then(cleanupFn => {
      if (cleanupFn) cleanup = cleanupFn
    })

    return () => cleanup()
  }, [refreshToken])

  // Auto-refresh token when it's about to expire
  useEffect(() => {
    if (!isAuthenticated()) return

    const interval = setInterval(() => {
      if (authService.isTokenExpiringSoon()) {
        refreshToken()
      }
    }, 60000) // Check every minute

    return () => clearInterval(interval)
  }, [isAuthenticated, refreshToken])

  // Session timeout check
  useEffect(() => {
    if (!isAuthenticated()) return

    const interval = setInterval(() => {
      if (authService.isSessionExpired()) {
        logout()
        showError('Session expired due to inactivity')
      }
    }, 30000) // Check every 30 seconds

    return () => clearInterval(interval)
  }, [isAuthenticated, logout, showError])

  return {
    // User state
    user,
    token,
    isAuthenticated: isAuthenticated(),
    isInitialized,
    loading,

    // Auth actions
    login,
    register,
    logout,
    forgotPassword,
    resetPassword,
    verifyEmail,
    updateProfile,
    changePassword,
    deleteAccount,
    refreshToken,

    // User checks
    hasRole,
    hasPermission,
    isEmailVerified: isEmailVerified(),
    isOnboardingComplete: isOnboardingComplete(),

    // Subscription info
    subscription: getSubscription(),
    hasActiveSubscription: hasActiveSubscription(),
    isOnTrial: isOnTrial(),
    trialDaysRemaining: getTrialDaysRemaining(),

    // Utility functions
    extendSession: authService.extendSession
  }
}

// Export both default and named export for flexibility
export default useAuth
export { useAuth }