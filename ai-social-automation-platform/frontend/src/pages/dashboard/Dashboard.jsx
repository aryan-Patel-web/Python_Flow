import React, { useState } from 'react';
import { 
  Calendar, Clock, Zap, Search, Plus, BarChart3, Sparkles, Globe, MessageCircle, 
  TrendingUp, Eye, Heart, Bot, Brain, Instagram, Facebook, Twitter, Linkedin, 
  Youtube, Check, X, Shield, Edit3, Send, Image, Video, Hash, Menu, Filter
} from 'lucide-react';

const VelocityPostDashboard = () => {
  const [activeTab, setActiveTab] = useState('publishing');
  const [selectedPlatforms, setSelectedPlatforms] = useState(['instagram', 'twitter']);
  const [postContent, setPostContent] = useState('');
  const [isAiGenerating, setIsAiGenerating] = useState(false);
  const [selectedContentDomain, setSelectedContentDomain] = useState('tech-tips');
  const [showScheduler, setShowScheduler] = useState(false);
  const [scheduledDate, setScheduledDate] = useState('');
  const [scheduledTime, setScheduledTime] = useState('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const [connectedPlatforms] = useState({
    instagram: { connected: true, username: '@techstartup', followers: 12500 },
    twitter: { connected: true, username: '@techstartup', followers: 8300 },
    linkedin: { connected: true, username: 'Tech Startup Inc', followers: 2100 },
    facebook: { connected: false, username: null, followers: 0 },
    youtube: { connected: false, username: null, followers: 0 }
  });

  const [queuedPosts, setQueuedPosts] = useState([
    {
      id: 1,
      content: "🚀 Just shipped our new API endpoint! Now you can integrate our AI content generator directly into your workflow. Developers are going to love this...",
      platforms: ['twitter', 'linkedin'],
      scheduledFor: '2024-01-16 14:30',
      status: 'scheduled',
      aiGenerated: true,
      performanceScore: 87,
      estimatedReach: '2.5K',
      estimatedEngagement: '340'
    },
    {
      id: 2,
      content: "💡 Pro tip: The best time to post on LinkedIn is Tuesday-Thursday between 8-10 AM. Our AI analyzed 50,000+ posts to find this pattern.",
      platforms: ['linkedin', 'twitter'],
      scheduledFor: '2024-01-17 09:00',
      status: 'scheduled',
      aiGenerated: true,
      performanceScore: 92,
      estimatedReach: '3.2K',
      estimatedEngagement: '485'
    }
  ]);

  const [contentDomains] = useState([
    { id: 'tech-tips', name: '💻 Tech Tips', active: true, posts: 145, engagement: 12.3, color: 'bg-blue-500' },
    { id: 'startup-insights', name: '🚀 Startup Insights', active: true, posts: 89, engagement: 18.7, color: 'bg-purple-500' },
    { id: 'ai-trends', name: '🤖 AI Trends', active: true, posts: 67, engagement: 15.2, color: 'bg-green-500' },
    { id: 'product-updates', name: '📦 Product Updates', active: true, posts: 45, engagement: 15.8, color: 'bg-orange-500' }
  ]);

  const platformIcons = {
    instagram: Instagram,
    twitter: Twitter,
    linkedin: Linkedin,
    facebook: Facebook,
    youtube: Youtube
  };

  const platformColors = {
    instagram: 'from-pink-500 to-purple-600',
    twitter: 'from-blue-400 to-blue-600',
    linkedin: 'from-blue-600 to-blue-800',
    facebook: 'from-blue-500 to-blue-700',
    youtube: 'from-red-500 to-red-700'
  };

  const generateAiContent = async (domain = 'tech-tips') => {
    setIsAiGenerating(true);
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    const aiGeneratedContent = {
      'tech-tips': "🔧 JavaScript Performance Tip: Use `Object.freeze()` to prevent accidental mutations in your objects. It's a simple way to catch bugs early and improve code reliability. What's your favorite JS performance hack? 🚀 #JavaScript #WebDev #CodeTips",
      'startup-insights': "📈 Startup founders: Your MVP doesn't need to be perfect. It needs to solve one problem really well. Focus on that core value proposition and iterate from there. The market will tell you what to build next! 💡 #StartupLife #MVP #ProductDevelopment",
      'ai-trends': "🤖 The latest GPT-4 update shows 40% improvement in code generation accuracy. This is huge for developer productivity. We're already integrating it into our platform - the future of coding is here! 🚀 #AI #MachineLearning #TechNews #Coding",
      'product-updates': "🚀 New Feature Alert: Our AI now generates industry-specific content! Whether you're in fintech, healthcare, or e-commerce, get content that speaks your industry's language. Try it now! ✨ #ProductUpdate #AI #ContentMarketing"
    };

    setPostContent(aiGeneratedContent[domain] || aiGeneratedContent['tech-tips']);
    setIsAiGenerating(false);
  };

  const schedulePost = () => {
    const newPost = {
      id: queuedPosts.length + 1,
      content: postContent,
      platforms: selectedPlatforms,
      scheduledFor: scheduledDate && scheduledTime ? `${scheduledDate} ${scheduledTime}` : '2024-01-16 16:00',
      status: 'scheduled',
      aiGenerated: postContent.includes('AI') || postContent.includes('🤖') || postContent.includes('💡'),
      performanceScore: Math.floor(Math.random() * 20) + 80,
      estimatedReach: `${(Math.random() * 3 + 1).toFixed(1)}K`,
      estimatedEngagement: `${Math.floor(Math.random() * 300 + 200)}`
    };
    
    setQueuedPosts([...queuedPosts, newPost]);
    setPostContent('');
    setShowScheduler(false);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">VelocityPost.ai</h1>
              <span className="text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white px-2 py-1 rounded-full">
                AI-Powered
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search posts, analytics..."
                className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
              />
            </div>

            <div className="flex items-center space-x-2 bg-green-50 text-green-700 px-3 py-2 rounded-lg">
              <Bot className="w-4 h-4" />
              <span className="text-sm font-medium">AI Active</span>
            </div>

            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white font-medium text-sm">AP</span>
              </div>
              <span className="text-sm font-medium text-gray-700">Aryan Patel</span>
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`${sidebarCollapsed ? 'w-16' : 'w-64'} bg-white shadow-sm border-r border-gray-200 min-h-[calc(100vh-80px)] transition-all duration-300`}>
          <div className="p-4">
            <button
              onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
              className="w-full flex items-center justify-between p-2 rounded-lg hover:bg-gray-50 text-gray-600"
            >
              {!sidebarCollapsed && <span className="text-sm font-medium">Navigation</span>}
              <Menu className="w-4 h-4" />
            </button>
          </div>
          
          <nav className="px-4 space-y-2">
            {[
              { id: 'publishing', icon: Send, label: 'Publishing', active: activeTab === 'publishing' },
              { id: 'ai-content', icon: Brain, label: 'AI Content Lab', active: activeTab === 'ai-content', badge: 'NEW' },
              { id: 'calendar', icon: Calendar, label: 'Calendar', active: activeTab === 'calendar' },
              { id: 'analytics', icon: BarChart3, label: 'Analytics', active: activeTab === 'analytics' },
              { id: 'engagement', icon: MessageCircle, label: 'Engagement', active: activeTab === 'engagement' },
              { id: 'platforms', icon: Globe, label: 'Platforms', active: activeTab === 'platforms' }
            ].map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between p-3 rounded-lg transition-colors ${
                  item.active ? 'bg-blue-50 text-blue-700' : 'text-gray-700 hover:bg-gray-50'
                }`}
                title={sidebarCollapsed ? item.label : ''}
              >
                <div className="flex items-center space-x-3">
                  <item.icon className="w-5 h-5" />
                  {!sidebarCollapsed && <span className={item.active ? 'font-medium' : ''}>{item.label}</span>}
                </div>
                {!sidebarCollapsed && item.badge && (
                  <span className="text-xs bg-gradient-to-r from-purple-500 to-pink-500 text-white px-2 py-1 rounded-full">
                    {item.badge}
                  </span>
                )}
              </button>
            ))}
          </nav>

          {/* AI Performance Widget */}
          {!sidebarCollapsed && (
            <div className="m-4 p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg text-white">
              <div className="flex items-center space-x-2 mb-3">
                <Sparkles className="w-5 h-5" />
                <h3 className="font-semibold">AI Performance</h3>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Posts Generated</span>
                  <span className="font-semibold">342</span>
                </div>
                <div className="flex justify-between">
                  <span>Avg Performance</span>
                  <span className="font-semibold">+127%</span>
                </div>
                <div className="flex justify-between">
                  <span>Time Saved</span>
                  <span className="font-semibold">43 hours</span>
                </div>
              </div>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          {activeTab === 'publishing' && (
            <div className="space-y-6">
              {/* Create Post Section */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Create Post</h2>
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => generateAiContent(selectedContentDomain)}
                      disabled={isAiGenerating}
                      className="flex items-center space-x-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
                    >
                      {isAiGenerating ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <Bot className="w-4 h-4" />
                          <span>Generate with AI</span>
                        </>
                      )}
                    </button>
                    <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                      <Plus className="w-4 h-4" />
                      <span>Manual Post</span>
                    </button>
                  </div>
                </div>

                {/* Content Domain Selection */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Content Domain:</label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {contentDomains.map((domain) => (
                      <button
                        key={domain.id}
                        onClick={() => setSelectedContentDomain(domain.id)}
                        className={`p-3 rounded-lg border-2 transition-all text-left ${
                          selectedContentDomain === domain.id
                            ? 'border-purple-500 bg-purple-50'
                            : 'border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <div className="flex items-center space-x-2 mb-1">
                          <div className={`w-3 h-3 rounded-full ${domain.color}`}></div>
                          <span className="text-sm font-medium">{domain.name}</span>
                        </div>
                        <div className="text-xs text-gray-500">
                          {domain.posts} posts • {domain.engagement}% engagement
                        </div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Platform Selection */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Post to:</label>
                  <div className="flex items-center space-x-3 flex-wrap gap-2">
                    {Object.entries(connectedPlatforms).map(([platform, data]) => {
                      const IconComponent = platformIcons[platform];
                      const isSelected = selectedPlatforms.includes(platform);
                      const isConnected = data.connected;
                      
                      return (
                        <button
                          key={platform}
                          onClick={() => {
                            if (!isConnected) return;
                            setSelectedPlatforms(prev => 
                              isSelected 
                                ? prev.filter(p => p !== platform)
                                : [...prev, platform]
                            );
                          }}
                          disabled={!isConnected}
                          className={`flex items-center space-x-2 px-3 py-2 rounded-lg border transition-all ${
                            !isConnected 
                              ? 'border-gray-200 bg-gray-50 opacity-50 cursor-not-allowed'
                              : isSelected
                                ? `border-purple-500 bg-gradient-to-r ${platformColors[platform]} text-white`
                                : 'border-gray-200 hover:border-gray-300 bg-white'
                          }`}
                        >
                          <IconComponent className="w-4 h-4" />
                          <span className="text-sm capitalize">{platform}</span>
                          {isConnected && isSelected && <Check className="w-3 h-3" />}
                          {!isConnected && <X className="w-3 h-3 text-gray-400" />}
                        </button>
                      );
                    })}
                  </div>
                </div>

                {/* Content Input */}
                <div className="mb-4">
                  <div className="relative">
                    <textarea
                      value={postContent}
                      onChange={(e) => setPostContent(e.target.value)}
                      placeholder="What would you like to share? Or click 'Generate with AI' for instant content ideas..."
                      className="w-full p-4 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 min-h-[120px] resize-none"
                    />
                    <div className="absolute bottom-3 right-3 flex items-center space-x-3">
                      <span className="text-xs text-gray-500">{postContent.length}/280</span>
                      {(postContent.includes('🤖') || postContent.includes('💡') || postContent.includes('AI')) && (
                        <div className="flex items-center space-x-1 text-purple-600">
                          <Sparkles className="w-3 h-3" />
                          <span className="text-xs">AI Generated</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Media Upload */}
                <div className="mb-4 flex items-center space-x-4">
                  <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors">
                    <Image className="w-4 h-4" />
                    <span className="text-sm">Add Image</span>
                  </button>
                  <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors">
                    <Video className="w-4 h-4" />
                    <span className="text-sm">Add Video</span>
                  </button>
                  <button className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 transition-colors">
                    <Hash className="w-4 h-4" />
                    <span className="text-sm">Trending Tags</span>
                  </button>
                  <button className="flex items-center space-x-2 text-purple-600 hover:text-purple-700 transition-colors">
                    <Brain className="w-4 h-4" />
                    <span className="text-sm">AI Optimize</span>
                  </button>
                </div>

                {/* AI Performance Prediction */}
                {postContent && (
                  <div className="mb-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <Brain className="w-4 h-4 text-green-600" />
                        <span className="text-sm font-medium text-green-800">AI Performance Prediction</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 h-2 bg-green-200 rounded-full">
                          <div className="w-16 h-2 bg-green-500 rounded-full"></div>
                        </div>
                        <span className="text-sm font-semibold text-green-800">87/100</span>
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-xs text-green-700">
                      <div>
                        <span className="font-medium">Estimated Reach:</span>
                        <div className="text-green-800 font-semibold">2.3K users</div>
                      </div>
                      <div>
                        <span className="font-medium">Predicted Engagement:</span>
                        <div className="text-green-800 font-semibold">+23% above avg</div>
                      </div>
                      <div>
                        <span className="font-medium">Best Time:</span>
                        <div className="text-green-800 font-semibold">2:30 PM today</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={schedulePost}
                      disabled={!postContent || selectedPlatforms.length === 0}
                      className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Add to Queue
                    </button>
                    <button 
                      onClick={() => setShowScheduler(true)}
                      className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      Schedule for Later
                    </button>
                    <button className="border border-gray-300 text-gray-700 px-6 py-2 rounded-lg hover:bg-gray-50 transition-colors">
                      Save as Draft
                    </button>
                  </div>
                  <button className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 transition-colors">
                    Share Now
                  </button>
                </div>

                {/* Scheduler Modal */}
                {showScheduler && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
                    <div className="bg-white rounded-xl p-6 w-96 max-w-90vw">
                      <h3 className="text-lg font-semibold mb-4">Schedule Post</h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Date</label>
                          <input
                            type="date"
                            value={scheduledDate}
                            onChange={(e) => setScheduledDate(e.target.value)}
                            className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Time</label>
                          <input
                            type="time"
                            value={scheduledTime}
                            onChange={(e) => setScheduledTime(e.target.value)}
                            className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                          />
                        </div>
                        <div className="flex items-center space-x-3">
                          <button
                            onClick={() => setShowScheduler(false)}
                            className="flex-1 border border-gray-300 text-gray-700 py-2 rounded-lg hover:bg-gray-50 transition-colors"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={schedulePost}
                            className="flex-1 bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors"
                          >
                            Schedule
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>

              {/* Queue Section */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-lg font-semibold text-gray-900">Scheduled Posts Queue</h2>
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Clock className="w-4 h-4" />
                      <span>{queuedPosts.length} posts scheduled</span>
                    </div>
                    <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 text-sm">
                      <Filter className="w-4 h-4" />
                      <span>Filter</span>
                    </button>
                  </div>
                </div>

                <div className="space-y-4">
                  {queuedPosts.map((post) => (
                    <div key={post.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-3">
                            {post.platforms.map(platform => {
                              const IconComponent = platformIcons[platform];
                              return (
                                <div key={platform} className={`flex items-center space-x-1 text-xs bg-gradient-to-r ${platformColors[platform]} text-white px-2 py-1 rounded-full`}>
                                  <IconComponent className="w-3 h-3" />
                                  <span className="capitalize">{platform}</span>
                                </div>
                              );
                            })}
                            {post.aiGenerated && (
                              <div className="flex items-center space-x-1 text-xs bg-purple-100 text-purple-700 px-2 py-1 rounded-full">
                                <Sparkles className="w-3 h-3" />
                                <span>AI Generated</span>
                              </div>
                            )}
                            <div className="flex items-center space-x-1 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                              <TrendingUp className="w-3 h-3" />
                              <span>Score: {post.performanceScore}/100</span>
                            </div>
                          </div>
                          <p className="text-gray-900 mb-3 leading-relaxed">{post.content}</p>
                          <div className="flex items-center space-x-6 text-sm text-gray-600">
                            <div className="flex items-center space-x-1">
                              <Calendar className="w-4 h-4" />
                              <span>{post.scheduledFor}</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Eye className="w-4 h-4" />
                              <span>{post.estimatedReach} reach</span>
                            </div>
                            <div className="flex items-center space-x-1">
                              <Heart className="w-4 h-4" />
                              <span>{post.estimatedEngagement} engagement</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center space-x-2 ml-4">
                          <button className="text-gray-400 hover:text-blue-600 transition-colors">
                            <Edit3 className="w-4 h-4" />
                          </button>
                          <button className="text-gray-400 hover:text-red-500 transition-colors">
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'ai-content' && (
            <div className="space-y-6">
              <div className="text-center py-12">
                <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-6">
                  <Brain className="w-10 h-10 text-white" />
                </div>
                <h2 className="text-3xl font-bold text-gray-900 mb-3">AI Content Lab</h2>
                <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
                  Generate unlimited content ideas with our industry-specific AI engine. Each domain is trained on thousands of high-performing posts.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
                  {contentDomains.map((domain) => (
                    <div key={domain.id} className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow cursor-pointer"
                         onClick={() => generateAiContent(domain.id)}>
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-gray-900">{domain.name}</h3>
                        <div className={`w-3 h-3 rounded-full ${domain.active ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                      </div>
                                              <div className="space-y-2 text-sm text-gray-600">
                        <div className="flex justify-between">
                          <span>Generated Posts</span>
                          <span className="font-medium">{domain.posts}</span>
                        </div>
                        <div className="flex justify-between">
                          <span>Avg Engagement</span>
                          <span className="font-medium text-green-600">{domain.engagement}%</span>
                        </div>
                      </div>
                      <button className="w-full mt-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white py-2 rounded-lg hover:opacity-90">
                        Generate Content
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">AI-Generated Posts</p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">284</p>
                    </div>
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                      <Bot className="w-6 h-6 text-purple-600" />
                    </div>
                  </div>
                  <div className="flex items-center mt-4">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-green-600 ml-1">+127% vs manual posts</span>
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Total Engagement</p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">98.5K</p>
                    </div>
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                      <Heart className="w-6 h-6 text-green-600" />
                    </div>
                  </div>
                  <div className="flex items-center mt-4">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-green-600 ml-1">+89% this month</span>
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">Time Saved</p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">43h</p>
                    </div>
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Clock className="w-6 h-6 text-blue-600" />
                    </div>
                  </div>
                  <div className="flex items-center mt-4">
                    <Bot className="w-4 h-4 text-blue-500" />
                    <span className="text-sm text-blue-600 ml-1">vs manual creation</span>
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium text-gray-600">AI Performance Score</p>
                      <p className="text-3xl font-bold text-gray-900 mt-1">91/100</p>
                    </div>
                    <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                      <Brain className="w-6 h-6 text-yellow-600" />
                    </div>
                  </div>
                  <div className="flex items-center mt-4">
                    <TrendingUp className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm text-yellow-600 ml-1">Learning & improving</span>
                  </div>
                </div>
              </div>

              {/* AI vs Manual Performance Chart */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">AI vs Manual Content Performance</h3>
                <div className="h-64 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-500">Performance comparison chart</p>
                    <p className="text-sm text-gray-400">AI content performs 127% better on average</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'platforms' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6">
                <div className="flex items-center space-x-3 mb-3">
                  <Shield className="w-6 h-6 text-green-600" />
                  <h3 className="text-lg font-semibold text-gray-900">🔒 Secure OAuth 2.0 Authentication</h3>
                </div>
                <p className="text-gray-700 mb-4">
                  Unlike Buffer's basic connection, we use bank-level security with AI-powered optimization for each platform.
                </p>
                <div className="flex items-center space-x-4 text-sm">
                  <div className="flex items-center space-x-1 text-green-600">
                    <Check className="w-4 h-4" />
                    <span>Military-grade encryption</span>
                  </div>
                  <div className="flex items-center space-x-1 text-green-600">
                    <Check className="w-4 h-4" />
                    <span>AI content optimization</span>
                  </div>
                  <div className="flex items-center space-x-1 text-green-600">
                    <Check className="w-4 h-4" />
                    <span>Performance tracking</span>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {Object.entries(connectedPlatforms).map(([platform, data]) => {
                  const IconComponent = platformIcons[platform];
                  return (
                    <div key={platform} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                      <div className="flex items-center space-x-4 mb-4">
                        <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                          data.connected 
                            ? 'bg-gradient-to-r from-blue-500 to-purple-500' 
                            : 'bg-gray-100'
                        }`}>
                          <IconComponent className={`w-6 h-6 ${data.connected ? 'text-white' : 'text-gray-400'}`} />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h3 className="text-lg font-semibold text-gray-900 capitalize">{platform}</h3>
                            {data.connected && (
                              <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                                AI Optimized
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-600">
                            {data.connected ? `${data.followers.toLocaleString()} followers` : 'Not connected'}
                          </p>
                        </div>
                      </div>

                      <div className="mb-4">
                        {data.connected ? (
                          <div className="flex items-center space-x-2 text-green-600">
                            <Check className="w-4 h-4" />
                            <span className="text-sm font-medium">Connected & AI-Optimized</span>
                          </div>
                        ) : (
                          <div className="flex items-center space-x-2 text-gray-500">
                            <X className="w-4 h-4" />
                            <span className="text-sm">Not connected</span>
                          </div>
                        )}
                      </div>

                      {data.connected && (
                        <div className="mb-4 space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">AI Performance Score</span>
                            <span className="font-medium text-green-600">94/100</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Posts This Month</span>
                            <span className="font-medium">23</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Avg Engagement</span>
                            <span className="font-medium text-green-600">+187%</span>
                          </div>
                        </div>
                      )}

                      <div className="space-y-2">
                        {data.connected ? (
                          <div className="space-y-2">
                            <button className="w-full bg-blue-50 text-blue-700 py-2 px-4 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium">
                              🚀 Optimize with AI
                            </button>
                            <button className="w-full bg-red-50 text-red-700 py-2 px-4 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium">
                              Disconnect
                            </button>
                          </div>
                        ) : (
                          <button className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 px-4 rounded-lg hover:opacity-90 transition-opacity font-medium flex items-center justify-center space-x-2">
                            <Shield className="w-4 h-4" />
                            <span>🔒 Connect Securely</span>
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Comparison with Buffer */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Why VelocityPost Beats Buffer</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
                      <X className="w-4 h-4 text-red-500" />
                      <span>Buffer's Limitations</span>
                    </h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• Manual content creation only</li>
                      <li>• Generic posting for all industries</li>
                      <li>• Basic scheduling without optimization</li>
                      <li>• Limited performance insights</li>
                      <li>• No AI-powered improvements</li>
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-3 flex items-center space-x-2">
                      <Check className="w-4 h-4 text-green-500" />
                      <span>VelocityPost Advantages</span>
                    </h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li>• AI generates unlimited content ideas</li>
                      <li>• Industry-specific content optimization</li>
                      <li>• Smart timing based on audience behavior</li>
                      <li>• Performance prediction before posting</li>
                      <li>• Continuous learning and improvement</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default VelocityPostDashboard;