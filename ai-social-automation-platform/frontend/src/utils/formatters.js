// Date formatters
export const formatDate = (date, format = 'short') => {
  const d = new Date(date)
  
  const formats = {
    short: d.toLocaleDateString(),
    long: d.toLocaleDateString('en-US', { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    }),
    time: d.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit' 
    }),
    datetime: d.toLocaleString('en-US', { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    }),
    relative: formatRelativeTime(d)
  }
  
  return formats[format] || formats.short
}

export const formatRelativeTime = (date) => {
  const now = new Date()
  const diffInSeconds = Math.floor((now - new Date(date)) / 1000)
  
  if (diffInSeconds < 60) return 'Just now'
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`
  
  return formatDate(date, 'short')
}

// Number formatters
export const formatNumber = (num, decimals = 0) => {
  if (num === null || num === undefined) return '0'
  return Number(num).toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  })
}

export const formatCompactNumber = (num) => {
  if (num === null || num === undefined) return '0'
  
  const absNum = Math.abs(num)
  
  if (absNum >= 1000000) {
    return (num / 1000000).toFixed(1) + 'M'
  }
  if (absNum >= 1000) {
    return (num / 1000).toFixed(1) + 'K'
  }
  
  return num.toString()
}

export const formatPercentage = (value, decimals = 1) => {
  if (value === null || value === undefined) return '0%'
  return `${Number(value).toFixed(decimals)}%`
}

export const formatCurrency = (amount, currency = 'USD') => {
  if (amount === null || amount === undefined) return '$0.00'
  
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 2
  }).format(amount)
}

// Text formatters
export const formatText = (text, maxLength = 100) => {
  if (!text) return ''
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export const formatHashtags = (text) => {
  if (!text) return ''
  return text.replace(/#(\w+)/g, '<span class="text-blue-600">#$1</span>')
}

export const formatMentions = (text) => {
  if (!text) return ''
  return text.replace(/@(\w+)/g, '<span class="text-blue-600">@$1</span>')
}

export const formatUrls = (text) => {
  if (!text) return ''
  const urlRegex = /(https?:\/\/[^\s]+)/g
  return text.replace(urlRegex, '<a href="$1" target="_blank" class="text-blue-600 underline">$1</a>')
}

// Platform specific formatters
export const formatPlatformContent = (content, platform) => {
  if (!content) return ''
  
  const maxLengths = {
    twitter: 280,
    instagram: 2200,
    facebook: 63206,
    linkedin: 3000,
    youtube: 5000
  }
  
  const maxLength = maxLengths[platform] || 1000
  return formatText(content, maxLength)
}

export const formatPlatformMetrics = (metrics, platform) => {
  const platformLabels = {
    instagram: {
      likes: 'Likes',
      comments: 'Comments',
      shares: 'Shares',
      saves: 'Saves',
      reach: 'Reach'
    },
    facebook: {
      likes: 'Reactions',
      comments: 'Comments',
      shares: 'Shares',
      reach: 'Reach'
    },
    twitter: {
      likes: 'Likes',
      comments: 'Replies',
      shares: 'Retweets',
      reach: 'Impressions'
    },
    linkedin: {
      likes: 'Reactions',
      comments: 'Comments',
      shares: 'Shares',
      reach: 'Impressions'
    },
    youtube: {
      likes: 'Likes',
      comments: 'Comments',
      shares: 'Shares',
      views: 'Views'
    }
  }
  
  const labels = platformLabels[platform] || platformLabels.instagram
  const formatted = {}
  
  Object.keys(metrics).forEach(key => {
    const label = labels[key] || key.charAt(0).toUpperCase() + key.slice(1)
    formatted[label] = formatCompactNumber(metrics[key])
  })
  
  return formatted
}

// File size formatter
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// Duration formatter
export const formatDuration = (seconds) => {
  if (!seconds) return '0:00'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${remainingSeconds.toString().padStart(2, '0')}`
  }
  
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

// Username formatter
export const formatUsername = (username, platform) => {
  if (!username) return ''
  
  const prefixes = {
    twitter: '@',
    instagram: '@',
    tiktok: '@',
    youtube: '',
    facebook: '',
    linkedin: ''
  }
  
  const prefix = prefixes[platform] || '@'
  return username.startsWith(prefix) ? username : prefix + username
}

// Engagement rate formatter
export const formatEngagementRate = (engagement, followers) => {
  if (!engagement || !followers || followers === 0) return '0%'
  
  const rate = (engagement / followers) * 100
  return formatPercentage(rate)
}

// Growth rate formatter
export const formatGrowthRate = (current, previous) => {
  if (!current || !previous || previous === 0) return '0%'
  
  const growth = ((current - previous) / previous) * 100
  const sign = growth > 0 ? '+' : ''
  return `${sign}${formatPercentage(growth)}`
}

// Color formatter for metrics
export const getMetricColor = (value, type = 'neutral') => {
  const colors = {
    positive: value > 0 ? 'text-green-600' : value < 0 ? 'text-red-600' : 'text-gray-600',
    engagement: value > 3 ? 'text-green-600' : value > 1 ? 'text-yellow-600' : 'text-red-600',
    growth: value > 0 ? 'text-green-600' : value < 0 ? 'text-red-600' : 'text-gray-600',
    neutral: 'text-gray-600'
  }
  
  return colors[type] || colors.neutral
}

// Status formatter
export const formatStatus = (status) => {
  const statusMap = {
    active: { label: 'Active', color: 'green' },
    inactive: { label: 'Inactive', color: 'gray' },
    pending: { label: 'Pending', color: 'yellow' },
    failed: { label: 'Failed', color: 'red' },
    success: { label: 'Success', color: 'green' },
    processing: { label: 'Processing', color: 'blue' },
    cancelled: { label: 'Cancelled', color: 'gray' },
    scheduled: { label: 'Scheduled', color: 'yellow' },
    published: { label: 'Published', color: 'green' },
    draft: { label: 'Draft', color: 'gray' }
  }
  
  return statusMap[status] || { label: status, color: 'gray' }
}

// Array formatter
export const formatList = (items, maxItems = 3, separator = ', ') => {
  if (!items || !Array.isArray(items)) return ''
  
  if (items.length <= maxItems) {
    return items.join(separator)
  }
  
  const visible = items.slice(0, maxItems)
  const remaining = items.length - maxItems
  
  return `${visible.join(separator)} and ${remaining} more`
}

// Phone number formatter
export const formatPhoneNumber = (phone) => {
  if (!phone) return ''
  
  const cleaned = phone.replace(/\D/g, '')
  const match = cleaned.match(/^(\d{3})(\d{3})(\d{4})$/)
  
  if (match) {
    return `(${match[1]}) ${match[2]}-${match[3]}`
  }
  
  return phone
}

// Social media handle formatter
export const formatSocialHandle = (handle, platform) => {
  if (!handle) return ''
  
  // Remove existing @ or platform-specific prefixes
  const cleaned = handle.replace(/^@/, '').replace(/^https?:\/\/[^\/]+\//, '')
  
  return formatUsername(cleaned, platform)
}

export default {
  formatDate,
  formatRelativeTime,
  formatNumber,
  formatCompactNumber,
  formatPercentage,
  formatCurrency,
  formatText,
  formatHashtags,
  formatMentions,
  formatUrls,
  formatPlatformContent,
  formatPlatformMetrics,
  formatFileSize,
  formatDuration,
  formatUsername,
  formatEngagementRate,
  formatGrowthRate,
  getMetricColor,
  formatStatus,
  formatList,
  formatPhoneNumber,
  formatSocialHandle
}