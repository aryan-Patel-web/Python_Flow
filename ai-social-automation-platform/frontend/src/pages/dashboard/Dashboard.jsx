import React, { useState, useEffect } from 'react';
import { 
  Calendar, Clock, Zap, Bell, Search, Settings, LogOut, ChevronLeft, Plus, 
  BarChart3, Target, Sparkles, Globe, MessageCircle, TrendingUp, Users, Eye, Heart, 
  Share2, ArrowUp, ArrowDown, Play, Pause, Square as Stop, Bot, Brain, Lightbulb, Rocket,
  Instagram, Facebook, Twitter, Linkedin, Youtube, Check, X, Shield, AlertCircle,
  Filter, Download, RefreshCw, Edit3, Send, Image, Video, Hash, AtSign, Activity, ArrowRight
} from 'lucide-react';

const Dashboard = () => {
  // Auto-posting state
  const [automationStatus, setAutomationStatus] = useState('running');
  const [isLoading, setIsLoading] = useState(false);
  
  // Platform connections state
  const [connectedPlatforms, setConnectedPlatforms] = useState({
    instagram: { 
      connected: true, 
      username: '@techstartup', 
      followers: 12500, 
      posts: 45,
      engagement: 8.7,
      nextPost: '2:30 PM'
    },
    twitter: { 
      connected: true, 
      username: '@techstartup', 
      followers: 8300, 
      posts: 67,
      engagement: 12.3,
      nextPost: '3:15 PM'
    },
    linkedin: { 
      connected: true, 
      username: 'Tech Startup Inc', 
      followers: 2100, 
      posts: 23,
      engagement: 15.8,
      nextPost: '4:45 PM'
    },
    facebook: { 
      connected: false, 
      username: null, 
      followers: 0, 
      posts: 0,
      engagement: 0,
      nextPost: null
    },
    youtube: { 
      connected: false, 
      username: null, 
      followers: 0, 
      posts: 0,
      engagement: 0,
      nextPost: null
    }
  });

  // Recent activity data
  const [recentPosts, setRecentPosts] = useState([
    {
      id: 1,
      platform: 'instagram',
      content: '🚀 Just shipped our new API endpoint! Developers are going to love the seamless integration possibilities...',
      timestamp: '2 hours ago',
      engagement: { likes: 127, comments: 23, shares: 12 },
      aiGenerated: true,
      performanceScore: 89
    },
    {
      id: 2,
      platform: 'twitter',
      content: '💡 Pro tip: The best time to post on LinkedIn is Tuesday-Thursday between 8-10 AM. Our AI analyzed 50K+ posts to find this pattern.',
      timestamp: '4 hours ago',
      engagement: { likes: 89, comments: 15, shares: 34 },
      aiGenerated: true,
      performanceScore: 92
    },
    {
      id: 3,
      platform: 'linkedin',
      content: '📊 Monthly report: Our AI-powered content strategy increased engagement by 187% this month. Here\'s what worked...',
      timestamp: '6 hours ago',
      engagement: { likes: 245, comments: 67, shares: 89 },
      aiGenerated: true,
      performanceScore: 95
    }
  ]);

  // Platform icons mapping
  const platformIcons = {
    instagram: Instagram,
    twitter: Twitter,
    linkedin: Linkedin,
    facebook: Facebook,
    youtube: Youtube
  };

  const platformColors = {
    instagram: 'from-purple-500 to-pink-500',
    twitter: 'from-blue-400 to-blue-600',
    linkedin: 'from-blue-600 to-blue-800',
    facebook: 'from-blue-600 to-blue-700',
    youtube: 'from-red-500 to-red-600'
  };

  // Auto-posting controls
  const handleStartAutomation = async () => {
    setIsLoading(true);
    setAutomationStatus('running');
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  const handlePauseAutomation = async () => {
    setIsLoading(true);
    setAutomationStatus('paused');
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  const handleStopAutomation = async () => {
    setIsLoading(true);
    setAutomationStatus('stopped');
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsLoading(false);
  };

  // Calculate metrics
  const totalPosts = Object.values(connectedPlatforms).reduce((sum, platform) => sum + platform.posts, 0);
  const totalFollowers = Object.values(connectedPlatforms).reduce((sum, platform) => sum + platform.followers, 0);
  const avgEngagement = Object.values(connectedPlatforms)
    .filter(p => p.connected)
    .reduce((sum, platform) => sum + platform.engagement, 0) / 
    Object.values(connectedPlatforms).filter(p => p.connected).length;

  const connectedCount = Object.values(connectedPlatforms).filter(p => p.connected).length;

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Welcome back! Here's your AI-powered social media performance.</p>
        </div>
        
        {/* Automation Status */}
        <div className="flex items-center space-x-4">
          <div className={`flex items-center space-x-2 px-4 py-2 rounded-full text-sm font-medium ${
            automationStatus === 'running' 
              ? 'bg-green-100 text-green-800' 
              : automationStatus === 'paused'
              ? 'bg-yellow-100 text-yellow-800'
              : 'bg-red-100 text-red-800'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              automationStatus === 'running' ? 'bg-green-500 animate-pulse' :
              automationStatus === 'paused' ? 'bg-yellow-500' : 'bg-red-500'
            }`}></div>
            <span>AI Automation: {automationStatus.charAt(0).toUpperCase() + automationStatus.slice(1)}</span>
          </div>
          
          <div className="flex items-center space-x-2">
            <button
              onClick={handleStartAutomation}
              disabled={isLoading || automationStatus === 'running'}
              className="p-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Start AI Automation"
            >
              <Play className="w-4 h-4" />
            </button>
            <button
              onClick={handlePauseAutomation}
              disabled={isLoading || automationStatus === 'stopped'}
              className="p-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Pause AI Automation"
            >
              <Pause className="w-4 h-4" />
            </button>
            <button
              onClick={handleStopAutomation}
              disabled={isLoading || automationStatus === 'stopped'}
              className="p-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="Stop AI Automation"
            >
              <Stop className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* AI Automation Status Card */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-white/20 rounded-xl">
              <Bot className="w-6 h-6" />
            </div>
            <span className="text-xs bg-white/20 px-2 py-1 rounded-full font-medium">
              AI Powered
            </span>
          </div>
          <div className="text-3xl font-bold mb-1">{totalPosts}</div>
          <div className="text-blue-100 text-sm">AI Posts Generated</div>
          <div className="text-xs text-blue-200 mt-2">+23% this week</div>
        </div>

        {/* Connected Platforms */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-green-100 rounded-xl">
              <Globe className="w-6 h-6 text-green-600" />
            </div>
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full font-medium">
              Connected
            </span>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">{connectedCount}/5</div>
          <div className="text-gray-600 text-sm">Platforms Active</div>
          <div className="text-xs text-green-600 mt-2">OAuth Secured</div>
        </div>

        {/* Total Followers */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-purple-100 rounded-xl">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
            <span className="text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full font-medium">
              Growing
            </span>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {(totalFollowers / 1000).toFixed(1)}K
          </div>
          <div className="text-gray-600 text-sm">Total Followers</div>
          <div className="text-xs text-purple-600 mt-2 flex items-center">
            <ArrowUp className="w-3 h-3 mr-1" />
            +12.3% growth
          </div>
        </div>

        {/* Engagement Rate */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="p-3 bg-orange-100 rounded-xl">
              <TrendingUp className="w-6 h-6 text-orange-600" />
            </div>
            <span className="text-xs bg-orange-100 text-orange-700 px-2 py-1 rounded-full font-medium">
              AI Optimized
            </span>
          </div>
          <div className="text-3xl font-bold text-gray-900 mb-1">
            {avgEngagement.toFixed(1)}%
          </div>
          <div className="text-gray-600 text-sm">Avg Engagement</div>
          <div className="text-xs text-orange-600 mt-2 flex items-center">
            <ArrowUp className="w-3 h-3 mr-1" />
            AI boosted +127%
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Platform Status */}
        <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-semibold text-gray-900">Platform Overview</h2>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium inline-flex items-center">
              Manage Platforms
              <ArrowRight className="w-4 h-4 ml-1" />
            </button>
          </div>

          <div className="space-y-4">
            {Object.entries(connectedPlatforms).map(([platform, data]) => {
              const IconComponent = platformIcons[platform];
              const gradient = platformColors[platform];
              
              return (
                <div key={platform} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 bg-gradient-to-r ${gradient} rounded-xl flex items-center justify-center`}>
                      <IconComponent className="w-6 h-6 text-white" />
                    </div>
                    
                    <div>
                      <div className="flex items-center space-x-2">
                        <h3 className="font-semibold text-gray-900 capitalize">{platform}</h3>
                        {data.connected ? (
                          <Check className="w-4 h-4 text-green-500" />
                        ) : (
                          <X className="w-4 h-4 text-red-500" />
                        )}
                      </div>
                      <p className="text-sm text-gray-600">
                        {data.connected ? data.username : 'Not connected'}
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    {data.connected ? (
                      <div className="space-y-1">
                        <div className="text-sm font-semibold text-gray-900">
                          {data.followers.toLocaleString()} followers
                        </div>
                        <div className="text-xs text-gray-500">
                          {data.posts} posts • {data.engagement}% engagement
                        </div>
                        <div className="text-xs text-blue-600 font-medium">
                          Next AI post: {data.nextPost}
                        </div>
                      </div>
                    ) : (
                      <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                        Connect Now
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>

          {/* Quick Actions */}
          <div className="mt-6 flex flex-wrap gap-3">
            <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
              <Plus className="w-4 h-4" />
              <span>Connect Platform</span>
            </button>
            <button className="flex items-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors">
              <Brain className="w-4 h-4" />
              <span>Generate Content</span>
            </button>
            <button className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors">
              <Zap className="w-4 h-4" />
              <span>Boost Automation</span>
            </button>
          </div>
        </div>

        {/* AI Performance */}
        <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-6">AI Performance</h2>
          
          <div className="space-y-6">
            {/* AI Health Score */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">AI Health Score</span>
                <span className="text-2xl font-bold text-green-600">94/100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-green-500 h-2 rounded-full" style={{width: '94%'}}></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">Excellent performance across all metrics</p>
            </div>

            {/* Content Quality */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Content Quality</span>
                <span className="text-lg font-bold text-blue-600">87%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-blue-500 h-2 rounded-full" style={{width: '87%'}}></div>
              </div>
            </div>

            {/* Engagement Prediction */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Engagement Prediction</span>
                <span className="text-lg font-bold text-purple-600">91%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div className="bg-purple-500 h-2 rounded-full" style={{width: '91%'}}></div>
              </div>
            </div>

            {/* AI Insights */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4">
              <div className="flex items-center space-x-2 mb-2">
                <Lightbulb className="w-5 h-5 text-blue-600" />
                <span className="font-semibold text-blue-900">AI Insight</span>
              </div>
              <p className="text-sm text-blue-800">
                Your Tuesday posts perform 34% better. AI will automatically schedule more content on Tuesdays.
              </p>
            </div>

            {/* AI Stats */}
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">127%</div>
                <div className="text-xs text-gray-600">Performance Boost</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">43hrs</div>
                <div className="text-xs text-gray-600">Time Saved</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Recent AI Posts</h2>
          <div className="flex items-center space-x-3">
            <button className="text-gray-500 hover:text-gray-700">
              <Filter className="w-4 h-4" />
            </button>
            <button className="text-gray-500 hover:text-gray-700">
              <Download className="w-4 h-4" />
            </button>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              View All
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {recentPosts.map((post) => {
            const IconComponent = platformIcons[post.platform];
            const gradient = platformColors[post.platform];
            
            return (
              <div key={post.id} className="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-all">
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-3 flex-1">
                    <div className={`w-10 h-10 bg-gradient-to-r ${gradient} rounded-lg flex items-center justify-center flex-shrink-0`}>
                      <IconComponent className="w-5 h-5 text-white" />
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="font-medium text-gray-900 capitalize">{post.platform}</span>
                        <span className="text-sm text-gray-500">• {post.timestamp}</span>
                        {post.aiGenerated && (
                          <span className="inline-flex items-center space-x-1 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                            <Sparkles className="w-3 h-3" />
                            <span>AI Generated</span>
                          </span>
                        )}
                        <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                          Score: {post.performanceScore}
                        </span>
                      </div>
                      
                      <p className="text-gray-800 mb-3 line-clamp-2">{post.content}</p>
                      
                      <div className="flex items-center space-x-4 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <Heart className="w-4 h-4" />
                          <span>{post.engagement.likes}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MessageCircle className="w-4 h-4" />
                          <span>{post.engagement.comments}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Share2 className="w-4 h-4" />
                          <span>{post.engagement.shares}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2 ml-4">
                    <button className="text-gray-400 hover:text-gray-600">
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button className="text-gray-400 hover:text-red-500">
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Bottom Action Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* AI Content Generator */}
        <div className="bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <Brain className="w-8 h-8" />
            <ArrowRight className="w-5 h-5" />
          </div>
          <h3 className="text-xl font-bold mb-2">AI Content Lab</h3>
          <p className="text-purple-100 mb-4 text-sm">
            Generate unlimited content ideas with our advanced AI engine
          </p>
          <button className="bg-white text-purple-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
            Generate Now
          </button>
        </div>

        {/* Auto-Posting Center */}
        <div className="bg-gradient-to-r from-blue-500 to-cyan-500 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <Zap className="w-8 h-8" />
            <ArrowRight className="w-5 h-5" />
          </div>
          <h3 className="text-xl font-bold mb-2">Auto-Posting Hub</h3>
          <p className="text-blue-100 mb-4 text-sm">
            Manage your complete automation settings and scheduling
          </p>
          <button className="bg-white text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
            Open Center
          </button>
        </div>

        {/* Analytics Center */}
        <div className="bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl p-6 text-white">
          <div className="flex items-center justify-between mb-4">
            <BarChart3 className="w-8 h-8" />
            <ArrowRight className="w-5 h-5" />
          </div>
          <h3 className="text-xl font-bold mb-2">Performance Analytics</h3>
          <p className="text-green-100 mb-4 text-sm">
            Deep insights and AI recommendations for growth
          </p>
          <button className="bg-white text-green-600 px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors">
            View Analytics
          </button>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
