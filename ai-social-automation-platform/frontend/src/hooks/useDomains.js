import { useState, useEffect, useCallback } from 'react'
import { domains } from '../services/apiService'
import useToast from './useToast'

const useDomains = () => {
  const [availableDomains, setAvailableDomains] = useState([])
  const [selectedDomains, setSelectedDomains] = useState([])
  const [loading, setLoading] = useState(false)
  const [previewData, setPreviewData] = useState({})
  const [errors, setErrors] = useState({})
  const { success, error: showError, loading: showLoading } = useToast()

  // Load available domains
  const loadAvailableDomains = useCallback(async () => {
    setLoading(true)
    setErrors({})
    
    try {
      const data = await domains.getAvailable()
      setAvailableDomains(data.domains || [])
      return data
    } catch (error) {
      setErrors({ load: error.message })
      showError('Failed to load available domains')
      return null
    } finally {
      setLoading(false)
    }
  }, [showError])

  // Load user selected domains
  const loadUserDomains = useCallback(async () => {
    setLoading(true)
    setErrors({})
    
    try {
      const data = await domains.getUserDomains()
      setSelectedDomains(data.domains || [])
      return data
    } catch (error) {
      setErrors({ loadUser: error.message })
      showError('Failed to load your selected domains')
      return null
    } finally {
      setLoading(false)
    }
  }, [showError])

  // Update domain selection
  const updateSelection = useCallback(async (domainIds) => {
    const loadingId = showLoading('Updating domain selection...')
    setErrors({})
    
    try {
      const response = await domains.updateSelection(domainIds)
      setSelectedDomains(response.domains || [])
      success('Domain selection updated successfully!')
      return response
    } catch (error) {
      setErrors({ update: error.message })
      showError('Failed to update domain selection')
      return null
    }
  }, [success, showError, showLoading])

  // Add domain to selection
  const addDomain = useCallback(async (domainId) => {
    const currentIds = selectedDomains.map(d => d.id)
    if (currentIds.includes(domainId)) {
      showError('Domain is already selected')
      return false
    }
    
    const newIds = [...currentIds, domainId]
    const result = await updateSelection(newIds)
    return result !== null
  }, [selectedDomains, updateSelection, showError])

  // Remove domain from selection
  const removeDomain = useCallback(async (domainId) => {
    const currentIds = selectedDomains.map(d => d.id)
    const newIds = currentIds.filter(id => id !== domainId)
    const result = await updateSelection(newIds)
    return result !== null
  }, [selectedDomains, updateSelection])

  // Toggle domain selection
  const toggleDomain = useCallback(async (domainId) => {
    const currentIds = selectedDomains.map(d => d.id)
    if (currentIds.includes(domainId)) {
      return await removeDomain(domainId)
    } else {
      return await addDomain(domainId)
    }
  }, [selectedDomains, addDomain, removeDomain])

  // Get content preview for domain
  const getPreview = useCallback(async (domainId, platformId = 'instagram') => {
    setErrors(prev => ({ ...prev, [`preview_${domainId}`]: null }))
    
    try {
      const response = await domains.getPreview(domainId, platformId)
      setPreviewData(prev => ({
        ...prev,
        [`${domainId}_${platformId}`]: response.preview
      }))
      return response.preview
    } catch (error) {
      setErrors(prev => ({ ...prev, [`preview_${domainId}`]: error.message }))
      showError(`Failed to load preview for ${platformId}`)
      return null
    }
  }, [showError])

  // Get cached preview
  const getCachedPreview = useCallback((domainId, platformId = 'instagram') => {
    return previewData[`${domainId}_${platformId}`] || null
  }, [previewData])

  // Get domain by ID
  const getDomain = useCallback((domainId) => {
    return availableDomains.find(d => d.id === domainId) || null
  }, [availableDomains])

  // Check if domain is selected
  const isDomainSelected = useCallback((domainId) => {
    return selectedDomains.some(d => d.id === domainId)
  }, [selectedDomains])

  // Get domains by category
  const getDomainsByCategory = useCallback((category) => {
    return availableDomains.filter(d => d.category === category)
  }, [availableDomains])

  // Get popular domains
  const getPopularDomains = useCallback(() => {
    return availableDomains.filter(d => d.popularity === 'high')
  }, [availableDomains])

  // Get recommended domains based on user preferences
  const getRecommendedDomains = useCallback((userInterests = []) => {
    if (userInterests.length === 0) return getPopularDomains()
    
    return availableDomains.filter(domain => 
      domain.tags?.some(tag => 
        userInterests.some(interest => 
          tag.toLowerCase().includes(interest.toLowerCase())
        )
      )
    ).sort((a, b) => {
      // Sort by popularity and relevance
      const aScore = (a.popularity === 'high' ? 3 : a.popularity === 'medium' ? 2 : 1)
      const bScore = (b.popularity === 'high' ? 3 : b.popularity === 'medium' ? 2 : 1)
      return bScore - aScore
    })
  }, [availableDomains, getPopularDomains])

  // Get domain statistics
  const getDomainStats = useCallback(() => {
    const total = availableDomains.length
    const selected = selectedDomains.length
    const categories = [...new Set(availableDomains.map(d => d.category))].length
    const popular = getPopularDomains().length
    
    return {
      total,
      selected,
      categories,
      popular,
      selectionRate: total > 0 ? (selected / total) * 100 : 0
    }
  }, [availableDomains, selectedDomains, getPopularDomains])

  // Search domains
  const searchDomains = useCallback((query) => {
    if (!query.trim()) return availableDomains
    
    const lowercaseQuery = query.toLowerCase()
    return availableDomains.filter(domain =>
      domain.name.toLowerCase().includes(lowercaseQuery) ||
      domain.description.toLowerCase().includes(lowercaseQuery) ||
      domain.category.toLowerCase().includes(lowercaseQuery) ||
      domain.tags?.some(tag => tag.toLowerCase().includes(lowercaseQuery))
    )
  }, [availableDomains])

  // Filter domains
  const filterDomains = useCallback((filters = {}) => {
    let filtered = [...availableDomains]
    
    if (filters.category) {
      filtered = filtered.filter(d => d.category === filters.category)
    }
    
    if (filters.popularity) {
      filtered = filtered.filter(d => d.popularity === filters.popularity)
    }
    
    if (filters.difficulty) {
      filtered = filtered.filter(d => d.stats?.difficulty === filters.difficulty)
    }
    
    if (filters.platform) {
      filtered = filtered.filter(d => 
        !d.bestPlatforms || d.bestPlatforms.includes(filters.platform)
      )
    }
    
    if (filters.selected !== undefined) {
      filtered = filtered.filter(d => isDomainSelected(d.id) === filters.selected)
    }
    
    return filtered
  }, [availableDomains, isDomainSelected])

  // Validate domain selection
  const validateSelection = useCallback((domainIds = null) => {
    const domainsToCheck = domainIds || selectedDomains.map(d => d.id)
    const errors = []
    
    if (domainsToCheck.length === 0) {
      errors.push('Please select at least one content domain')
    }
    
    if (domainsToCheck.length > 10) {
      errors.push('You can select up to 10 content domains')
    }
    
    // Check for conflicting domains
    const conflictGroups = {
      'serious': ['business', 'finance', 'education'],
      'entertainment': ['memes', 'humor', 'entertainment']
    }
    
    const selectedCategories = domainsToCheck.map(id => {
      const domain = getDomain(id)
      return domain?.category
    }).filter(Boolean)
    
    Object.entries(conflictGroups).forEach(([group, categories]) => {
      const hasMultiple = categories.filter(cat => selectedCategories.includes(cat)).length > 1
      if (hasMultiple) {
        errors.push(`Consider focusing on either serious or entertainment content for better audience engagement`)
      }
    })
    
    return {
      isValid: errors.length === 0,
      errors,
      warnings: errors.filter(e => e.includes('Consider'))
    }
  }, [selectedDomains, getDomain])

  // Get content suggestions for selected domains
  const getContentSuggestions = useCallback(() => {
    return selectedDomains.map(domain => ({
      domainId: domain.id,
      domainName: domain.name,
      suggestions: domain.examples || [],
      bestTimes: domain.optimalPostingTimes || [],
      platforms: domain.bestPlatforms || ['instagram', 'facebook']
    }))
  }, [selectedDomains])

  // Bulk operations
  const selectMultipleDomains = useCallback(async (domainIds) => {
    const currentIds = selectedDomains.map(d => d.id)
    const uniqueNewIds = domainIds.filter(id => !currentIds.includes(id))
    const newSelection = [...currentIds, ...uniqueNewIds]
    
    return await updateSelection(newSelection)
  }, [selectedDomains, updateSelection])

  const clearSelection = useCallback(async () => {
    return await updateSelection([])
  }, [updateSelection])

  const selectRecommended = useCallback(async (userInterests = []) => {
    const recommended = getRecommendedDomains(userInterests)
    const topRecommended = recommended.slice(0, 5).map(d => d.id)
    return await updateSelection(topRecommended)
  }, [getRecommendedDomains, updateSelection])

  // Load initial data
  useEffect(() => {
    Promise.all([
      loadAvailableDomains(),
      loadUserDomains()
    ])
  }, [loadAvailableDomains, loadUserDomains])

  // Auto-refresh every 10 minutes
  useEffect(() => {
    const interval = setInterval(() => {
      loadAvailableDomains()
    }, 10 * 60 * 1000)

    return () => clearInterval(interval)
  }, [loadAvailableDomains])

  return {
    // Data
    availableDomains,
    selectedDomains,
    loading,
    errors,
    previewData,

    // Actions
    loadAvailableDomains,
    loadUserDomains,
    updateSelection,
    addDomain,
    removeDomain,
    toggleDomain,
    getPreview,

    // Getters
    getDomain,
    getCachedPreview,
    getDomainsByCategory,
    getPopularDomains,
    getRecommendedDomains,
    getDomainStats,
    getContentSuggestions,

    // Utilities
    searchDomains,
    filterDomains,
    isDomainSelected,
    validateSelection,

    // Bulk operations
    selectMultipleDomains,
    clearSelection,
    selectRecommended
  }
}

export default useDomains