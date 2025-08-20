import apiService from './apiService'

class BillingService {
  constructor() {
    this.cache = new Map()
    this.cacheTimeout = 5 * 60 * 1000 // 5 minutes
  }

  // Cache helper methods
  getCacheKey(method, params = {}) {
    return `${method}_${JSON.stringify(params)}`
  }

  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    })
  }

  getCache(key) {
    const cached = this.cache.get(key)
    if (cached && (Date.now() - cached.timestamp) < this.cacheTimeout) {
      return cached.data
    }
    this.cache.delete(key)
    return null
  }

  clearCache() {
    this.cache.clear()
  }

  // Subscription Management
  async getSubscription() {
    const cacheKey = this.getCacheKey('subscription')
    const cached = this.getCache(cacheKey)
    if (cached) return cached

    try {
      const subscription = await apiService.billing.getSubscription()
      this.setCache(cacheKey, subscription)
      return subscription
    } catch (error) {
      console.error('Failed to fetch subscription:', error)
      throw error
    }
  }

  async getPlans() {
    const cacheKey = this.getCacheKey('plans')
    const cached = this.getCache(cacheKey)
    if (cached) return cached

    try {
      const plans = await apiService.billing.getPlans()
      this.setCache(cacheKey, plans)
      return plans
    } catch (error) {
      console.error('Failed to fetch plans:', error)
      throw error
    }
  }

  async subscribe(planId, paymentMethodId, promoCode = null) {
    try {
      const subscription = await apiService.billing.subscribe(planId, paymentMethodId, promoCode)
      this.clearCache() // Clear cache after subscription change
      return subscription
    } catch (error) {
      console.error('Subscription failed:', error)
      throw error
    }
  }

  async updateSubscription(planId) {
    try {
      const subscription = await apiService.billing.updateSubscription(planId)
      this.clearCache() // Clear cache after update
      return subscription
    } catch (error) {
      console.error('Failed to update subscription:', error)
      throw error
    }
  }

  async cancelSubscription(reason = null, feedback = null) {
    try {
      const result = await apiService.billing.cancelSubscription({ reason, feedback })
      this.clearCache() // Clear cache after cancellation
      return result
    } catch (error) {
      console.error('Failed to cancel subscription:', error)
      throw error
    }
  }

  async pauseSubscription(pauseUntil = null) {
    try {
      const subscription = await apiService.billing.pauseSubscription({ pauseUntil })
      this.clearCache()
      return subscription
    } catch (error) {
      console.error('Failed to pause subscription:', error)
      throw error
    }
  }

  async resumeSubscription() {
    try {
      const subscription = await apiService.billing.resumeSubscription()
      this.clearCache()
      return subscription
    } catch (error) {
      console.error('Failed to resume subscription:', error)
      throw error
    }
  }

  // Usage Tracking
  async getUsage(period = 'current') {
    const cacheKey = this.getCacheKey('usage', { period })
    const cached = this.getCache(cacheKey)
    if (cached) return cached

    try {
      const usage = await apiService.billing.getUsage(period)
      this.setCache(cacheKey, usage)
      return usage
    } catch (error) {
      console.error('Failed to fetch usage:', error)
      throw error
    }
  }

  async getUsageHistory(months = 6) {
    try {
      return await apiService.billing.getUsageHistory(months)
    } catch (error) {
      console.error('Failed to fetch usage history:', error)
      throw error
    }
  }

  // Invoice Management
  async getInvoices(limit = 10, offset = 0) {
    try {
      return await apiService.billing.getInvoices({ limit, offset })
    } catch (error) {
      console.error('Failed to fetch invoices:', error)
      throw error
    }
  }

  async getInvoice(invoiceId) {
    try {
      return await apiService.billing.getInvoice(invoiceId)
    } catch (error) {
      console.error('Failed to fetch invoice:', error)
      throw error
    }
  }

  async downloadInvoice(invoiceId, format = 'pdf') {
    try {
      const response = await apiService.billing.downloadInvoice(invoiceId, format)
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `invoice-${invoiceId}.${format}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
      
      return true
    } catch (error) {
      console.error('Failed to download invoice:', error)
      throw error
    }
  }

  // Payment Methods
  async getPaymentMethods() {
    const cacheKey = this.getCacheKey('payment_methods')
    const cached = this.getCache(cacheKey)
    if (cached) return cached

    try {
      const paymentMethods = await apiService.billing.getPaymentMethods()
      this.setCache(cacheKey, paymentMethods)
      return paymentMethods
    } catch (error) {
      console.error('Failed to fetch payment methods:', error)
      throw error
    }
  }

  async addPaymentMethod(paymentMethodData) {
    try {
      const paymentMethod = await apiService.billing.addPaymentMethod(paymentMethodData)
      this.clearCache() // Clear cache after adding payment method
      return paymentMethod
    } catch (error) {
      console.error('Failed to add payment method:', error)
      throw error
    }
  }

  async deletePaymentMethod(paymentMethodId) {
    try {
      await apiService.billing.deletePaymentMethod(paymentMethodId)
      this.clearCache() // Clear cache after deletion
      return true
    } catch (error) {
      console.error('Failed to delete payment method:', error)
      throw error
    }
  }

  async setDefaultPaymentMethod(paymentMethodId) {
    try {
      await apiService.billing.setDefaultPaymentMethod(paymentMethodId)
      this.clearCache() // Clear cache after update
      return true
    } catch (error) {
      console.error('Failed to set default payment method:', error)
      throw error
    }
  }

  // Promo Codes & Discounts
  async validatePromoCode(promoCode) {
    try {
      return await apiService.billing.validatePromoCode(promoCode)
    } catch (error) {
      console.error('Failed to validate promo code:', error)
      throw error
    }
  }

  async applyPromoCode(promoCode) {
    try {
      const result = await apiService.billing.applyPromoCode(promoCode)
      this.clearCache() // Clear cache after applying promo
      return result
    } catch (error) {
      console.error('Failed to apply promo code:', error)
      throw error
    }
  }

  // Billing Preferences
  async getBillingPreferences() {
    try {
      return await apiService.billing.getBillingPreferences()
    } catch (error) {
      console.error('Failed to fetch billing preferences:', error)
      throw error
    }
  }

  async updateBillingPreferences(preferences) {
    try {
      return await apiService.billing.updateBillingPreferences(preferences)
    } catch (error) {
      console.error('Failed to update billing preferences:', error)
      throw error
    }
  }

  // Utility Methods
  calculatePlanCost(plan, billingCycle = 'monthly', promoDiscount = 0) {
    const basePrice = billingCycle === 'yearly' ? plan.yearlyPrice : plan.monthlyPrice
    const discount = billingCycle === 'yearly' ? plan.yearlyDiscount || 0 : 0
    const promoDiscountAmount = (basePrice * promoDiscount) / 100
    
    return {
      basePrice,
      discount,
      promoDiscount: promoDiscountAmount,
      finalPrice: basePrice - discount - promoDiscountAmount,
      savings: discount + promoDiscountAmount
    }
  }

  formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount)
  }

  getUsagePercentage(used, limit) {
    if (!limit || limit === 0) return 0
    return Math.min((used / limit) * 100, 100)
  }

  isUsageLimitReached(used, limit, threshold = 0.9) {
    return this.getUsagePercentage(used, limit) >= (threshold * 100)
  }

  getDaysUntilBilling(nextBillingDate) {
    const today = new Date()
    const billingDate = new Date(nextBillingDate)
    const diffTime = billingDate - today
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    return Math.max(0, diffDays)
  }

  getTrialDaysRemaining(trialEndDate) {
    if (!trialEndDate) return 0
    return this.getDaysUntilBilling(trialEndDate)
  }

  isTrialExpired(trialEndDate) {
    if (!trialEndDate) return false
    return new Date() > new Date(trialEndDate)
  }

  canUpgrade(currentPlan, targetPlan) {
    const planHierarchy = ['starter', 'pro', 'agency']
    const currentIndex = planHierarchy.indexOf(currentPlan?.id)
    const targetIndex = planHierarchy.indexOf(targetPlan?.id)
    
    return targetIndex > currentIndex
  }

  canDowngrade(currentPlan, targetPlan) {
    const planHierarchy = ['starter', 'pro', 'agency']
    const currentIndex = planHierarchy.indexOf(currentPlan?.id)
    const targetIndex = planHierarchy.indexOf(targetPlan?.id)
    
    return targetIndex < currentIndex
  }

  getFeatureAvailability(userPlan, feature) {
    const planFeatures = {
      starter: ['basic_analytics', 'basic_support', 'basic_content'],
      pro: ['basic_analytics', 'advanced_analytics', 'priority_support', 'all_content', 'custom_scheduling'],
      agency: ['basic_analytics', 'advanced_analytics', 'enterprise_analytics', '24_7_support', 'all_content', 'custom_scheduling', 'white_label', 'api_access']
    }
    
    return planFeatures[userPlan?.id]?.includes(feature) || false
  }

  // Webhook helpers for frontend
  handleWebhookEvent(event) {
    switch (event.type) {
      case 'subscription.updated':
        this.clearCache()
        // Emit custom event for components to listen to
        window.dispatchEvent(new CustomEvent('subscription-updated', { 
          detail: event.data 
        }))
        break
      
      case 'payment.succeeded':
        this.clearCache()
        window.dispatchEvent(new CustomEvent('payment-succeeded', { 
          detail: event.data 
        }))
        break
      
      case 'payment.failed':
        window.dispatchEvent(new CustomEvent('payment-failed', { 
          detail: event.data 
        }))
        break
      
      case 'invoice.created':
        window.dispatchEvent(new CustomEvent('invoice-created', { 
          detail: event.data 
        }))
        break
      
      default:
        console.log('Unhandled webhook event:', event.type)
    }
  }

  // Event listeners for real-time updates
  addEventListener(eventType, callback) {
    window.addEventListener(eventType, callback)
    return () => window.removeEventListener(eventType, callback)
  }
}

// Create and export singleton instance
const billingService = new BillingService()

export default billingService

// Export specific methods for convenience
export const {
  getSubscription,
  getPlans,
  subscribe,
  updateSubscription,
  cancelSubscription,
  getUsage,
  getInvoices,
  getPaymentMethods,
  addPaymentMethod,
  calculatePlanCost,
  formatCurrency,
  getUsagePercentage,
  isUsageLimitReached
} = billingService