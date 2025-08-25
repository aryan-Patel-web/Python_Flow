import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import { 
  Play, Pause, Square, Bot, Calendar, BarChart3, Settings,
  Zap, Clock, Target, TrendingUp, Users, Heart, MessageCircle,
  RefreshCw, AlertCircle
} from 'lucide-react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { autoPostingService } from '../../services/autoPostingService';

const AutoPostingCenter = () => {
  const [automationStatus, setAutomationStatus] = useState('stopped');
  const [stats, setStats] = useState({
    postsToday: 0,
    totalPosts: 0,
    avgEngagement: 0,
    activeConnections: 0,
    nextPostIn: null
  });
  const [recentPosts, setRecentPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(null);

  useEffect(() => {
    fetchAutomationData();
    
    // Refresh data every 30 seconds
    const interval = setInterval(fetchAutomationData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchAutomationData = async () => {
    try {
      const [statusData, statsData, postsData] = await Promise.all([
        autoPostingService.getStatus(),
        autoPostingService.getStats(),
        autoPostingService.getRecentPosts(10)
      ]);
      
      setAutomationStatus(statusData.status);
      setStats(statsData);
      setRecentPosts(postsData);
    } catch (error) {
      console.error('Failed to fetch automation data:', error);
      toast.error('Failed to load automation data');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAutomation = async () => {
    try {
      setActionLoading('start');
      await autoPostingService.startAutomation();
      setAutomationStatus('running');
      toast.success('🚀 Auto-posting started! AI is now generating and posting content.');
    } catch (error) {
      console.error('Failed to start automation:', error);
      toast.error('Failed to start automation: ' + error.message);
    } finally {
      setActionLoading(null);
    }
  };

  const handlePauseAutomation = async () => {
    try {
      setActionLoading('pause');
      await autoPostingService.pauseAutomation();
      setAutomationStatus('paused');
      toast.success('⏸️ Auto-posting paused. You can resume anytime.');
    } catch (error) {
      console.error('Failed to pause automation:', error);
      toast.error('Failed to pause automation');
    } finally {
      setActionLoading(null);
    }
  };

  const handleStopAutomation = async () => {
    if (!window.confirm('Stop auto-posting completely? This will cancel all scheduled posts.')) {
      return;
    }

    try {
      setActionLoading('stop');
      await autoPostingService.stopAutomation();
      setAutomationStatus('stopped');
      toast.success('🛑 Auto-posting stopped completely.');
    } catch (error) {
      console.error('Failed to stop automation:', error);
      toast.error('Failed to stop automation');
    } finally {
      setActionLoading(null);
    }
  };

  const getStatusColor = () => {
    switch (automationStatus) {
      case 'running':
        return 'text-green-600 bg-green-100';
      case 'paused':
        return 'text-yellow-600 bg-yellow-100';
      case 'stopped':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusText = () => {
    switch (automationStatus) {
      case 'running':
        return 'Active - AI is working';
      case 'paused':
        return 'Paused - Ready to resume';
      case 'stopped':
        return 'Stopped - Click start to begin';
      default:
        return 'Unknown status';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" text="Loading automation center..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <Bot className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Auto-Posting Center</h1>
              <p className="text-gray-600">AI-powered social media automation</p>
            </div>
          </div>
          
          <div className={`px-4 py-2 rounded-lg font-medium ${getStatusColor()}`}>
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                automationStatus === 'running' ? 'bg-green-600' :
                automationStatus === 'paused' ? 'bg-yellow-600' : 'bg-red-600'
              }`}></div>
              <span>{getStatusText()}</span>
            </div>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center space-x-4">
          <button
            onClick={handleStartAutomation}
            disabled={automationStatus === 'running' || actionLoading}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
              automationStatus === 'running' || actionLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-700 text-white'
            }`}
          >
            {actionLoading === 'start' ? (
              <LoadingSpinner size="sm" color="white" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            <span>Start Auto-Posting</span>
          </button>

          <button
            onClick={handlePauseAutomation}
            disabled={automationStatus !== 'running' || actionLoading}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
              automationStatus !== 'running' || actionLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-yellow-600 hover:bg-yellow-700 text-white'
            }`}
          >
            {actionLoading === 'pause' ? (
              <LoadingSpinner size="sm" color="white" />
            ) : (
              <Pause className="w-4 h-4" />
            )}
            <span>Pause</span>
          </button>

          <button
            onClick={handleStopAutomation}
            disabled={automationStatus === 'stopped' || actionLoading}
            className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors ${
              automationStatus === 'stopped' || actionLoading
                ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                : 'bg-red-600 hover:bg-red-700 text-white'
            }`}
          >
            {actionLoading === 'stop' ? (
              <LoadingSpinner size="sm" color="white" />
            ) : (
              <Square className="w-4 h-4" />
            )}
            <span>Stop</span>
          </button>

          <Link
            to="/posting-scheduler"
            className="flex items-center space-x-2 px-6 py-3 border border-gray-300 rounded-lg font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </Link>
        </div>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Posts Today</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.postsToday}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <TrendingUp className="w-4 h-4 text-green-500" />
            <span className="text-sm text-green-600 ml-1">+12% from yesterday</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Posts</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.totalPosts}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <Bot className="w-4 h-4 text-purple-500" />
            <span className="text-sm text-purple-600 ml-1">AI generated</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Engagement</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.avgEngagement}%</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Heart className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <TrendingUp className="w-4 h-4 text-green-500" />
            <span className="text-sm text-green-600 ml-1">Above average</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Next Post In</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">
                {stats.nextPostIn || '-- : --'}
              </p>
            </div>
            <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <Target className="w-4 h-4 text-yellow-500" />
            <span className="text-sm text-yellow-600 ml-1">Scheduled</span>
          </div>
        </div>
      </div>

      {/* Recent Posts */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Recent AI Posts</h2>
          <button
            onClick={fetchAutomationData}
            className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
          >
            <RefreshCw className="w-4 h-4" />
            <span className="text-sm">Refresh</span>
          </button>
        </div>

        {recentPosts.length === 0 ? (
          <div className="text-center py-12">
            <Bot className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No posts yet</h3>
            <p className="text-gray-600 mb-6">Start auto-posting to see AI-generated content here</p>
            <button
              onClick={handleStartAutomation}
              className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2 rounded-lg"
            >
              Start Auto-Posting
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {recentPosts.map((post) => (
              <div key={post.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center space-x-3">
                    <div className="flex space-x-1">
                      {post.platforms.map((platform) => (
                        <div
                          key={platform}
                          className={`w-6 h-6 rounded-full flex items-center justify-center text-xs text-white ${
                            platform === 'instagram' ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                            platform === 'facebook' ? 'bg-blue-600' :
                            platform === 'twitter' ? 'bg-black' :
                            platform === 'linkedin' ? 'bg-blue-700' :
                            'bg-gray-500'
                          }`}
                        >
                          {platform.charAt(0).toUpperCase()}
                        </div>
                      ))}
                    </div>
                    <div className="flex items-center space-x-2">
                      <Bot className="w-4 h-4 text-purple-600" />
                      <span className="text-sm text-purple-600 font-medium">AI Generated</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">{post.publishedAt || post.scheduledFor}</p>
                    <p className={`text-xs ${
                      post.status === 'published' ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {post.status}
                    </p>
                  </div>
                </div>
                
                <p className="text-gray-900 mb-3">{post.content}</p>
                
                {post.status === 'published' && post.engagement && (
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <div className="flex items-center space-x-1">
                      <Heart className="w-4 h-4" />
                      <span>{post.engagement.likes}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <MessageCircle className="w-4 h-4" />
                      <span>{post.engagement.comments}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4" />
                      <span>{post.engagement.reach} reach</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Link
          to="/content-generator"
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Generate Content</h3>
              <p className="text-sm text-gray-600">Create AI posts manually</p>
            </div>
          </div>
        </Link>

        <Link
          to="/posting-scheduler"
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">Schedule Settings</h3>
              <p className="text-sm text-gray-600">Configure posting times</p>
            </div>
          </div>
        </Link>

        <Link
          to="/analytics"
          className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
        >
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-6 h-6 text-green-600" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">View Analytics</h3>
              <p className="text-sm text-gray-600">Track performance</p>
            </div>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default AutoPostingCenter;