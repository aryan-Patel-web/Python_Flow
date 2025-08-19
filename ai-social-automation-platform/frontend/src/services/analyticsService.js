import apiService from './apiService';

class AnalyticsService {
  /**
   * Get analytics overview data
   */
  async getOverview(timeframe = '7d', platform = 'all') {
    try {
      const params = new URLSearchParams({
        timeframe,
        platform
      });
      
      const response = await apiService.get(`/analytics/overview?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching analytics overview:', error);
      throw error;
    }
  }

  /**
   * Get engagement analytics
   */
  async getEngagementData(timeframe = '7d', platform = 'all', metrics = 'all') {
    try {
      const params = new URLSearchParams({
        timeframe,
        platform,
        metrics
      });
      
      const response = await apiService.get(`/analytics/engagement?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching engagement data:', error);
      throw error;
    }
  }

  /**
   * Get growth metrics
   */
  async getGrowthMetrics(timeframe = '30d', platform = 'all') {
    try {
      const params = new URLSearchParams({
        timeframe,
        platform
      });
      
      const response = await apiService.get(`/analytics/growth?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching growth metrics:', error);
      throw error;
    }
  }

  /**
   * Get platform breakdown
   */
  async getPlatformBreakdown(timeframe = '7d') {
    try {
      const params = new URLSearchParams({ timeframe });
      const response = await apiService.get(`/analytics/platforms?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching platform breakdown:', error);
      throw error;
    }
  }

  /**
   * Get top performing posts
   */
  async getTopPosts(timeframe = '7d', platform = 'all', limit = 10) {
    try {
      const params = new URLSearchParams({
        timeframe,
        platform,
        limit: limit.toString()
      });
      
      const response = await apiService.get(`/analytics/top-posts?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching top posts:', error);
      throw error;
    }
  }

  /**
   * Get audience insights
   */
  async getAudienceInsights(platform = 'all') {
    try {
      const params = new URLSearchParams({ platform });
      const response = await apiService.get(`/analytics/audience?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching audience insights:', error);
      throw error;
    }
  }

  /**
   * Get content performance analytics
   */
  async getContentPerformance(timeframe = '30d', contentType = 'all') {
    try {
      const params = new URLSearchParams({
        timeframe,
        content_type: contentType
      });
      
      const response = await apiService.get(`/analytics/content?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching content performance:', error);
      throw error;
    }
  }

  /**
   * Get posting schedule analytics
   */
  async getPostingScheduleAnalytics(timeframe = '30d') {
    try {
      const params = new URLSearchParams({ timeframe });
      const response = await apiService.get(`/analytics/schedule?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching schedule analytics:', error);
      throw error;
    }
  }

  /**
   * Get hashtag performance
   */
  async getHashtagPerformance(timeframe = '30d', limit = 20) {
    try {
      const params = new URLSearchParams({
        timeframe,
        limit: limit.toString()
      });
      
      const response = await apiService.get(`/analytics/hashtags?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching hashtag performance:', error);
      throw error;
    }
  }

  /**
   * Get competitor analysis
   */
  async getCompetitorAnalysis(competitors = [], timeframe = '30d') {
    try {
      const response = await apiService.post('/analytics/competitors', {
        competitors,
        timeframe
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching competitor analysis:', error);
      throw error;
    }
  }

  /**
   * Get AI insights and recommendations
   */
  async getAIInsights(timeframe = '30d') {
    try {
      const params = new URLSearchParams({ timeframe });
      const response = await apiService.get(`/analytics/insights?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching AI insights:', error);
      throw error;
    }
  }

  /**
   * Export analytics data
   */
  async exportData(type = 'overview', timeframe = '30d', format = 'csv') {
    try {
      const params = new URLSearchParams({
        type,
        timeframe,
        format
      });
      
      const response = await fetch(`${apiService.baseURL}/analytics/export?${params}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Export failed');
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-${type}-${timeframe}.${format}`;
      a.click();
      window.URL.revokeObjectURL(url);
      
      return { success: true };
    } catch (error) {
      console.error('Error exporting analytics data:', error);
      throw error;
    }
  }

  /**
   * Get real-time metrics
   */
  async getRealTimeMetrics() {
    try {
      const response = await apiService.get('/analytics/realtime');
      return response.data;
    } catch (error) {
      console.error('Error fetching real-time metrics:', error);
      throw error;
    }
  }

  /**
   * Track custom event
   */
  async trackEvent(eventName, properties = {}) {
    try {
      const response = await apiService.post('/analytics/events', {
        event_name: eventName,
        properties,
        timestamp: new Date().toISOString()
      });
      return response.data;
    } catch (error) {
      console.error('Error tracking event:', error);
      throw error;
    }
  }

  /**
   * Get funnel analysis
   */
  async getFunnelAnalysis(funnelSteps, timeframe = '30d') {
    try {
      const response = await apiService.post('/analytics/funnel', {
        steps: funnelSteps,
        timeframe
      });
      return response.data;
    } catch (error) {
      console.error('Error fetching funnel analysis:', error);
      throw error;
    }
  }

  /**
   * Get cohort analysis
   */
  async getCohortAnalysis(cohortType = 'monthly', timeframe = '6m') {
    try {
      const params = new URLSearchParams({
        cohort_type: cohortType,
        timeframe
      });
      
      const response = await apiService.get(`/analytics/cohort?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching cohort analysis:', error);
      throw error;
    }
  }

  /**
   * Get conversion tracking
   */
  async getConversionTracking(timeframe = '30d') {
    try {
      const params = new URLSearchParams({ timeframe });
      const response = await apiService.get(`/analytics/conversions?${params}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching conversion tracking:', error);
      throw error;
    }
  }

  /**
   * Utility methods for data formatting
   */
  formatMetric(value, type = 'number') {
    if (value === null || value === undefined) return 'N/A';
    
    switch (type) {
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'currency':
        return new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: 'USD'
        }).format(value);
      case 'compact':
        if (value >= 1000000) {
          return `${(value / 1000000).toFixed(1)}M`;
        } else if (value >= 1000) {
          return `${(value / 1000).toFixed(1)}K`;
        }
        return value.toString();
      case 'duration':
        const hours = Math.floor(value / 3600);
        const minutes = Math.floor((value % 3600) / 60);
        return `${hours}h ${minutes}m`;
      default:
        return new Intl.NumberFormat('en-US').format(value);
    }
  }

  /**
   * Calculate engagement rate
   */
  calculateEngagementRate(likes, comments, shares, followers) {
    if (!followers || followers === 0) return 0;
    const totalEngagement = (likes || 0) + (comments || 0) + (shares || 0);
    return (totalEngagement / followers) * 100;
  }

  /**
   * Calculate growth rate
   */
  calculateGrowthRate(current, previous) {
    if (!previous || previous === 0) {
      return current > 0 ? 100 : 0;
    }
    return ((current - previous) / previous) * 100;
  }

  /**
   * Get optimal posting times based on engagement data
   */
  getOptimalPostingTimes(engagementData) {
    if (!engagementData || !Array.isArray(engagementData)) {
      return [];
    }

    return engagementData
      .map(item => ({
        hour: item.hour,
        day: item.day,
        engagement: item.total_engagement,
        posts: item.post_count
      }))
      .sort((a, b) => b.engagement - a.engagement)
      .slice(0, 5);
  }

  /**
   * Generate analytics report
   */
  async generateReport(reportType = 'comprehensive', timeframe = '30d', options = {}) {
    try {
      const response = await apiService.post('/analytics/reports', {
        report_type: reportType,
        timeframe,
        options
      });
      return response.data;
    } catch (error) {
      console.error('Error generating report:', error);
      throw error;
    }
  }
}

// Create singleton instance
const analyticsService = new AnalyticsService();

export default analyticsService;