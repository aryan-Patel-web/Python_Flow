import { useState, useEffect, useCallback } from 'react'
import { credentials } from '../services/apiService'
import useToast from './useToast'

const useCredentials = () => {
  const [platforms, setPlatforms] = useState([])
  const [loading, setLoading] = useState(false)
  const [testing, setTesting] = useState({})
  const [errors, setErrors] = useState({})
  const { success, error: showError, loading: showLoading } = useToast()

  // Load all platform credentials
  const loadCredentials = useCallback(async () => {
    setLoading(true)
    setErrors({})
    
    try {
      const data = await credentials.getAll()
      setPlatforms(data.platforms || [])
      return data
    } catch (error) {
      setErrors({ load: error.message })
      showError('Failed to load platform credentials')
      return null
    } finally {
      setLoading(false)
    }
  }, [showError])

  // Add or update platform credentials
  const saveCredentials = useCallback(async (platformData) => {
    const loadingId = showLoading('Saving credentials...')
    setErrors({})
    
    try {
      let response
      if (platformData.id) {
        response = await credentials.update(platformData.id, platformData)
        success('Platform credentials updated successfully!')
      } else {
        response = await credentials.create(platformData)
        success('Platform credentials added successfully!')
      }
      
      // Update local state
      setPlatforms(prev => {
        if (platformData.id) {
          return prev.map(p => p.id === platformData.id ? response.platform : p)
        } else {
          return [...prev, response.platform]
        }
      })
      
      return response.platform
    } catch (error) {
      setErrors({ save: error.message })
      showError(error.message || 'Failed to save credentials')
      return null
    }
  }, [success, showError, showLoading])

  // Delete platform credentials
  const deleteCredentials = useCallback(async (platformId) => {
    const loadingId = showLoading('Removing platform...')
    setErrors({})
    
    try {
      await credentials.delete(platformId)
      
      // Update local state
      setPlatforms(prev => prev.filter(p => p.id !== platformId))
      success('Platform removed successfully!')
      
      return true
    } catch (error) {
      setErrors({ delete: error.message })
      showError('Failed to remove platform')
      return false
    }
  }, [success, showError, showLoading])

  // Test platform connection
  const testConnection = useCallback(async (platformId, credentialData = null) => {
    setTesting(prev => ({ ...prev, [platformId]: true }))
    setErrors(prev => ({ ...prev, [platformId]: null }))
    
    try {
      let response
      if (credentialData) {
        // Test new credentials before saving
        response = await credentials.testConnection(credentialData)
      } else {
        // Test existing saved credentials
        response = await credentials.test(platformId)
      }
      
      if (response.success) {
        success(`${response.platformName} connection successful!`)
        
        // Update platform status if testing existing credentials
        if (!credentialData) {
          setPlatforms(prev => prev.map(p => 
            p.id === platformId 
              ? { ...p, isConnected: true, lastTested: new Date().toISOString() }
              : p
          ))
        }
        
        return { success: true, data: response.data }
      } else {
        const errorMsg = response.error || 'Connection test failed'
        setErrors(prev => ({ ...prev, [platformId]: errorMsg }))
        showError(errorMsg)
        return { success: false, error: errorMsg }
      }
    } catch (error) {
      const errorMsg = error.message || 'Connection test failed'
      setErrors(prev => ({ ...prev, [platformId]: errorMsg }))
      showError(errorMsg)
      return { success: false, error: errorMsg }
    } finally {
      setTesting(prev => ({ ...prev, [platformId]: false }))
    }
  }, [success, showError])

  // Toggle platform active status
  const togglePlatform = useCallback(async (platformId, isActive) => {
    const platform = platforms.find(p => p.id === platformId)
    if (!platform) return false

    try {
      const updatedPlatform = { ...platform, isActive }
      const response = await credentials.update(platformId, updatedPlatform)
      
      setPlatforms(prev => prev.map(p => 
        p.id === platformId ? response.platform : p
      ))
      
      success(`${platform.name} ${isActive ? 'activated' : 'paused'} successfully!`)
      return true
    } catch (error) {
      showError(`Failed to ${isActive ? 'activate' : 'pause'} ${platform.name}`)
      return false
    }
  }, [platforms, success, showError])

  // Get platform by ID
  const getPlatform = useCallback((platformId) => {
    return platforms.find(p => p.id === platformId) || null
  }, [platforms])

  // Get connected platforms
  const getConnectedPlatforms = useCallback(() => {
    return platforms.filter(p => p.isConnected)
  }, [platforms])

  // Get active platforms
  const getActivePlatforms = useCallback(() => {
    return platforms.filter(p => p.isConnected && p.isActive)
  }, [platforms])

  // Get platforms by type
  const getPlatformsByType = useCallback((type) => {
    return platforms.filter(p => p.type === type)
  }, [platforms])

  // Check if platform is connected
  const isPlatformConnected = useCallback((platformId) => {
    const platform = getPlatform(platformId)
    return platform?.isConnected || false
  }, [getPlatform])

  // Check if platform is active
  const isPlatformActive = useCallback((platformId) => {
    const platform = getPlatform(platformId)
    return platform?.isConnected && platform?.isActive || false
  }, [getPlatform])

  // Get platform connection stats
  const getConnectionStats = useCallback(() => {
    const total = platforms.length
    const connected = getConnectedPlatforms().length
    const active = getActivePlatforms().length
    
    return {
      total,
      connected,
      active,
      pending: total - connected,
      connectionRate: total > 0 ? (connected / total) * 100 : 0,
      activeRate: connected > 0 ? (active / connected) * 100 : 0
    }
  }, [platforms, getConnectedPlatforms, getActivePlatforms])

  // Validate credentials for a platform
  const validateCredentials = useCallback((platformType, credentialData) => {
    const requiredFields = {
      instagram: ['username', 'password'],
      facebook: ['email', 'password'],
      youtube: ['email', 'password'],
      linkedin: ['email', 'password'],
      twitter: ['username', 'password']
    }

    const required = requiredFields[platformType] || []
    const missing = required.filter(field => !credentialData[field]?.trim())
    
    if (missing.length > 0) {
      return {
        isValid: false,
        errors: missing.map(field => `${field} is required`),
        missingFields: missing
      }
    }

    // Additional validation rules
    const errors = []
    
    if (credentialData.email && !/\S+@\S+\.\S+/.test(credentialData.email)) {
      errors.push('Please enter a valid email address')
    }

    if (credentialData.password && credentialData.password.length < 6) {
      errors.push('Password must be at least 6 characters long')
    }

    return {
      isValid: errors.length === 0,
      errors,
      missingFields: []
    }
  }, [])

  // Bulk operations
  const testAllConnections = useCallback(async () => {
    const connectedPlatforms = getConnectedPlatforms()
    const results = []
    
    for (const platform of connectedPlatforms) {
      const result = await testConnection(platform.id)
      results.push({
        platformId: platform.id,
        platformName: platform.name,
        ...result
      })
    }
    
    const successful = results.filter(r => r.success).length
    const total = results.length
    
    if (successful === total) {
      success(`All ${total} platforms are connected successfully!`)
    } else {
      showError(`${total - successful} of ${total} platforms have connection issues`)
    }
    
    return results
  }, [getConnectedPlatforms, testConnection, success, showError])

  const refreshAllPlatforms = useCallback(async () => {
    return await loadCredentials()
  }, [loadCredentials])

  // Load credentials on mount
  useEffect(() => {
    loadCredentials()
  }, [loadCredentials])

  // Auto-refresh every 5 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      loadCredentials()
    }, 5 * 60 * 1000)

    return () => clearInterval(interval)
  }, [loadCredentials])

  return {
    // Data
    platforms,
    loading,
    testing,
    errors,

    // Actions
    loadCredentials,
    saveCredentials,
    deleteCredentials,
    testConnection,
    togglePlatform,

    // Getters
    getPlatform,
    getConnectedPlatforms,
    getActivePlatforms,
    getPlatformsByType,
    getConnectionStats,

    // Checkers
    isPlatformConnected,
    isPlatformActive,

    // Validation
    validateCredentials,

    // Bulk operations
    testAllConnections,
    refreshAllPlatforms
  }
}

export default useCredentials