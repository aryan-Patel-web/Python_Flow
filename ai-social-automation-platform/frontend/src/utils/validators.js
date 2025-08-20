// Email validation
export const validateEmail = (email) => {
  if (!email) return 'Email is required'
  
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!emailRegex.test(email)) {
    return 'Please enter a valid email address'
  }
  
  return null
}

// Password validation
export const validatePassword = (password, options = {}) => {
  const {
    minLength = 6,
    requireUppercase = false,
    requireLowercase = false,
    requireNumber = false,
    requireSpecial = false
  } = options
  
  if (!password) return 'Password is required'
  
  if (password.length < minLength) {
    return `Password must be at least ${minLength} characters long`
  }
  
  if (requireUppercase && !/[A-Z]/.test(password)) {
    return 'Password must contain at least one uppercase letter'
  }
  
  if (requireLowercase && !/[a-z]/.test(password)) {
    return 'Password must contain at least one lowercase letter'
  }
  
  if (requireNumber && !/\d/.test(password)) {
    return 'Password must contain at least one number'
  }
  
  if (requireSpecial && !/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    return 'Password must contain at least one special character'
  }
  
  return null
}

// Confirm password validation
export const validateConfirmPassword = (password, confirmPassword) => {
  if (!confirmPassword) return 'Please confirm your password'
  
  if (password !== confirmPassword) {
    return 'Passwords do not match'
  }
  
  return null
}

// Name validation
export const validateName = (name, fieldName = 'Name') => {
  if (!name || !name.trim()) return `${fieldName} is required`
  
  if (name.trim().length < 2) {
    return `${fieldName} must be at least 2 characters long`
  }
  
  if (name.trim().length > 50) {
    return `${fieldName} must be less than 50 characters`
  }
  
  return null
}

// Username validation
export const validateUsername = (username) => {
  if (!username) return 'Username is required'
  
  if (username.length < 3) {
    return 'Username must be at least 3 characters long'
  }
  
  if (username.length > 30) {
    return 'Username must be less than 30 characters'
  }
  
  if (!/^[a-zA-Z0-9_]+$/.test(username)) {
    return 'Username can only contain letters, numbers, and underscores'
  }
  
  return null
}

// Phone number validation
export const validatePhoneNumber = (phone) => {
  if (!phone) return 'Phone number is required'
  
  const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/
  const cleaned = phone.replace(/\D/g, '')
  
  if (!phoneRegex.test(cleaned)) {
    return 'Please enter a valid phone number'
  }
  
  return null
}

// URL validation
export const validateUrl = (url, fieldName = 'URL') => {
  if (!url) return `${fieldName} is required`
  
  try {
    new URL(url)
    return null
  } catch {
    return `Please enter a valid ${fieldName.toLowerCase()}`
  }
}

// Social media handle validation
export const validateSocialHandle = (handle, platform) => {
  if (!handle) return 'Handle is required'
  
  // Remove @ symbol if present
  const cleanHandle = handle.replace(/^@/, '')
  
  const platformRules = {
    instagram: {
      minLength: 1,
      maxLength: 30,
      pattern: /^[a-zA-Z0-9._]+$/,
      message: 'Instagram handle can only contain letters, numbers, periods, and underscores'
    },
    twitter: {
      minLength: 1,
      maxLength: 15,
      pattern: /^[a-zA-Z0-9_]+$/,
      message: 'Twitter handle can only contain letters, numbers, and underscores'
    },
    facebook: {
      minLength: 5,
      maxLength: 50,
      pattern: /^[a-zA-Z0-9.]+$/,
      message: 'Facebook username can only contain letters, numbers, and periods'
    },
    linkedin: {
      minLength: 3,
      maxLength: 100,
      pattern: /^[a-zA-Z0-9-]+$/,
      message: 'LinkedIn handle can only contain letters, numbers, and hyphens'
    },
    youtube: {
      minLength: 3,
      maxLength: 30,
      pattern: /^[a-zA-Z0-9_-]+$/,
      message: 'YouTube handle can only contain letters, numbers, underscores, and hyphens'
    }
  }
  
  const rules = platformRules[platform]
  if (!rules) return null
  
  if (cleanHandle.length < rules.minLength) {
    return `Handle must be at least ${rules.minLength} characters long`
  }
  
  if (cleanHandle.length > rules.maxLength) {
    return `Handle must be less than ${rules.maxLength} characters`
  }
  
  if (!rules.pattern.test(cleanHandle)) {
    return rules.message
  }
  
  return null
}

// Content validation
export const validateContent = (content, platform, contentType = 'post') => {
  if (!content || !content.trim()) return 'Content is required'
  
  const limits = {
    twitter: { post: 280 },
    instagram: { post: 2200, story: 2200 },
    facebook: { post: 63206 },
    linkedin: { post: 3000 },
    youtube: { description: 5000 },
    tiktok: { description: 300 }
  }
  
  const limit = limits[platform]?.[contentType] || 1000
  
  if (content.length > limit) {
    return `Content must be less than ${limit} characters for ${platform}`
  }
  
  return null
}

// File validation
export const validateFile = (file, options = {}) => {
  const {
    maxSize = 10 * 1024 * 1024, // 10MB
    allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif'],
    fieldName = 'File'
  } = options
  
  if (!file) return `${fieldName} is required`
  
  if (file.size > maxSize) {
    const sizeMB = Math.round(maxSize / (1024 * 1024))
    return `${fieldName} must be smaller than ${sizeMB}MB`
  }
  
  if (!allowedTypes.includes(file.type)) {
    const types = allowedTypes.map(type => type.split('/')[1]).join(', ')
    return `${fieldName} must be one of: ${types}`
  }
  
  return null
}

// Date validation
export const validateDate = (date, fieldName = 'Date') => {
  if (!date) return `${fieldName} is required`
  
  const selectedDate = new Date(date)
  const now = new Date()
  
  if (isNaN(selectedDate.getTime())) {
    return `Please enter a valid ${fieldName.toLowerCase()}`
  }
  
  if (selectedDate < now) {
    return `${fieldName} must be in the future`
  }
  
  return null
}

// Time validation
export const validateTime = (time, fieldName = 'Time') => {
  if (!time) return `${fieldName} is required`
  
  const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/
  if (!timeRegex.test(time)) {
    return `Please enter a valid ${fieldName.toLowerCase()} (HH:MM)`
  }
  
  return null
}

// Required field validation
export const validateRequired = (value, fieldName = 'Field') => {
  if (value === null || value === undefined || value === '' || 
      (Array.isArray(value) && value.length === 0) ||
      (typeof value === 'object' && Object.keys(value).length === 0)) {
    return `${fieldName} is required`
  }
  
  return null
}

// Numeric validation
export const validateNumber = (value, options = {}) => {
  const {
    min,
    max,
    integer = false,
    fieldName = 'Value'
  } = options
  
  if (!value && value !== 0) return `${fieldName} is required`
  
  const num = parseFloat(value)
  
  if (isNaN(num)) {
    return `${fieldName} must be a valid number`
  }
  
  if (integer && !Number.isInteger(num)) {
    return `${fieldName} must be a whole number`
  }
  
  if (min !== undefined && num < min) {
    return `${fieldName} must be at least ${min}`
  }
  
  if (max !== undefined && num > max) {
    return `${fieldName} must be no more than ${max}`
  }
  
  return null
}

// Length validation
export const validateLength = (value, options = {}) => {
  const {
    min = 0,
    max = Infinity,
    fieldName = 'Field'
  } = options
  
  if (!value) return `${fieldName} is required`
  
  const length = value.length
  
  if (length < min) {
    return `${fieldName} must be at least ${min} characters long`
  }
  
  if (length > max) {
    return `${fieldName} must be no more than ${max} characters long`
  }
  
  return null
}

// Array validation
export const validateArray = (array, options = {}) => {
  const {
    minItems = 0,
    maxItems = Infinity,
    fieldName = 'Items'
  } = options
  
  if (!Array.isArray(array)) {
    return `${fieldName} must be a list`
  }
  
  if (array.length < minItems) {
    return `Please select at least ${minItems} ${fieldName.toLowerCase()}`
  }
  
  if (array.length > maxItems) {
    return `Please select no more than ${maxItems} ${fieldName.toLowerCase()}`
  }
  
  return null
}

// Form validation helper
export const validateForm = (data, rules) => {
  const errors = {}
  
  Object.keys(rules).forEach(field => {
    const fieldRules = Array.isArray(rules[field]) ? rules[field] : [rules[field]]
    const value = data[field]
    
    for (const rule of fieldRules) {
      const error = rule(value)
      if (error) {
        errors[field] = error
        break // Stop at first error for this field
      }
    }
  })
  
  return {
    isValid: Object.keys(errors).length === 0,
    errors
  }
}

// Async validation helper
export const validateAsync = async (value, asyncValidator) => {
  try {
    const result = await asyncValidator(value)
    return result
  } catch (error) {
    return error.message || 'Validation failed'
  }
}

export default {
  validateEmail,
  validatePassword,
  validateConfirmPassword,
  validateName,
  validateUsername,
  validatePhoneNumber,
  validateUrl,
  validateSocialHandle,
  validateContent,
  validateFile,
  validateDate,
  validateTime,
  validateRequired,
  validateNumber,
  validateLength,
  validateArray,
  validateForm,
  validateAsync
}