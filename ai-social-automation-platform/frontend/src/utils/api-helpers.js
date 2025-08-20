import { ERROR_MESSAGES } from './constants'

// HTTP status code helpers
export const isSuccessStatus = (status) => status >= 200 && status < 300
export const isClientError = (status) => status >= 400 && status < 500
export const isServerError = (status) => status >= 500

// Error handling helpers
export const getErrorMessage = (error) => {
  if (error.response) {
    // Server responded with error status
    const { status, data } = error.response
    
    if (data?.message) return data.message
    if (data?.error) return data.error
    
    switch (status) {
      case 400:
        return ERROR_MESSAGES.VALIDATION_ERROR
      case 401:
        return ERROR_MESSAGES.UNAUTHORIZED
      case 403:
        return ERROR_MESSAGES.FORBIDDEN
      case 404:
        return ERROR_MESSAGES.NOT_FOUND
      case 429:
        return ERROR_MESSAGES.RATE_LIMIT
      case 500:
        return ERROR_MESSAGES.SERVER_ERROR
      default:
        return `HTTP Error ${status}`
    }
  }
  
  if (error.request) {
    // Network error
    return ERROR_MESSAGES.NETWORK_ERROR
  }
  
  return error.message || 'An unexpected error occurred'
}

// Request helpers
export const buildQueryString = (params) => {
  const filteredParams = Object.entries(params)
    .filter(([_, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => {
      if (Array.isArray(value)) {
        return value.map(v => `${encodeURIComponent(key)}=${encodeURIComponent(v)}`).join('&')
      }
      return `${encodeURIComponent(key)}=${encodeURIComponent(value)}`
    })
  
  return filteredParams.length > 0 ? `?${filteredParams.join('&')}` : ''
}

export const buildFormData = (data) => {
  const formData = new FormData()
  
  Object.entries(data).forEach(([key, value]) => {
    if (value instanceof File) {
      formData.append(key, value)
    } else if (Array.isArray(value)) {
      value.forEach((item, index) => {
        if (item instanceof File) {
          formData.append(`${key}[${index}]`, item)
        } else {
          formData.append(`${key}[]`, item)
        }
      })
    } else if (value !== null && value !== undefined) {
      formData.append(key, value.toString())
    }
  })
  
  return formData
}

// Response helpers
export const extractData = (response) => {
  return response?.data || response
}

export const extractPagination = (response) => {
  const data = extractData(response)
  return {
    currentPage: data?.pagination?.currentPage || 1,
    totalPages: data?.pagination?.totalPages || 1,
    totalItems: data?.pagination?.totalItems || 0,
    itemsPerPage: data?.pagination?.itemsPerPage || 10,
    hasNextPage: data?.pagination?.hasNextPage || false,
    hasPrevPage: data?.pagination?.hasPrevPage || false
  }
}

// API endpoint helpers
export const buildEndpoint = (base, ...segments) => {
  const cleanSegments = segments
    .filter(segment => segment !== null && segment !== undefined)
    .map(segment => segment.toString().replace(/^\/+|\/+$/g, ''))
  
  return [base.replace(/\/+$/, ''), ...cleanSegments].join('/')
}

export const buildResourceEndpoint = (resource, id = null, action = null) => {
  let endpoint = `/${resource}`
  
  if (id) endpoint += `/${id}`
  if (action) endpoint += `/${action}`
  
  return endpoint
}

// Cache helpers
export const getCacheKey = (endpoint, params = {}) => {
  const queryString = buildQueryString(params)
  return `${endpoint}${queryString}`
}

export const isCacheValid = (timestamp, maxAge = 5 * 60 * 1000) => {
  return Date.now() - timestamp < maxAge
}

// Retry helpers
export const createRetryConfig = (maxRetries = 3, baseDelay = 1000) => {
  return {
    maxRetries,
    shouldRetry: (error) => {
      const status = error.response?.status
      // Retry on network errors or 5xx server errors
      return !status || status >= 500
    },
    getDelay: (attempt) => {
      // Exponential backoff with jitter
      const delay = baseDelay * Math.pow(2, attempt - 1)
      const jitter = Math.random() * 0.1 * delay
      return delay + jitter
    }
  }
}

export const withRetry = async (requestFn, retryConfig = createRetryConfig()) => {
  let lastError
  
  for (let attempt = 1; attempt <= retryConfig.maxRetries; attempt++) {
    try {
      return await requestFn()
    } catch (error) {
      lastError = error
      
      if (attempt === retryConfig.maxRetries || !retryConfig.shouldRetry(error)) {
        throw error
      }
      
      const delay = retryConfig.getDelay(attempt)
      await new Promise(resolve => setTimeout(resolve, delay))
    }
  }
  
  throw lastError
}

// Request timeout helper
export const withTimeout = (promise, timeoutMs = 10000) => {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Request timeout')), timeoutMs)
    })
  ])
}

// Batch request helper
export const batchRequests = async (requests, batchSize = 5) => {
  const results = []
  
  for (let i = 0; i < requests.length; i += batchSize) {
    const batch = requests.slice(i, i + batchSize)
    const batchResults = await Promise.allSettled(batch)
    results.push(...batchResults)
  }
  
  return results
}

// API response transformer
export const transformResponse = (response, transformer) => {
  if (typeof transformer === 'function') {
    return transformer(response)
  }
  
  return response
}

// Request interceptor helpers
export const addAuthHeader = (config, token) => {
  if (token) {
    config.headers = {
      ...config.headers,
      Authorization: `Bearer ${token}`
    }
  }
  return config
}

export const addTimestamp = (config) => {
  config.metadata = {
    ...config.metadata,
    timestamp: Date.now()
  }
  return config
}

// Response validation
export const validateResponse = (response, schema) => {
  if (!schema) return true
  
  try {
    if (typeof schema.validate === 'function') {
      return schema.validate(response)
    }
    
    // Simple object structure validation
    if (typeof schema === 'object') {
      return validateObjectStructure(response, schema)
    }
    
    return true
  } catch (error) {
    console.warn('Response validation failed:', error)
    return false
  }
}

const validateObjectStructure = (obj, schema) => {
  if (typeof obj !== 'object' || obj === null) return false
  
  for (const key in schema) {
    if (schema[key].required && !(key in obj)) {
      return false
    }
    
    if (key in obj && schema[key].type) {
      const expectedType = schema[key].type
      const actualType = typeof obj[key]
      
      if (expectedType === 'array' && !Array.isArray(obj[key])) {
        return false
      } else if (expectedType !== 'array' && actualType !== expectedType) {
        return false
      }
    }
  }
  
  return true
}

// Polling helper
export const poll = async (requestFn, options = {}) => {
  const {
    interval = 1000,
    maxAttempts = 30,
    condition = (response) => response?.status === 'complete'
  } = options
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const response = await requestFn()
      
      if (condition(response)) {
        return response
      }
      
      if (attempt < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, interval))
      }
    } catch (error) {
      if (attempt === maxAttempts) {
        throw error
      }
      
      await new Promise(resolve => setTimeout(resolve, interval))
    }
  }
  
  throw new Error('Polling timeout exceeded')
}

// File upload helpers
export const uploadFile = async (file, uploadFn, onProgress) => {
  const formData = new FormData()
  formData.append('file', file)
  
  return uploadFn(formData, {
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(progress)
      }
    }
  })
}

export const uploadFiles = async (files, uploadFn, onProgress) => {
  const uploads = Array.from(files).map((file, index) => {
    return uploadFile(file, uploadFn, (progress) => {
      if (onProgress) {
        onProgress(index, progress)
      }
    })
  })
  
  return Promise.all(uploads)
}

// Request deduplication
const pendingRequests = new Map()

export const deduplicateRequest = async (key, requestFn) => {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key)
  }
  
  const promise = requestFn().finally(() => {
    pendingRequests.delete(key)
  })
  
  pendingRequests.set(key, promise)
  return promise
}

// API status helpers
export const checkApiHealth = async (healthEndpoint) => {
  try {
    const response = await fetch(healthEndpoint, {
      method: 'GET',
      timeout: 5000
    })
    
    return {
      healthy: response.ok,
      status: response.status,
      timestamp: Date.now()
    }
  } catch (error) {
    return {
      healthy: false,
      error: error.message,
      timestamp: Date.now()
    }
  }
}

// Rate limiting helpers
export const createRateLimiter = (maxRequests = 100, windowMs = 60000) => {
  const requests = []
  
  return {
    canMakeRequest: () => {
      const now = Date.now()
      const windowStart = now - windowMs
      
      // Remove old requests
      while (requests.length > 0 && requests[0] < windowStart) {
        requests.shift()
      }
      
      return requests.length < maxRequests
    },
    
    recordRequest: () => {
      requests.push(Date.now())
    },
    
    getTimeUntilReset: () => {
      if (requests.length === 0) return 0
      
      const oldestRequest = requests[0]
      const windowEnd = oldestRequest + windowMs
      const now = Date.now()
      
      return Math.max(0, windowEnd - now)
    }
  }
}

// Request optimization helpers
export const optimizeRequest = (config) => {
  // Add compression
  if (!config.headers) config.headers = {}
  config.headers['Accept-Encoding'] = 'gzip, deflate, br'
  
  // Add cache control for GET requests
  if (config.method === 'GET' || !config.method) {
    config.headers['Cache-Control'] = 'no-cache'
  }
  
  // Add content type for POST/PUT/PATCH
  if (['POST', 'PUT', 'PATCH'].includes(config.method)) {
    if (!config.headers['Content-Type'] && !(config.data instanceof FormData)) {
      config.headers['Content-Type'] = 'application/json'
    }
  }
  
  return config
}

// Response caching
const responseCache = new Map()

export const cacheResponse = (key, response, ttl = 300000) => {
  const cacheEntry = {
    data: response,
    timestamp: Date.now(),
    ttl
  }
  
  responseCache.set(key, cacheEntry)
  
  // Auto cleanup
  setTimeout(() => {
    responseCache.delete(key)
  }, ttl)
  
  return response
}

export const getCachedResponse = (key) => {
  const entry = responseCache.get(key)
  
  if (!entry) return null
  
  const isExpired = Date.now() - entry.timestamp > entry.ttl
  if (isExpired) {
    responseCache.delete(key)
    return null
  }
  
  return entry.data
}

// Mock API helpers for development
export const createMockResponse = (data, delay = 500) => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        data,
        status: 200,
        statusText: 'OK',
        headers: {},
        config: {}
      })
    }, delay)
  })
}

export const createMockError = (status = 500, message = 'Mock error', delay = 500) => {
  return new Promise((_, reject) => {
    setTimeout(() => {
      const error = new Error(message)
      error.response = {
        status,
        statusText: 'Error',
        data: { message }
      }
      reject(error)
    }, delay)
  })
}

// Performance monitoring
export const withPerformanceMonitoring = async (requestFn, label) => {
  const startTime = performance.now()
  
  try {
    const result = await requestFn()
    const endTime = performance.now()
    const duration = endTime - startTime
    
    console.log(`API Request [${label}]: ${duration.toFixed(2)}ms`)
    
    // Send to analytics if available
    if (window.analytics && window.analytics.track) {
      window.analytics.track('API Request', {
        label,
        duration,
        success: true
      })
    }
    
    return result
  } catch (error) {
    const endTime = performance.now()
    const duration = endTime - startTime
    
    console.error(`API Request [${label}] failed after ${duration.toFixed(2)}ms:`, error)
    
    // Send to analytics if available
    if (window.analytics && window.analytics.track) {
      window.analytics.track('API Request', {
        label,
        duration,
        success: false,
        error: error.message
      })
    }
    
    throw error
  }
}

// Request logging
export const logRequest = (config) => {
  if (process.env.NODE_ENV === 'development') {
    console.group(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`)
    console.log('Config:', config)
    console.log('Headers:', config.headers)
    if (config.data) console.log('Data:', config.data)
    console.groupEnd()
  }
}

export const logResponse = (response) => {
  if (process.env.NODE_ENV === 'development') {
    console.group(`✅ API Response: ${response.status} ${response.config?.url}`)
    console.log('Status:', response.status, response.statusText)
    console.log('Headers:', response.headers)
    console.log('Data:', response.data)
    console.groupEnd()
  }
}

export const logError = (error) => {
  if (process.env.NODE_ENV === 'development') {
    console.group(`❌ API Error: ${error.config?.url}`)
    console.error('Error:', error.message)
    if (error.response) {
      console.log('Response:', error.response.status, error.response.data)
    }
    console.log('Config:', error.config)
    console.groupEnd()
  }
}

export default {
  isSuccessStatus,
  isClientError,
  isServerError,
  getErrorMessage,
  buildQueryString,
  buildFormData,
  extractData,
  extractPagination,
  buildEndpoint,
  buildResourceEndpoint,
  getCacheKey,
  isCacheValid,
  createRetryConfig,
  withRetry,
  withTimeout,
  batchRequests,
  transformResponse,
  addAuthHeader,
  addTimestamp,
  validateResponse,
  poll,
  uploadFile,
  uploadFiles,
  deduplicateRequest,
  checkApiHealth,
  createRateLimiter,
  optimizeRequest,
  cacheResponse,
  getCachedResponse,
  createMockResponse,
  createMockError,
  withPerformanceMonitoring,
  logRequest,
  logResponse,
  logError
}