import React, { useState, useEffect } from 'react';
import EngagementChart from '../../components/analytics/EngagementChart';
import { 
  TrendingUp, 
  Users, 
  Calendar, 
  Eye, 
  Heart, 
  MessageCircle, 
  Share2,
  Download,
  Filter,
  RefreshCw
} from 'lucide-react';

const AnalyticsPage = () => {
  const [timeframe, setTimeframe] = useState('7d');
  const [selectedPlatform, setSelectedPlatform] = useState('all');
  const [loading, setLoading] = useState(false);
  const [analyticsData, setAnalyticsData] = useState({
    overview: {},
    topPosts: [],
    platformBreakdown: [],
    growthMetrics: {}
  });

  useEffect(() => {
    fetchAnalyticsData();
  }, [timeframe, selectedPlatform]);

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      const params = new URLSearchParams({
        timeframe,
        platform: selectedPlatform
      });
      
      const response = await fetch(`/api/analytics/overview?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      }
    } catch (error) {
      console.error('Error fetching analytics:', error);
      // Set demo data
      setAnalyticsData({
        overview: {
          totalPosts: 45,
          totalViews: 12500,
          totalEngagement: 3200,
          engagementRate: 2.56,
          followerGrowth: 156,
          reachGrowth: 23.5
        },
        topPosts: [
          {
            id: 1,
            platform: 'instagram',
            text: 'Check out our latest AI automation features! 🤖',
            engagement: 450,
            likes: 320,
            comments: 85,
            shares: 45,
            date: '2024-01-15'
          },
          {
            id: 2,
            platform: 'linkedin',
            text: 'How AI is transforming social media marketing...',
            engagement: 320,
            likes: 200,
            comments: 95,
            shares: 25,
            date: '2024-01-14'
          }
        ],
        platformBreakdown: [
          { platform: 'Instagram', posts: 18, engagement: 1250, color: '#E1306C' },
          { platform: 'Facebook', posts: 12, engagement: 890, color: '#1877F2' },
          { platform: 'LinkedIn', posts: 8, engagement: 650, color: '#0A66C2' },
          { platform: 'Twitter', posts: 7, engagement: 410, color: '#1DA1F2' }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  const platforms = [
    { value: 'all', label: 'All Platforms' },
    { value: 'instagram', label: 'Instagram' },
    { value: 'facebook', label: 'Facebook' },
    { value: 'linkedin', label: 'LinkedIn' },
    { value: 'twitter', label: 'Twitter' },
    { value: 'youtube', label: 'YouTube' }
  ];

  const timeframes = [
    { value: '24h', label: 'Last 24 Hours' },
    { value: '7d', label: 'Last 7 Days' },
    { value: '30d', label: 'Last 30 Days' },
    { value: '90d', label: 'Last 90 Days' }
  ];

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const getPlatformIcon = (platform) => {
    const icons = {
      instagram: '📷',
      facebook: '👥',
      linkedin: '💼',
      twitter: '🐦',
      youtube: '📹'
    };
    return icons[platform] || '📱';
  };

  const getPlatformColor = (platform) => {
    const colors = {
      instagram: 'bg-pink-100 text-pink-800',
      facebook: 'bg-blue-100 text-blue-800',
      linkedin: 'bg-indigo-100 text-indigo-800',
      twitter: 'bg-sky-100 text-sky-800',
      youtube: 'bg-red-100 text-red-800'
    };
    return colors[platform] || 'bg-gray-100 text-gray-800';
  };

  const exportAnalytics = () => {
    // Create CSV export
    const csvData = [
      ['Metric', 'Value'],
      ['Total Posts', analyticsData.overview?.totalPosts || 0],
      ['Total Views', analyticsData.overview?.totalViews || 0],
      ['Total Engagement', analyticsData.overview?.totalEngagement || 0],
      ['Engagement Rate', `${analyticsData.overview?.engagementRate || 0}%`],
      ['Follower Growth', analyticsData.overview?.followerGrowth || 0]
    ].map(row => row.join(',')).join('\n');
    
    const blob = new Blob([csvData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${timeframe}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
            <p className="text-gray-600 mt-1">Track your social media performance and engagement</p>
          </div>
          <div className="flex items-center space-x-4">
            <button
              onClick={exportAnalytics}
              className="flex items-center px-4 py-2 bg-white border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
            >
              <Download className="w-4 h-4 mr-2" />
              Export
            </button>
            <button
              onClick={fetchAnalyticsData}
              disabled={loading}
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
            >
              <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <Filter className="w-4 h-4 text-gray-500" />
              <span className="text-sm font-medium text-gray-700">Filters:</span>
            </div>
            
            <select
              value={timeframe}
              onChange={(e) => setTimeframe(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {timeframes.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>

            <select
              value={selectedPlatform}
              onChange={(e) => setSelectedPlatform(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {platforms.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Posts</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatNumber(analyticsData.overview?.totalPosts)}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600">+12%</span>
              <span className="text-gray-500 ml-1">vs last period</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Views</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatNumber(analyticsData.overview?.totalViews)}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Eye className="w-6 h-6 text-green-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600">+8.5%</span>
              <span className="text-gray-500 ml-1">vs last period</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Total Engagement</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {formatNumber(analyticsData.overview?.totalEngagement)}
                </p>
              </div>
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Heart className="w-6 h-6 text-purple-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600">+15.2%</span>
              <span className="text-gray-500 ml-1">vs last period</span>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Engagement Rate</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">
                  {analyticsData.overview?.engagementRate?.toFixed(1) || 0}%
                </p>
              </div>
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <TrendingUp className="w-6 h-6 text-orange-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center text-sm">
              <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              <span className="text-green-600">+2.1%</span>
              <span className="text-gray-500 ml-1">vs last period</span>
            </div>
          </div>
        </div>

        {/* Main Chart */}
        <EngagementChart timeframe={timeframe} platform={selectedPlatform} />

        {/* Platform Breakdown & Top Posts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Platform Breakdown */}
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Platform Breakdown</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {analyticsData.platformBreakdown?.map((platform, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-sm ${getPlatformColor(platform.platform.toLowerCase())}`}>
                        {getPlatformIcon(platform.platform.toLowerCase())}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{platform.platform}</p>
                        <p className="text-sm text-gray-500">{platform.posts} posts</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium text-gray-900">{formatNumber(platform.engagement)}</p>
                      <p className="text-sm text-gray-500">engagement</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Top Posts */}
          <div className="bg-white rounded-lg shadow-sm border">
            <div className="p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Top Performing Posts</h3>
            </div>
            <div className="p-6">
              <div className="space-y-4">
                {analyticsData.topPosts?.map((post, index) => (
                  <div key={post.id} className="border rounded-lg p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getPlatformColor(post.platform)}`}>
                          {post.platform}
                        </span>
                        <span className="text-xs text-gray-500">
                          {new Date(post.date).toLocaleDateString()}
                        </span>
                      </div>
                      <span className="text-sm font-medium text-gray-900">
                        {formatNumber(post.engagement)} eng.
                      </span>
                    </div>
                    <p className="text-sm text-gray-900 mb-3 line-clamp-2">{post.text}</p>
                    <div className="flex items-center space-x-4 text-xs text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Heart className="w-3 h-3" />
                        <span>{formatNumber(post.likes)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MessageCircle className="w-3 h-3" />
                        <span>{formatNumber(post.comments)}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Share2 className="w-3 h-3" />
                        <span>{formatNumber(post.shares)}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Growth Metrics */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-900">Growth Metrics</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 mb-1">
                  +{analyticsData.overview?.followerGrowth || 0}
                </div>
                <div className="text-sm text-gray-600">New Followers</div>
                <div className="text-xs text-gray-500 mt-1">This {timeframe}</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 mb-1">
                  +{analyticsData.overview?.reachGrowth?.toFixed(1) || 0}%
                </div>
                <div className="text-sm text-gray-600">Reach Growth</div>
                <div className="text-xs text-gray-500 mt-1">vs last period</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 mb-1">
                  {analyticsData.overview?.engagementRate?.toFixed(1) || 0}%
                </div>
                <div className="text-sm text-gray-600">Avg. Engagement Rate</div>
                <div className="text-xs text-gray-500 mt-1">Across all platforms</div>
              </div>
            </div>
          </div>
        </div>

        {/* Insights & Recommendations */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h3 className="text-lg font-semibold text-gray-900">AI Insights & Recommendations</h3>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <h4 className="font-medium text-blue-900 mb-2">🚀 Growth Opportunity</h4>
                <p className="text-sm text-blue-800">
                  Your Instagram engagement is 23% higher than average. Consider posting similar content on other platforms.
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <h4 className="font-medium text-green-900 mb-2">⏰ Optimal Timing</h4>
                <p className="text-sm text-green-800">
                  Posts between 7-9 PM show 34% higher engagement. Schedule more content during these hours.
                </p>
              </div>
              <div className="bg-purple-50 rounded-lg p-4">
                <h4 className="font-medium text-purple-900 mb-2">📝 Content Strategy</h4>
                <p className="text-sm text-purple-800">
                  Video content receives 2.3x more engagement than images. Consider increasing video posts.
                </p>
              </div>
              <div className="bg-orange-50 rounded-lg p-4">
                <h4 className="font-medium text-orange-900 mb-2">🎯 Audience Insight</h4>
                <p className="text-sm text-orange-800">
                  Your audience is most active on weekdays. Focus content distribution Tuesday-Thursday.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;