import React, { useState } from 'react';

const AutomationPage = () => {
  const [automationEnabled, setAutomationEnabled] = useState(false);
  const [selectedFrequency, setSelectedFrequency] = useState('daily');

  const automationRules = [
    {
      id: 1,
      name: 'Tech News Automation',
      description: 'Auto-post tech news content daily',
      platform: 'LinkedIn',
      frequency: 'Daily at 9:00 AM',
      status: 'active',
      postsGenerated: 45
    },
    {
      id: 2,
      name: 'Meme Monday',
      description: 'Share funny memes every Monday',
      platform: 'Instagram',
      frequency: 'Weekly on Monday',
      status: 'active',
      postsGenerated: 12
    },
    {
      id: 3,
      name: 'Coding Tips',
      description: 'Share programming tips and tricks',
      platform: 'Twitter',
      frequency: 'Daily at 2:00 PM',
      status: 'paused',
      postsGenerated: 28
    }
  ];

  const platforms = [
    { id: 'instagram', name: 'Instagram', icon: '📷', connected: true },
    { id: 'facebook', name: 'Facebook', icon: '📘', connected: true },
    { id: 'twitter', name: 'Twitter', icon: '🐦', connected: false },
    { id: 'linkedin', name: 'LinkedIn', icon: '💼', connected: true },
    { id: 'youtube', name: 'YouTube', icon: '🎥', connected: false },
    { id: 'tiktok', name: 'TikTok', icon: '🎵', connected: false }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'inactive':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Automation Hub</h1>
            <p className="text-gray-600 mt-1">Manage your AI-powered content automation</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center">
              <span className="text-sm text-gray-700 mr-3">Master Automation</span>
              <button
                onClick={() => setAutomationEnabled(!automationEnabled)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  automationEnabled ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    automationEnabled ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
            <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors">
              + New Rule
            </button>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-blue-100 rounded-lg">
              <span className="text-blue-600 text-xl">🤖</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Rules</p>
              <p className="text-2xl font-bold text-gray-900">
                {automationRules.filter(rule => rule.status === 'active').length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg">
              <span className="text-green-600 text-xl">📝</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Posts Generated</p>
              <p className="text-2xl font-bold text-gray-900">
                {automationRules.reduce((sum, rule) => sum + rule.postsGenerated, 0)}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-purple-100 rounded-lg">
              <span className="text-purple-600 text-xl">🔗</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Connected Platforms</p>
              <p className="text-2xl font-bold text-gray-900">
                {platforms.filter(platform => platform.connected).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center">
            <div className="p-3 bg-yellow-100 rounded-lg">
              <span className="text-yellow-600 text-xl">⚡</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Velocity Score</p>
              <p className="text-2xl font-bold text-gray-900">87%</p>
            </div>
          </div>
        </div>
      </div>

      {/* Automation Rules */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Automation Rules</h2>
          <div className="flex space-x-2">
            <button className="text-sm text-gray-600 hover:text-gray-900">Filter</button>
            <button className="text-sm text-gray-600 hover:text-gray-900">Sort</button>
          </div>
        </div>

        <div className="space-y-4">
          {automationRules.map((rule) => (
            <div key={rule.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-medium text-gray-900">{rule.name}</h3>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(rule.status)}`}>
                      {rule.status}
                    </span>
                  </div>
                  <p className="text-gray-600 text-sm mt-1">{rule.description}</p>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                    <span>📍 {rule.platform}</span>
                    <span>⏰ {rule.frequency}</span>
                    <span>📊 {rule.postsGenerated} posts generated</span>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <span>⚙️</span>
                  </button>
                  <button className="p-2 text-gray-400 hover:text-gray-600">
                    <span>📊</span>
                  </button>
                  <button className="p-2 text-gray-400 hover:text-red-600">
                    <span>🗑️</span>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Platform Status */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Platform Connections</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {platforms.map((platform) => (
            <div key={platform.id} className="border border-gray-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">{platform.icon}</span>
                  <div>
                    <h3 className="font-medium text-gray-900">{platform.name}</h3>
                    <p className="text-sm text-gray-500">
                      {platform.connected ? 'Connected' : 'Not connected'}
                    </p>
                  </div>
                </div>
                <div className={`w-3 h-3 rounded-full ${
                  platform.connected ? 'bg-green-500' : 'bg-gray-300'
                }`} />
              </div>
              {!platform.connected && (
                <button className="w-full mt-3 text-sm bg-blue-50 text-blue-700 py-2 rounded-md hover:bg-blue-100 transition-colors">
                  Connect Platform
                </button>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-center">
            <span className="text-3xl mb-2 block">🚀</span>
            <span className="text-sm font-medium text-gray-700">Create New Rule</span>
            <p className="text-xs text-gray-500 mt-1">Set up automated posting</p>
          </button>

          <button className="p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors text-center">
            <span className="text-3xl mb-2 block">📊</span>
            <span className="text-sm font-medium text-gray-700">View Analytics</span>
            <p className="text-xs text-gray-500 mt-1">Check automation performance</p>
          </button>

          <button className="p-6 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors text-center">
            <span className="text-3xl mb-2 block">⚙️</span>
            <span className="text-sm font-medium text-gray-700">Bulk Actions</span>
            <p className="text-xs text-gray-500 mt-1">Manage multiple rules</p>
          </button>
        </div>
      </div>
    </div>
  );
};

export default AutomationPage;