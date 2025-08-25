import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { 
  Clock, Calendar, Target, Zap, Save, RefreshCw, 
  TrendingUp, Users, BarChart3, Settings, AlertCircle
} from 'lucide-react';
import LoadingSpinner from '../../components/common/LoadingSpinner';
import { schedulerService } from '../../services/schedulerService';

const PostingScheduler = () => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState({
    postsPerDay: 3,
    activeHours: {
      start: '09:00',
      end: '18:00'
    },
    daysOfWeek: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
    timezones: 'America/New_York',
    platforms: {
      instagram: { enabled: true, postsPerDay: 2, optimalTimes: ['10:00', '15:00'] },
      facebook: { enabled: true, postsPerDay: 2, optimalTimes: ['12:00', '19:00'] },
      twitter: { enabled: true, postsPerDay: 4, optimalTimes: ['08:00', '12:00', '16:00', '20:00'] },
      linkedin: { enabled: true, postsPerDay: 1, optimalTimes: ['09:00'] },
      youtube: { enabled: false, postsPerDay: 0, optimalTimes: [] }
    },
    contentDistribution: {
      memes: 30,
      tech: 40,
      business: 20,
      lifestyle: 10
    },
    aiSettings: {
      creativity: 75,
      engagementFocus: true,
      trendFollowing: true,
      brandVoiceConsistency: 85
    }
  });

  const [analytics, setAnalytics] = useState({
    bestTimes: [],
    engagementByHour: {},
    platformPerformance: {}
  });

  useEffect(() => {
    fetchSchedulerSettings();
    fetchAnalytics();
  }, []);

  const fetchSchedulerSettings = async () => {
    try {
      const data = await schedulerService.getSettings();
      setSettings(data);
    } catch (error) {
      console.error('Failed to fetch scheduler settings:', error);
      toast.error('Failed to load scheduler settings');
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const data = await schedulerService.getAnalytics();
      setAnalytics(data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      await schedulerService.updateSettings(settings);
      toast.success('🎯 Schedule settings saved! Auto-posting will use new configuration.');
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast.error('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const handleOptimalTimesUpdate = async () => {
    try {
      setSaving(true);
      const optimalTimes = await schedulerService.generateOptimalTimes();
      
      setSettings(prev => ({
        ...prev,
        platforms: {
          ...prev.platforms,
          ...optimalTimes
        }
      }));
      
      toast.success('🤖 AI updated optimal posting times based on your audience data!');
    } catch (error) {
      console.error('Failed to update optimal times:', error);
      toast.error('Failed to generate optimal times');
    } finally {
      setSaving(false);
    }
  };

  const updatePlatformSetting = (platform, field, value) => {
    setSettings(prev => ({
      ...prev,
      platforms: {
        ...prev.platforms,
        [platform]: {
          ...prev.platforms[platform],
          [field]: value
        }
      }
    }));
  };

  const updateContentDistribution = (domain, value) => {
    const total = Object.values(settings.contentDistribution).reduce((sum, val) => val === settings.contentDistribution[domain] ? sum : sum + val, 0);
    const remaining = Math.max(0, 100 - total);
    
    setSettings(prev => ({
      ...prev,
      contentDistribution: {
        ...prev.contentDistribution,
        [domain]: Math.min(value, remaining + settings.contentDistribution[domain])
      }
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <LoadingSpinner size="lg" text="Loading scheduler settings..." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <Calendar className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Posting Scheduler</h1>
              <p className="text-gray-600">Configure when and how AI posts your content</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            <button
              onClick={handleOptimalTimesUpdate}
              disabled={saving}
              className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              <TrendingUp className="w-4 h-4" />
              <span>AI Optimize</span>
            </button>
            
            <button
              onClick={handleSave}
              disabled={saving}
              className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium transition-colors"
            >
              {saving ? (
                <LoadingSpinner size="sm" color="white" />
              ) : (
                <Save className="w-4 h-4" />
              )}
              <span>{saving ? 'Saving...' : 'Save Settings'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* General Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Posts Per Day */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Posts Per Day</label>
            <div className="flex items-center space-x-4">
              <input
                type="range"
                min="1"
                max="10"
                value={settings.postsPerDay}
                onChange={(e) => setSettings(prev => ({ ...prev, postsPerDay: parseInt(e.target.value) }))}
                className="flex-1"
              />
              <span className="text-lg font-semibold text-gray-900 w-8">{settings.postsPerDay}</span>
            </div>
            <p className="text-xs text-gray-500 mt-1">Recommended: 3-6 posts per day</p>
          </div>

          {/* Active Hours */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Active Hours</label>
            <div className="flex items-center space-x-2">
              <input
                type="time"
                value={settings.activeHours.start}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  activeHours: { ...prev.activeHours, start: e.target.value }
                }))}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <span className="text-gray-500">to</span>
              <input
                type="time"
                value={settings.activeHours.end}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  activeHours: { ...prev.activeHours, end: e.target.value }
                }))}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">AI will only post during these hours</p>
          </div>

          {/* Timezone */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
            <select
              value={settings.timezones}
              onChange={(e) => setSettings(prev => ({ ...prev, timezones: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="America/New_York">Eastern Time (ET)</option>
              <option value="America/Chicago">Central Time (CT)</option>
              <option value="America/Denver">Mountain Time (MT)</option>
              <option value="America/Los_Angeles">Pacific Time (PT)</option>
              <option value="Europe/London">London (GMT)</option>
              <option value="Europe/Paris">Paris (CET)</option>
              <option value="Asia/Tokyo">Tokyo (JST)</option>
              <option value="Australia/Sydney">Sydney (AEDT)</option>
            </select>
          </div>
        </div>

        {/* Days of Week */}
        <div className="mt-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">Active Days</label>
          <div className="flex flex-wrap gap-2">
            {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map((day) => (
              <button
                key={day}
                onClick={() => {
                  const isActive = settings.daysOfWeek.includes(day);
                  setSettings(prev => ({
                    ...prev,
                    daysOfWeek: isActive 
                      ? prev.daysOfWeek.filter(d => d !== day)
                      : [...prev.daysOfWeek, day]
                  }));
                }}
                className={`px-4 py-2 rounded-lg font-medium capitalize transition-colors ${
                  settings.daysOfWeek.includes(day)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {day.slice(0, 3)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Platform-Specific Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Platform Settings</h2>
        
        <div className="space-y-6">
          {Object.entries(settings.platforms).map(([platform, config]) => (
            <div key={platform} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-bold ${
                    platform === 'instagram' ? 'bg-gradient-to-r from-purple-500 to-pink-500' :
                    platform === 'facebook' ? 'bg-blue-600' :
                    platform === 'twitter' ? 'bg-black' :
                    platform === 'linkedin' ? 'bg-blue-700' :
                    platform === 'youtube' ? 'bg-red-600' :
                    'bg-gray-500'
                  }`}>
                    {platform.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900 capitalize">{platform}</h3>
                    <p className="text-sm text-gray-600">
                      {config.enabled ? `${config.postsPerDay} posts/day` : 'Disabled'}
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      checked={config.enabled}
                      onChange={(e) => updatePlatformSetting(platform, 'enabled', e.target.checked)}
                      className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700">Enable</span>
                  </label>
                </div>
              </div>

              {config.enabled && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Posts Per Day</label>
                      <input
                        type="number"
                        min="0"
                        max="10"
                        value={config.postsPerDay}
                        onChange={(e) => updatePlatformSetting(platform, 'postsPerDay', parseInt(e.target.value))}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Optimal Times
                        <button
                          onClick={() => handleOptimalTimesUpdate()}
                          className="ml-2 text-xs text-blue-600 hover:text-blue-700"
                        >
                          🤖 AI Optimize
                        </button>
                      </label>
                      <div className="flex flex-wrap gap-2">
                        {config.optimalTimes.map((time, index) => (
                          <div key={index} className="flex items-center space-x-1">
                            <input
                              type="time"
                              value={time}
                              onChange={(e) => {
                                const newTimes = [...config.optimalTimes];
                                newTimes[index] = e.target.value;
                                updatePlatformSetting(platform, 'optimalTimes', newTimes);
                              }}
                              className="px-2 py-1 border border-gray-300 rounded text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                            />
                            <button
                              onClick={() => {
                                const newTimes = config.optimalTimes.filter((_, i) => i !== index);
                                updatePlatformSetting(platform, 'optimalTimes', newTimes);
                              }}
                              className="text-red-500 hover:text-red-700 text-sm"
                            >
                              ×
                            </button>
                          </div>
                        ))}
                        <button
                          onClick={() => {
                            const newTimes = [...config.optimalTimes, '12:00'];
                            updatePlatformSetting(platform, 'optimalTimes', newTimes);
                          }}
                          className="text-blue-600 hover:text-blue-700 text-sm px-2 py-1 border border-dashed border-blue-300 rounded"
                        >
                          + Add Time
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Content Distribution */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Content Distribution</h2>
        
        <div className="space-y-4">
          {Object.entries(settings.contentDistribution).map(([domain, percentage]) => (
            <div key={domain} className="flex items-center space-x-4">
              <div className="w-20">
                <span className="text-sm font-medium text-gray-700 capitalize">{domain}</span>
              </div>
              <div className="flex-1">
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={percentage}
                  onChange={(e) => updateContentDistribution(domain, parseInt(e.target.value))}
                  className="w-full"
                />
              </div>
              <div className="w-12 text-right">
                <span className="text-sm font-medium text-gray-900">{percentage}%</span>
              </div>
            </div>
          ))}
          
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-600">Total Distribution:</span>
              <span className={`font-medium ${
                Object.values(settings.contentDistribution).reduce((a, b) => a + b, 0) === 100 
                  ? 'text-green-600' 
                  : 'text-red-600'
              }`}>
                {Object.values(settings.contentDistribution).reduce((a, b) => a + b, 0)}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">AI Configuration</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Creativity Level: {settings.aiSettings.creativity}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={settings.aiSettings.creativity}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                aiSettings: { ...prev.aiSettings, creativity: parseInt(e.target.value) }
              }))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">Higher = more creative and unique content</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Brand Voice Consistency: {settings.aiSettings.brandVoiceConsistency}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={settings.aiSettings.brandVoiceConsistency}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                aiSettings: { ...prev.aiSettings, brandVoiceConsistency: parseInt(e.target.value) }
              }))}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-1">Higher = more consistent with your brand voice</p>
          </div>
        </div>

        <div className="mt-6 space-y-4">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.aiSettings.engagementFocus}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                aiSettings: { ...prev.aiSettings, engagementFocus: e.target.checked }
              }))}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <div>
              <span className="text-sm font-medium text-gray-700">Engagement Focus</span>
              <p className="text-xs text-gray-500">AI will optimize content for maximum engagement</p>
            </div>
          </label>

          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.aiSettings.trendFollowing}
              onChange={(e) => setSettings(prev => ({
                ...prev,
                aiSettings: { ...prev.aiSettings, trendFollowing: e.target.checked }
              }))}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <div>
              <span className="text-sm font-medium text-gray-700">Trend Following</span>
              <p className="text-xs text-gray-500">AI will incorporate trending topics and hashtags</p>
            </div>
          </label>
        </div>
      </div>

      {/* Analytics Preview */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Performance Analytics</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <BarChart3 className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Best Performing Time</h3>
            <p className="text-2xl font-bold text-blue-600">2:00 PM</p>
            <p className="text-sm text-gray-600">+47% engagement</p>
          </div>
          
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <Users className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Avg Daily Reach</h3>
            <p className="text-2xl font-bold text-green-600">12.4K</p>
            <p className="text-sm text-gray-600">+23% this week</p>
          </div>
          
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <Target className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <h3 className="font-semibold text-gray-900">Engagement Rate</h3>
            <p className="text-2xl font-bold text-purple-600">8.7%</p>
            <p className="text-sm text-gray-600">Above average</p>
          </div>
        </div>
      </div>

      {/* Save Confirmation */}
      {Object.values(settings.contentDistribution).reduce((a, b) => a + b, 0) !== 100 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center space-x-2">
            <AlertCircle className="w-5 h-5 text-yellow-600" />
            <p className="text-sm text-yellow-800">
              Content distribution must total 100%. Currently at {Object.values(settings.contentDistribution).reduce((a, b) => a + b, 0)}%
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default PostingScheduler;