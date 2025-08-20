import { useState, useEffect, useCallback } from 'react'
import { analytics } from '../services/apiService'
import useToast from './useToast'

const useAnalytics = (timeRange = '30d') => {
  const [data, setData] = useState({
    dashboard: null,
    engagement: null,
    growth: null,
    platforms: null,
    insights: null
  })
  const [loading, setLoading] = useState({
    dashboard: false,
    engagement: false,
    growth: false,
    platforms: false,
    insights: false
  })
  const [errors, setErrors] = useState({})
  const { error: showError } = useToast()

  // Set loading state for specific data type
  const setDataLoading = useCallback((dataType, isLoading) => {
    setLoading(prev => ({ ...prev, [dataType]: isLoading }))
  }, [])

  // Set error state for specific data type
  const setDataError = useCallback((dataType, error) => {
    setErrors(prev => ({ ...prev, [dataType]: error }))
    if (error) {
      showError(`Failed to load ${dataType} data: ${error.message}`)
    }
  }, [showError])

  // Fetch dashboard analytics
  const fetchDashboard = useCallback(async (customTimeRange = timeRange) => {
    setDataLoading('dashboard', true)
    setDataError('dashboard', null)
    
    try {
      const dashboardData = await analytics.getDashboard(customTimeRange)
      setData(prev => ({ ...prev, dashboard: dashboardData }))
      return dashboardData
    } catch (error) {
      setDataError('dashboard', error)
      return null
    } finally {
      setDataLoading('dashboard', false)
    }
  }, [timeRange, setDataLoading, setDataError])

  // Fetch engagement data
  const fetchEngagement = useCallback(async (params = {}) => {
    setDataLoading('engagement', true)
    setDataError('engagement', null)
    
    try {
      const engagementData = await analytics.getEngagement({
        timeRange,
        ...params
      })
      setData(prev => ({ ...prev, engagement: engagementData }))
      return engagementData
    } catch (error) {
      setDataError('engagement', error)
      return null
    } finally {
      setDataLoading('engagement', false)
    }
  }, [timeRange, setDataLoading, setDataError])

  // Fetch growth metrics
  const fetchGrowth = useCallback(async (params = {}) => {
    setDataLoading('growth', true)
    setDataError('growth', null)
    
    try {
      const growthData = await analytics.getGrowth({
        timeRange,
        ...params
      })
      setData(prev => ({ ...prev, growth: growthData }))
      return growthData
    } catch (error) {
      setDataError('growth', error)
      return null
    } finally {
      setDataLoading('growth', false)
    }
  }, [timeRange, setDataLoading, setDataError])

  // Fetch platform breakdown
  const fetchPlatforms = useCallback(async (customTimeRange = timeRange) => {
    setDataLoading('platforms', true)
    setDataError('platforms', null)
    
    try {
      const platformData = await analytics.getPlatformBreakdown(customTimeRange)
      setData(prev => ({ ...prev, platforms: platformData }))
      return platformData
    } catch (error) {
      setDataError('platforms', error)
      return null
    } finally {
      setDataLoading('platforms', false)
    }
  }, [timeRange, setDataLoading, setDataError])

  // Fetch insights
  const fetchInsights = useCallback(async (customTimeRange = timeRange) => {
    setDataLoading('insights', true)
    setDataError('insights', null)
    
    try {
      const insightsData = await analytics.getInsights(customTimeRange)
      setData(prev => ({ ...prev, insights: insightsData }))
      return insightsData
    } catch (error) {
      setDataError('insights', error)
      return null
    } finally {
      setDataLoading('insights', false)
    }
  }, [timeRange, setDataLoading, setDataError])

  // Fetch all analytics data
  const fetchAll = useCallback(async (customTimeRange = timeRange) => {
    const promises = [
      fetchDashboard(customTimeRange),
      fetchEngagement({ timeRange: customTimeRange }),
      fetchGrowth({ timeRange: customTimeRange }),
      fetchPlatforms(customTimeRange),
      fetchInsights(customTimeRange)
    ]
    
    const results = await Promise.allSettled(promises)
    
    return {
      dashboard: results[0].status === 'fulfilled' ? results[0].value : null,
      engagement: results[1].status === 'fulfilled' ? results[1].value : null,
      growth: results[2].status === 'fulfilled' ? results[2].value : null,
      platforms: results[3].status === 'fulfilled' ? results[3].value : null,
      insights: results[4].status === 'fulfilled' ? results[4].value : null
    }
  }, [timeRange, fetchDashboard, fetchEngagement, fetchGrowth, fetchPlatforms, fetchInsights])

  // Export analytics data
  const exportData = useCallback(async (config) => {
    setDataLoading('export', true)
    setDataError('export', null)
    
    try {
      const response = await analytics.exportData(config)
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `analytics-${config.format}-${Date.now()}.${config.format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (error) {
      setDataError('export', error)
      return false
    } finally {
      setDataLoading('export', false)
    }
  }, [setDataLoading, setDataError])

  // Calculate metrics helpers
  const calculateGrowthRate = useCallback((current, previous) => {
    if (!previous || previous === 0) return 0
    return ((current - previous) / previous) * 100
  }, [])

  const calculateEngagementRate = useCallback((engagement, reach) => {
    if (!reach || reach === 0) return 0
    return (engagement / reach) * 100
  }, [])

  const getTopPerformingPlatform = useCallback(() => {
    if (!data.platforms || !data.platforms.length) return null
    
    return data.platforms.reduce((top, platform) => {
      const currentEngagement = platform.engagement || 0
      const topEngagement = top?.engagement || 0
      return currentEngagement > topEngagement ? platform : top
    }, data.platforms[0])
  }, [data.platforms])

  const getBestPostingTime = useCallback((platformId = null) => {
    if (!data.insights?.optimalTimes) return null
    
    if (platformId) {
      return data.insights.optimalTimes[platformId] || null
    }
    
    // Return overall best time
    return data.insights.optimalTimes.overall || null
  }, [data.insights])

  const getContentPerformance = useCallback((contentType = null) => {
    if (!data.insights?.contentPerformance) return null
    
    if (contentType) {
      return data.insights.contentPerformance[contentType] || null
    }
    
    return data.insights.contentPerformance
  }, [data.insights])

  // Refresh specific data
  const refresh = useCallback(async (dataTypes = ['dashboard']) => {
    const promises = []
    
    if (dataTypes.includes('dashboard')) promises.push(fetchDashboard())
    if (dataTypes.includes('engagement')) promises.push(fetchEngagement())
    if (dataTypes.includes('growth')) promises.push(fetchGrowth())
    if (dataTypes.includes('platforms')) promises.push(fetchPlatforms())
    if (dataTypes.includes('insights')) promises.push(fetchInsights())
    
    await Promise.allSettled(promises)
  }, [fetchDashboard, fetchEngagement, fetchGrowth, fetchPlatforms, fetchInsights])

  // Auto-refresh data
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [refreshInterval, setRefreshInterval] = useState(5 * 60 * 1000) // 5 minutes

  useEffect(() => {
    if (!autoRefresh) return

    const interval = setInterval(() => {
      refresh(['dashboard', 'engagement'])
    }, refreshInterval)

    return () => clearInterval(interval)
  }, [autoRefresh, refreshInterval, refresh])

  // Load initial data
  useEffect(() => {
    fetchDashboard()
  }, [fetchDashboard])

  // Check if any data is loading
  const isLoading = Object.values(loading).some(Boolean)

  // Check if all data is loaded
  const isLoaded = data.dashboard !== null

  // Get summary stats
  const getSummary = useCallback(() => {
    if (!data.dashboard) return null

    return {
      totalFollowers: data.dashboard.totalFollowers || 0,
      totalPosts: data.dashboard.totalPosts || 0,
      totalEngagement: data.dashboard.totalEngagement || 0,
      engagementRate: data.dashboard.engagementRate || 0,
      growthRate: data.dashboard.growthRate || 0,
      topPlatform: getTopPerformingPlatform()?.name || 'N/A',
      bestPostingTime: getBestPostingTime() || 'N/A'
    }
  }, [data.dashboard, getTopPerformingPlatform, getBestPostingTime])

  return {
    // Data
    data,
    
    // Loading states
    loading,
    isLoading,
    isLoaded,
    
    // Error states
    errors,
    
    // Fetch functions
    fetchDashboard,
    fetchEngagement,
    fetchGrowth,
    fetchPlatforms,
    fetchInsights,
    fetchAll,
    
    // Utility functions
    exportData,
    refresh,
    calculateGrowthRate,
    calculateEngagementRate,
    getTopPerformingPlatform,
    getBestPostingTime,
    getContentPerformance,
    getSummary,
    
    // Auto-refresh
    autoRefresh,
    setAutoRefresh,
    refreshInterval,
    setRefreshInterval,
    
    // Time range
    timeRange
  }
}

export default useAnalytics