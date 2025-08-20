import React, { useState, useEffect, createContext, useContext } from 'react';
import { ArrowUp, ArrowDown, TrendingUp, Users, Eye, Heart, Share2, Calendar, Clock, Zap, Bell, Search, Settings, LogOut, ChevronLeft, Plus, Play, Pause, BarChart3, Target, Sparkles, Globe, MessageCircle, Star, Filter, Download, RefreshCw, Home, CreditCard, User, Mail, Lock, Building, ChevronRight, Instagram, Facebook, Twitter, Linkedin, Youtube, Check, X } from 'lucide-react';

// Auth Context
const AuthContext = createContext();

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState({ name: 'Aryan Patel', email: 'aryan@example.com', avatar: 'AP' });
  const [isAuthenticated, setIsAuthenticated] = useState(true);

  const login = (email, password) => {
    // Simulate login
    setIsAuthenticated(true);
    setUser({ name: 'Aryan Patel', email, avatar: 'AP' });
    return Promise.resolve();
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

const useAuth = () => useContext(AuthContext);

// Router Context (Simple routing simulation)
const RouterContext = createContext();

const Router = ({ children }) => {
  const [currentPath, setCurrentPath] = useState('/dashboard');
  const [history, setHistory] = useState(['/dashboard']);

  const navigate = (path) => {
    setHistory(prev => [...prev, path]);
    setCurrentPath(path);
  };

  const goBack = () => {
    if (history.length > 1) {
      const newHistory = history.slice(0, -1);
      setHistory(newHistory);
      setCurrentPath(newHistory[newHistory.length - 1]);
    }
  };

  return (
    <RouterContext.Provider value={{ currentPath, navigate, goBack, history }}>
      {children}
    </RouterContext.Provider>
  );
};

const useRouter = () => useContext(RouterContext);

// Layout Component
const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const { currentPath, navigate, goBack } = useRouter();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [notifications] = useState(3);

  const sidebarItems = [
    { path: '/dashboard', icon: BarChart3, label: 'Dashboard' },
    { path: '/platforms', icon: Globe, label: 'Platforms' },
    { path: '/domains', icon: Target, label: 'Content Domains' },
    { path: '/content', icon: Sparkles, label: 'Content Library' },
    { path: '/analytics', icon: TrendingUp, label: 'Analytics' },
    { path: '/automation', icon: Zap, label: 'Automation' },
    { path: '/billing', icon: CreditCard, label: 'Billing' },
    { path: '/settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center space-x-4">
            <button 
              onClick={goBack}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Go back"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-xl font-bold text-gray-900">VelocityPost.ai</h1>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="Search..."
                className="pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 w-64"
              />
            </div>

            <div className="relative">
              <button
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors relative"
              >
                <Bell className="w-5 h-5 text-gray-600" />
                {notifications > 0 && (
                  <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {notifications}
                  </span>
                )}
              </button>
              
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="p-4 border-b border-gray-100">
                    <h3 className="font-semibold text-gray-900">Notifications</h3>
                  </div>
                  <div className="p-2">
                    <div className="p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                      <p className="text-sm text-gray-900">Your Instagram post got 100+ likes!</p>
                      <p className="text-xs text-gray-500">5 minutes ago</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="relative">
              <button
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center space-x-2 p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <div className="w-8 h-8 bg-gradient-to-r from-green-400 to-blue-500 rounded-full flex items-center justify-center">
                  <span className="text-white font-medium text-sm">{user?.avatar}</span>
                </div>
                <span className="text-sm font-medium text-gray-700">{user?.name}</span>
              </button>

              {showUserMenu && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="p-2">
                    <button 
                      onClick={() => navigate('/settings')}
                      className="w-full flex items-center space-x-2 p-2 hover:bg-gray-50 rounded-lg"
                    >
                      <Settings className="w-4 h-4 text-gray-600" />
                      <span className="text-sm text-gray-700">Settings</span>
                    </button>
                    <button 
                      onClick={logout}
                      className="w-full flex items-center space-x-2 p-2 hover:bg-gray-50 rounded-lg"
                    >
                      <LogOut className="w-4 h-4 text-gray-600" />
                      <span className="text-sm text-gray-700">Logout</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <div className="flex pt-16">
        {/* Sidebar */}
        <aside className="w-64 bg-white shadow-sm border-r border-gray-200 min-h-[calc(100vh-64px)] fixed left-0 top-16">
          <nav className="p-4 space-y-2">
            {sidebarItems.map((item) => (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center space-x-3 p-3 rounded-lg transition-colors ${
                  currentPath === item.path
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <item.icon className="w-5 h-5" />
                <span className={currentPath === item.path ? 'font-medium' : ''}>{item.label}</span>
              </button>
            ))}
          </nav>

          <div className="m-4 p-4 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg text-white">
            <h3 className="font-semibold mb-1">Upgrade to Pro</h3>
            <p className="text-sm text-purple-100 mb-3">Unlimited posts, advanced analytics</p>
            <button 
              onClick={() => navigate('/billing')}
              className="w-full bg-white text-purple-600 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors"
            >
              Upgrade Now
            </button>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 ml-64 p-6">
          {children}
        </main>
      </div>
    </div>
  );
};

// Dashboard Page
const DashboardPage = () => {
  const { navigate } = useRouter();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d');
  const [automationStatus, setAutomationStatus] = useState('running');

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  const stats = {
    '24h': { posts: 12, engagement: '3.2K', followers: 1234, reach: '18.2K' },
    '7d': { posts: 89, engagement: '24.7K', followers: 1387, reach: '156.8K' },
    '30d': { posts: 342, engagement: '98.5K', followers: 1689, reach: '542.1K' },
  }[selectedTimeRange];

  const platforms = [
    { name: 'Instagram', icon: '📷', color: 'bg-gradient-to-r from-purple-500 to-pink-500', followers: 892, posts: 45, engagement: '8.2%' },
    { name: 'Twitter', icon: '🐦', color: 'bg-blue-500', followers: 1234, posts: 78, engagement: '5.7%' },
    { name: 'LinkedIn', icon: '💼', color: 'bg-blue-600', followers: 567, posts: 23, engagement: '12.3%' },
    { name: 'Facebook', icon: '📘', color: 'bg-blue-700', followers: 456, posts: 34, engagement: '6.8%' },
    { name: 'TikTok', icon: '🎵', color: 'bg-black', followers: 2341, posts: 67, engagement: '15.2%' },
    { name: 'YouTube', icon: '📺', color: 'bg-red-500', followers: 789, posts: 12, engagement: '9.4%' }
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Welcome back, Aryan! 👋</h1>
          <p className="text-gray-600 mt-1">
            {currentTime.toLocaleDateString('en-US', { 
              weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
              hour: '2-digit', minute: '2-digit'
            })}
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={selectedTimeRange}
            onChange={(e) => setSelectedTimeRange(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
          </select>
          <button 
            onClick={() => navigate('/content')}
            className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Create Post</span>
          </button>
        </div>
      </div>

      {/* Automation Status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${
              automationStatus === 'running' ? 'bg-green-100' : 'bg-yellow-100'
            }`}>
              <Zap className={`w-6 h-6 ${
                automationStatus === 'running' ? 'text-green-600' : 'text-yellow-600'
              }`} />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-gray-900">
                Automation {automationStatus === 'running' ? 'Active' : 'Paused'}
              </h3>
              <p className="text-gray-600">
                {automationStatus === 'running' 
                  ? 'AI is generating and posting content automatically' 
                  : 'Automation is currently paused'
                }
              </p>
            </div>
          </div>
          <button
            onClick={() => setAutomationStatus(prev => prev === 'running' ? 'paused' : 'running')}
            className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
              automationStatus === 'running'
                ? 'bg-yellow-100 text-yellow-700 hover:bg-yellow-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
          >
            {automationStatus === 'running' ? (
              <>
                <Pause className="w-4 h-4" />
                <span>Pause</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                <span>Resume</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Posts</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.posts}</p>
            </div>
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
              <Sparkles className="w-6 h-6 text-blue-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <ArrowUp className="w-4 h-4 text-green-500" />
            <span className="text-sm text-green-600 ml-1">+12% from last week</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Engagement</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.engagement}</p>
            </div>
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
              <Heart className="w-6 h-6 text-green-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <ArrowUp className="w-4 h-4 text-green-500" />
            <span className="text-sm text-green-600 ml-1">+8.2% from last week</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Followers</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.followers.toLocaleString()}</p>
            </div>
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-6 h-6 text-purple-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <ArrowUp className="w-4 h-4 text-green-500" />
            <span className="text-sm text-green-600 ml-1">+5.4% from last week</span>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Reach</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{stats.reach}</p>
            </div>
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
              <Eye className="w-6 h-6 text-orange-600" />
            </div>
          </div>
          <div className="flex items-center mt-4">
            <ArrowDown className="w-4 h-4 text-red-500" />
            <span className="text-sm text-red-600 ml-1">-2.1% from last week</span>
          </div>
        </div>
      </div>

      {/* Platform Performance */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold text-gray-900">Platform Performance</h2>
          <button 
            onClick={() => navigate('/platforms')}
            className="text-blue-600 text-sm hover:text-blue-700"
          >
            View All
          </button>
        </div>
        
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          {platforms.map((platform) => (
            <div key={platform.name} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow cursor-pointer">
              <div className="flex items-center space-x-3 mb-3">
                <div className={`w-10 h-10 ${platform.color} rounded-lg flex items-center justify-center text-white text-lg`}>
                  {platform.icon}
                </div>
                <div>
                  <h3 className="font-medium text-gray-900">{platform.name}</h3>
                  <p className="text-sm text-gray-600">{platform.followers} followers</p>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Posts</span>
                  <span className="font-medium">{platform.posts}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span className="text-gray-600">Engagement</span>
                  <span className="font-medium text-green-600">{platform.engagement}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Platforms Page
const PlatformsPage = () => {
  const [connectedPlatforms, setConnectedPlatforms] = useState({
    instagram: true,
    twitter: true,
    linkedin: false,
    facebook: false,
    tiktok: false,
    youtube: false
  });
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [selectedPlatform, setSelectedPlatform] = useState(null);

  const platforms = [
    { id: 'instagram', name: 'Instagram', icon: Instagram, color: 'from-purple-500 to-pink-500', description: 'Share photos and stories' },
    { id: 'twitter', name: 'Twitter', icon: Twitter, color: 'from-blue-400 to-blue-600', description: 'Share thoughts and updates' },
    { id: 'linkedin', name: 'LinkedIn', icon: Linkedin, color: 'from-blue-600 to-blue-800', description: 'Professional networking' },
    { id: 'facebook', name: 'Facebook', icon: Facebook, color: 'from-blue-500 to-blue-700', description: 'Connect with friends' },
    { id: 'tiktok', name: 'TikTok', icon: MessageCircle, color: 'from-black to-gray-800', description: 'Short video content' },
    { id: 'youtube', name: 'YouTube', icon: Youtube, color: 'from-red-500 to-red-700', description: 'Video sharing platform' }
  ];

  const handleConnect = (platform) => {
    setSelectedPlatform(platform);
    setShowConnectionModal(true);
  };

  const handleConnectionSubmit = () => {
    setConnectedPlatforms(prev => ({
      ...prev,
      [selectedPlatform.id]: true
    }));
    setShowConnectionModal(false);
    setSelectedPlatform(null);
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Platform Connections</h1>
          <p className="text-gray-600 mt-2">Connect your social media accounts to start automating</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {platforms.map((platform) => (
          <div key={platform.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center space-x-4 mb-4">
              <div className={`w-12 h-12 bg-gradient-to-r ${platform.color} rounded-lg flex items-center justify-center`}>
                <platform.icon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{platform.name}</h3>
                <p className="text-sm text-gray-600">{platform.description}</p>
              </div>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {connectedPlatforms[platform.id] ? (
                  <>
                    <Check className="w-4 h-4 text-green-500" />
                    <span className="text-sm text-green-600">Connected</span>
                  </>
                ) : (
                  <>
                    <X className="w-4 h-4 text-gray-400" />
                    <span className="text-sm text-gray-500">Not connected</span>
                  </>
                )}
              </div>
              <button
                onClick={() => connectedPlatforms[platform.id] ? null : handleConnect(platform)}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  connectedPlatforms[platform.id]
                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                }`}
                disabled={connectedPlatforms[platform.id]}
              >
                {connectedPlatforms[platform.id] ? 'Connected' : 'Connect'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Connection Modal */}
      {showConnectionModal && selectedPlatform && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-96">
            <h3 className="text-lg font-semibold mb-4">Connect {selectedPlatform.name}</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Username</label>
                <input
                  type="text"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your username"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                <input
                  type="password"
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter your password"
                />
              </div>
            </div>
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowConnectionModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleConnectionSubmit}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Connect
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Content Domains Page
const DomainsPage = () => {
  const { navigate } = useRouter();
  const [selectedDomains, setSelectedDomains] = useState(['tech-tips', 'memes']);
  const [postingFrequency, setPostingFrequency] = useState(3);
  const [postingTimes, setPostingTimes] = useState(['morning', 'afternoon']);

  const domains = [
    { id: 'tech-tips', name: 'Tech Tips', description: 'Programming tips and tricks', color: 'bg-blue-500', posts: 145, engagement: '12.3%' },
    { id: 'memes', name: 'Memes', description: 'Funny programming memes', color: 'bg-green-500', posts: 89, engagement: '18.7%' },
    { id: 'career-advice', name: 'Career Advice', description: 'Professional development tips', color: 'bg-purple-500', posts: 67, engagement: '9.2%' },
    { id: 'tutorials', name: 'Tutorials', description: 'Step-by-step coding guides', color: 'bg-orange-500', posts: 45, engagement: '15.8%' },
    { id: 'news', name: 'Tech News', description: 'Latest technology updates', color: 'bg-red-500', posts: 23, engagement: '11.4%' },
    { id: 'tools', name: 'Developer Tools', description: 'Useful development tools', color: 'bg-indigo-500', posts: 34, engagement: '13.2%' }
  ];

  const times = [
    { id: 'morning', label: 'Morning (9 AM)', description: 'Best for professional content' },
    { id: 'afternoon', label: 'Afternoon (2 PM)', description: 'Good for engagement' },
    { id: 'evening', label: 'Evening (6 PM)', description: 'Peak social media time' }
  ];

  const toggleDomain = (domainId) => {
    setSelectedDomains(prev => 
      prev.includes(domainId) 
        ? prev.filter(id => id !== domainId)
        : [...prev, domainId]
    );
  };

  const toggleTime = (timeId) => {
    setPostingTimes(prev => 
      prev.includes(timeId) 
        ? prev.filter(id => id !== timeId)
        : [...prev, timeId]
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Content Domains</h1>
        <p className="text-gray-600 mt-2">Choose the types of content you want to automate</p>
      </div>

      {/* Domain Selection */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Select Content Domains</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {domains.map((domain) => (
            <div
              key={domain.id}
              onClick={() => toggleDomain(domain.id)}
              className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                selectedDomains.includes(domain.id)
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-center space-x-3 mb-3">
                <div className={`w-3 h-3 ${domain.color} rounded-full`}></div>
                <h3 className="font-medium text-gray-900">{domain.name}</h3>
                {selectedDomains.includes(domain.id) && (
                  <Check className="w-4 h-4 text-blue-500 ml-auto" />
                )}
              </div>
              <p className="text-sm text-gray-600 mb-3">{domain.description}</p>
              <div className="flex justify-between text-xs">
                <span className="text-gray-500">{domain.posts} posts</span>
                <span className="text-green-600">{domain.engagement} engagement</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Posting Settings */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Posting Settings</h2>
        
        <div className="space-y-6">
          {/* Frequency */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Posts per day: {postingFrequency}
            </label>
            <input
              type="range"
              min="1"
              max="6"
              value={postingFrequency}
              onChange={(e) => setPostingFrequency(e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>1</span>
              <span>3</span>
              <span>6</span>
            </div>
          </div>

          {/* Timing */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Posting Times</label>
            <div className="space-y-2">
              {times.map((time) => (
                <label key={time.id} className="flex items-center space-x-3 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={postingTimes.includes(time.id)}
                    onChange={() => toggleTime(time.id)}
                    className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <div>
                    <span className="text-sm font-medium text-gray-900">{time.label}</span>
                    <p className="text-xs text-gray-500">{time.description}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={() => navigate('/content')}
          className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          Save Settings & View Content
        </button>
        <button
          onClick={() => navigate('/automation')}
          className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg hover:bg-green-700 transition-colors font-medium"
        >
          Start Automation
        </button>
      </div>
    </div>
  );
};

// Content Library Page
const ContentPage = () => {
  const { navigate } = useRouter();
  const [contentFilter, setContentFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedContent, setSelectedContent] = useState([]);

  const content = [
    {
      id: 1,
      platform: 'Instagram',
      type: 'Tech Tips',
      title: '10 JavaScript tips that will blow your mind 🤯',
      status: 'posted',
      scheduledFor: '2024-01-15 14:30',
      engagement: { likes: 245, comments: 12, shares: 8 },
      performance: 'high'
    },
    {
      id: 2,
      platform: 'Twitter',
      type: 'Memes',
      title: 'When you finally fix that bug that\'s been haunting you for days...',
      status: 'posted',
      scheduledFor: '2024-01-15 10:15',
      engagement: { likes: 89, comments: 23, shares: 34 },
      performance: 'medium'
    },
    {
      id: 3,
      platform: 'LinkedIn',
      type: 'Career Advice',
      title: 'The future of AI in software development - my thoughts',
      status: 'scheduled',
      scheduledFor: '2024-01-16 09:00',
      engagement: null,
      performance: 'scheduled'
    },
    {
      id: 4,
      platform: 'Facebook',
      type: 'Tech News',
      title: 'Breaking: New JavaScript framework released',
      status: 'draft',
      scheduledFor: null,
      engagement: null,
      performance: 'draft'
    }
  ];

  const filteredContent = content.filter(item => {
    if (contentFilter !== 'all' && item.platform.toLowerCase() !== contentFilter) return false;
    if (statusFilter !== 'all' && item.status !== statusFilter) return false;
    return true;
  });

  const toggleContentSelection = (id) => {
    setSelectedContent(prev => 
      prev.includes(id) 
        ? prev.filter(itemId => itemId !== id)
        : [...prev, id]
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Content Library</h1>
          <p className="text-gray-600 mt-2">Manage your generated and scheduled content</p>
        </div>
        <button
          onClick={() => navigate('/content/create')}
          className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          <span>Generate Content</span>
        </button>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
        <div className="flex items-center space-x-4">
          <div>
            <label className="text-sm font-medium text-gray-700 mr-2">Platform:</label>
            <select
              value={contentFilter}
              onChange={(e) => setContentFilter(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Platforms</option>
              <option value="instagram">Instagram</option>
              <option value="twitter">Twitter</option>
              <option value="linkedin">LinkedIn</option>
              <option value="facebook">Facebook</option>
            </select>
          </div>
          <div>
            <label className="text-sm font-medium text-gray-700 mr-2">Status:</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-200 rounded-lg px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Status</option>
              <option value="posted">Posted</option>
              <option value="scheduled">Scheduled</option>
              <option value="draft">Draft</option>
            </select>
          </div>
          {selectedContent.length > 0 && (
            <div className="ml-auto flex items-center space-x-2">
              <span className="text-sm text-gray-600">{selectedContent.length} selected</span>
              <button className="text-sm text-red-600 hover:text-red-700">Delete</button>
            </div>
          )}
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredContent.map((item) => (
          <div key={item.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={selectedContent.includes(item.id)}
                  onChange={() => toggleContentSelection(item.id)}
                  className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">
                  {item.platform}
                </span>
              </div>
              <span className={`text-xs px-2 py-1 rounded-full ${
                item.status === 'posted' ? 'bg-green-100 text-green-700' :
                item.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {item.status}
              </span>
            </div>

            <h3 className="font-medium text-gray-900 mb-2 line-clamp-2">{item.title}</h3>
            <p className="text-sm text-gray-600 mb-3">{item.type}</p>

            {item.scheduledFor && (
              <p className="text-xs text-gray-500 mb-3">
                {item.status === 'posted' ? 'Posted' : 'Scheduled'}: {item.scheduledFor}
              </p>
            )}

            {item.engagement && (
              <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                <span className="flex items-center">
                  <Heart className="w-3 h-3 mr-1" />
                  {item.engagement.likes}
                </span>
                <span className="flex items-center">
                  <MessageCircle className="w-3 h-3 mr-1" />
                  {item.engagement.comments}
                </span>
                <span className="flex items-center">
                  <Share2 className="w-3 h-3 mr-1" />
                  {item.engagement.shares}
                </span>
              </div>
            )}

            <div className="flex space-x-2">
              <button className="flex-1 text-sm bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200 transition-colors">
                Edit
              </button>
              <button className="flex-1 text-sm bg-blue-100 text-blue-700 py-2 rounded-lg hover:bg-blue-200 transition-colors">
                View
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Analytics Page
const AnalyticsPage = () => {
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('engagement');

  const metrics = {
    '7d': {
      totalPosts: 24,
      totalEngagement: 8234,
      followerGrowth: 156,
      avgEngagementRate: 5.7,
      topPerformingPost: 'JavaScript tips that will blow your mind'
    },
    '30d': {
      totalPosts: 98,
      totalEngagement: 45678,
      followerGrowth: 892,
      avgEngagementRate: 6.2,
      topPerformingPost: 'React vs Vue comparison'
    }
  };

  const currentMetrics = metrics[timeRange];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600 mt-2">Track your social media performance</p>
        </div>
        <div className="flex items-center space-x-3">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="border border-gray-200 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
          </select>
          <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
        </div>
      </div>

      {/* Overview Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Posts</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{currentMetrics.totalPosts}</p>
            </div>
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-blue-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Total Engagement</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{currentMetrics.totalEngagement.toLocaleString()}</p>
            </div>
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Heart className="w-5 h-5 text-green-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Follower Growth</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">+{currentMetrics.followerGrowth}</p>
            </div>
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <Users className="w-5 h-5 text-purple-600" />
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">Avg Engagement Rate</p>
              <p className="text-2xl font-bold text-gray-900 mt-1">{currentMetrics.avgEngagementRate}%</p>
            </div>
            <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-orange-600" />
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Engagement Over Time</h3>
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Chart visualization would go here</p>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Performance</h3>
          <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
            <p className="text-gray-500">Platform breakdown chart would go here</p>
          </div>
        </div>
      </div>

      {/* Top Performing Content */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Performing Content</h3>
        <div className="space-y-3">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <p className="font-medium text-gray-900">{currentMetrics.topPerformingPost}</p>
              <p className="text-sm text-gray-600">Instagram • Posted 3 days ago</p>
            </div>
            <div className="text-right">
              <p className="font-medium text-gray-900">2,456 likes</p>
              <p className="text-sm text-green-600">+15.2% engagement</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Automation Page
const AutomationPage = () => {
  const [automationEnabled, setAutomationEnabled] = useState(true);
  const [postingFrequency, setPostingFrequency] = useState(3);
  const [contentApproval, setContentApproval] = useState(false);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Automation Settings</h1>
        <p className="text-gray-600 mt-2">Configure your AI-powered automation</p>
      </div>

      {/* Automation Status */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Automation Status</h3>
            <p className="text-gray-600">
              {automationEnabled ? 'AI is actively generating and posting content' : 'Automation is paused'}
            </p>
          </div>
          <button
            onClick={() => setAutomationEnabled(!automationEnabled)}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              automationEnabled
                ? 'bg-red-100 text-red-700 hover:bg-red-200'
                : 'bg-green-100 text-green-700 hover:bg-green-200'
            }`}
          >
            {automationEnabled ? 'Pause Automation' : 'Start Automation'}
          </button>
        </div>
      </div>

      {/* Settings */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Posting Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Posts per day: {postingFrequency}
              </label>
              <input
                type="range"
                min="1"
                max="10"
                value={postingFrequency}
                onChange={(e) => setPostingFrequency(e.target.value)}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Content Approval</p>
                <p className="text-sm text-gray-600">Review content before posting</p>
              </div>
              <button
                onClick={() => setContentApproval(!contentApproval)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                  contentApproval ? 'bg-blue-600' : 'bg-gray-200'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                    contentApproval ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Settings</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Content Style</label>
              <select className="w-full border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>Professional</option>
                <option>Casual</option>
                <option>Humorous</option>
                <option>Educational</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Creativity Level</label>
              <input
                type="range"
                min="1"
                max="10"
                defaultValue="7"
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>Conservative</span>
                <span>Creative</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Billing Page
const BillingPage = () => {
  const [currentPlan] = useState('pro');
  const [billingCycle, setBillingCycle] = useState('monthly');

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      price: { monthly: 29, yearly: 290 },
      features: ['5 platforms', '50 posts/month', 'Basic analytics', 'Email support']
    },
    {
      id: 'pro',
      name: 'Pro',
      price: { monthly: 79, yearly: 790 },
      features: ['15 platforms', '500 posts/month', 'Advanced analytics', 'Priority support', 'Team collaboration']
    },
    {
      id: 'agency',
      name: 'Agency',
      price: { monthly: 199, yearly: 1990 },
      features: ['Unlimited platforms', 'Unlimited posts', 'White-label', 'Dedicated manager', 'Custom integrations']
    }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Billing & Subscription</h1>
        <p className="text-gray-600 mt-2">Manage your subscription and billing details</p>
      </div>

      {/* Current Plan */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Plan</h3>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-2xl font-bold text-gray-900">Pro Plan</p>
            <p className="text-gray-600">$79/month • Next billing: Feb 15, 2024</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-600">Usage this month</p>
            <p className="text-lg font-semibold text-gray-900">342 / 500 posts</p>
          </div>
        </div>
      </div>

      {/* Billing Cycle Toggle */}
      <div className="flex items-center justify-center">
        <div className="bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setBillingCycle('monthly')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              billingCycle === 'monthly'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Monthly
          </button>
          <button
            onClick={() => setBillingCycle('yearly')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              billingCycle === 'yearly'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Yearly (2 months free)
          </button>
        </div>
      </div>

      {/* Plans */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`bg-white rounded-xl shadow-sm border-2 p-6 ${
              currentPlan === plan.id ? 'border-blue-500' : 'border-gray-200'
            }`}
          >
            <div className="text-center mb-6">
              <h3 className="text-lg font-semibold text-gray-900">{plan.name}</h3>
              <div className="mt-2">
                <span className="text-3xl font-bold text-gray-900">
                  ${plan.price[billingCycle]}
                </span>
                <span className="text-gray-600">/{billingCycle === 'monthly' ? 'month' : 'year'}</span>
              </div>
            </div>
            
            <ul className="space-y-3 mb-6">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-center text-sm text-gray-600">
                  <Check className="w-4 h-4 text-green-500 mr-2" />
                  {feature}
                </li>
              ))}
            </ul>

            <button
              className={`w-full py-3 rounded-lg font-medium transition-colors ${
                currentPlan === plan.id
                  ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
              disabled={currentPlan === plan.id}
            >
              {currentPlan === plan.id ? 'Current Plan' : 'Upgrade'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

// Settings Page
const SettingsPage = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'integrations', label: 'Integrations', icon: Globe }
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">Manage your account settings and preferences</p>
      </div>

      <div className="flex space-x-6">
        {/* Sidebar */}
        <div className="w-64">
          <nav className="space-y-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-3 py-2 text-left rounded-lg transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-50 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          {activeTab === 'profile' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Information</h3>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                    <input
                      type="text"
                      defaultValue="Aryan"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                    <input
                      type="text"
                      defaultValue="Patel"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                  <input
                    type="email"
                    defaultValue={user?.email}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
                  <textarea
                    rows="3"
                    placeholder="Tell us about yourself..."
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                  Save Changes
                </button>
              </div>
            </div>
          )}

          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Current Password</label>
                    <input
                      type="password"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">New Password</label>
                    <input
                      type="password"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Confirm New Password</label>
                    <input
                      type="password"
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Update Password
                  </button>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Two-Factor Authentication</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900">Enable 2FA</p>
                    <p className="text-sm text-gray-600">Add an extra layer of security to your account</p>
                  </div>
                  <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
                    Enable
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'notifications' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Notification Preferences</h3>
              <div className="space-y-4">
                {[
                  { label: 'Email notifications for new posts', desc: 'Get notified when content is published' },
                  { label: 'Push notifications for engagement', desc: 'Receive alerts for likes, comments, shares' },
                  { label: 'Weekly analytics reports', desc: 'Get weekly performance summaries' },
                  { label: 'Automation status updates', desc: 'Notifications when automation starts/stops' }
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <p className="font-medium text-gray-900">{item.label}</p>
                      <p className="text-sm text-gray-600">{item.desc}</p>
                    </div>
                    <button className="relative inline-flex h-6 w-11 items-center rounded-full bg-blue-600">
                      <span className="inline-block h-4 w-4 transform rounded-full bg-white translate-x-6 transition-transform" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'integrations' && (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Third-party Integrations</h3>
              <div className="space-y-4">
                {[
                  { name: 'Zapier', desc: 'Connect with 3000+ apps', status: 'connected' },
                  { name: 'Slack', desc: 'Get notifications in Slack', status: 'disconnected' },
                  { name: 'Google Analytics', desc: 'Track website traffic', status: 'disconnected' },
                  { name: 'Webhooks', desc: 'Custom API integrations', status: 'connected' }
                ].map((integration, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900">{integration.name}</p>
                      <p className="text-sm text-gray-600">{integration.desc}</p>
                    </div>
                    <button
                      className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                        integration.status === 'connected'
                          ? 'bg-red-100 text-red-700 hover:bg-red-200'
                          : 'bg-blue-600 text-white hover:bg-blue-700'
                      }`}
                    >
                      {integration.status === 'connected' ? 'Disconnect' : 'Connect'}
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Login Page
const LoginPage = () => {
  const { login } = useAuth();
  const { navigate } = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Zap className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">Welcome back</h2>
          <p className="mt-2 text-gray-600">Sign in to VelocityPost.ai</p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your email"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter your password"
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input type="checkbox" className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500" />
              <span className="ml-2 text-sm text-gray-600">Remember me</span>
            </label>
            <button
              type="button"
              onClick={() => navigate('/forgot-password')}
              className="text-sm text-blue-600 hover:text-blue-500"
            >
              Forgot password?
            </button>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign in'}
          </button>

          <div className="text-center">
            <span className="text-sm text-gray-600">Don't have an account? </span>
            <button
              type="button"
              onClick={() => navigate('/register')}
              className="text-sm text-blue-600 hover:text-blue-500 font-medium"
            >
              Sign up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Register Page
const RegisterPage = () => {
  const { login } = useAuth();
  const { navigate } = useRouter();
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirmPassword) {
      alert('Passwords do not match');
      return;
    }
    
    setLoading(true);
    try {
      await login(formData.email, formData.password);
      navigate('/dashboard');
    } catch (error) {
      console.error('Registration failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <div className="flex justify-center">
            <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
              <Zap className="w-8 h-8 text-white" />
            </div>
          </div>
          <h2 className="mt-6 text-3xl font-bold text-gray-900">Create your account</h2>
          <p className="mt-2 text-gray-600">Start automating your social media today</p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">First Name</label>
                <input
                  type="text"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Last Name</label>
                <input
                  type="text"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  required
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create account'}
          </button>

          <div className="text-center">
            <span className="text-sm text-gray-600">Already have an account? </span>
            <button
              type="button"
              onClick={() => navigate('/login')}
              className="text-sm text-blue-600 hover:text-blue-500 font-medium"
            >
              Sign in
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Main App Component
const App = () => {
  const { isAuthenticated } = useAuth();
  const { currentPath } = useRouter();

  const renderPage = () => {
    if (!isAuthenticated) {
      if (currentPath === '/register') return <RegisterPage />;
      return <LoginPage />;
    }

    switch (currentPath) {
      case '/dashboard':
        return <DashboardPage />;
      case '/platforms':
        return <PlatformsPage />;
      case '/domains':
        return <DomainsPage />;
      case '/content':
        return <ContentPage />;
      case '/analytics':
        return <AnalyticsPage />;
      case '/automation':
        return <AutomationPage />;
      case '/billing':
        return <BillingPage />;
      case '/settings':
        return <SettingsPage />;
      default:
        return <DashboardPage />;
    }
  };

  return (
    <div className="App">
      {isAuthenticated ? (
        <Layout>
          {renderPage()}
        </Layout>
      ) : (
        renderPage()
      )}
    </div>
  );
};

// Root Component
const VelocityPostApp = () => {
  return (
    <AuthProvider>
      <Router>
        <App />
      </Router>
    </AuthProvider>
  );
};

export default VelocityPostApp;