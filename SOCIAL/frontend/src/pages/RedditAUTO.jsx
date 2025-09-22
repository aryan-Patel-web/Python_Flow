import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

// Replace process.env with conditional import for Vite or fallback
const API_BASE_URL =
  (typeof import.meta !== 'undefined' && import.meta.env && import.meta.env.VITE_API_URL)
    ? import.meta.env.VITE_API_URL
    : (typeof process !== 'undefined' && process.env && process.env.REACT_APP_API_URL)
      ? process.env.REACT_APP_API_URL
      : 'https://agentic-u5lx.onrender.com';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }
  
  static getDerivedStateFromError(error) {
    return { hasError: true };
  }
  
  componentDidCatch(error, errorInfo) {
    console.error('Error Boundary caught an error:', error, errorInfo);
  }
  
  render() {
    if (this.state.hasError) {
      return <div style={{ padding: '20px', textAlign: 'center' }}>
        <h2>Something went wrong.</h2>
        <button onClick={() => this.setState({ hasError: false })}>Try again</button>
      </div>;
    }
    return this.props.children;
  }
}

const RedditAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [backendConnected, setBackendConnected] = useState(false);
  const [redditConnected, setRedditConnected] = useState(false);
  const [redditUsername, setRedditUsername] = useState('');
  const [connectionError, setConnectionError] = useState('');
  
  const [userProfile, setUserProfile] = useState({
    domain: 'tech',
    businessType: 'AI automation platform',
    businessDescription: 'We help businesses automate their social media presence',
    targetAudience: 'tech_professionals',
    contentStyle: 'engaging',
    isConfigured: false
  });

  const [manualPost, setManualPost] = useState({
    subreddit: 'test',
    title: '',
    content: '',
    isGenerating: false
  });

  const [autoPostConfig, setAutoPostConfig] = useState({
    enabled: false,
    postsPerDay: 3,
    postingTimes: [],
    subreddits: ['test']
  });

  const [performanceData, setPerformanceData] = useState({
    postsToday: 0,
    totalKarma: 0,
    successRate: 95
  });

  const domainConfigs = {
    education: { 
      subreddits: ['test', 'IndianStudents', 'learnprogramming', 'programming'], 
      sampleBusiness: 'JEE coaching institute', 
      icon: '🎓', 
      description: 'Educational services' 
    },
    restaurant: { 
      subreddits: ['test', 'IndianFood', 'food', 'cooking'], 
      sampleBusiness: 'Traditional Indian restaurant', 
      icon: '🍽️', 
      description: 'Food & restaurants' 
    },
    tech: { 
      subreddits: ['test', 'developersIndia', 'learnprogramming', 'programming'], 
      sampleBusiness: 'AI automation platform', 
      icon: '💻', 
      description: 'Technology & programming' 
    },
    health: { 
      subreddits: ['test', 'fitness', 'nutrition', 'bodyweightfitness'], 
      sampleBusiness: 'Fitness coaching center', 
      icon: '💚', 
      description: 'Health & wellness' 
    },
    business: { 
      subreddits: ['test', 'entrepreneur', 'smallbusiness', 'startups'], 
      sampleBusiness: 'Business consulting firm', 
      icon: '💼', 
      description: 'Business & entrepreneurship' 
    }
  };

  const targetAudienceOptions = {
    'indian_students': { label: 'Indian Students', icon: '🎓' },
    'food_lovers': { label: 'Food Lovers', icon: '🍕' },
    'tech_professionals': { label: 'Tech Professionals', icon: '💻' },
    'health_conscious': { label: 'Health Conscious', icon: '💚' },
    'entrepreneurs': { label: 'Entrepreneurs', icon: '💼' },
    'general_users': { label: 'General Users', icon: '👥' }
  };

  const contentStyleOptions = {
    'engaging': 'Engaging & Interactive',
    'informative': 'Informative & Educational', 
    'promotional': 'Promotional & Marketing',
    'helpful': 'Helpful & Supportive',
    'casual': 'Casual & Friendly',
    'professional': 'Professional & Formal'
  };

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { 
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      message, 
      type 
    };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  }, []);




// TEMPORARY DEBUG - Add this after your state declarations
useEffect(() => {
  console.log('=== REDDIT STATE DEBUG ===');
  console.log('redditConnected:', redditConnected);
  console.log('redditUsername:', redditUsername);
  console.log('user:', user);
  console.log('makeAuthenticatedRequest available:', !!makeAuthenticatedRequest);
  
  // Check URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  console.log('URL params:');
  console.log('- reddit_connected:', urlParams.get('reddit_connected'));
  console.log('- username:', urlParams.get('username'));
  console.log('- error:', urlParams.get('error'));
}, [redditConnected, redditUsername, user, makeAuthenticatedRequest]);


// Initialize app state - FIXED VERSION
// Initialize app state - FIXED VERSION
// Initialize app state - FIXED VERSION
useEffect(() => {
  const initApp = async () => {
    // Only run for authenticated users
    if (!user?.email || user.email.includes('mock')) {
      console.log('Skipping init - no user or mock user');
      return;
    }

    // TEMPORARILY CLEAR INIT FLAG TO FORCE CONNECTION CHECK
    const initKey = `reddit_init_${user.email}`;
    localStorage.removeItem(initKey); // ADD THIS LINE TO FORCE REFRESH
    
    if (localStorage.getItem(initKey)) {
      console.log('Already initialized for', user.email);
      return;
    }

    try {
      console.log('🚀 Initializing Reddit Auto component for user:', user.email);
      localStorage.setItem(initKey, 'true');

      // Handle OAuth callback first
      const urlParams = new URLSearchParams(window.location.search);
      const redditConnectedParam = urlParams.get('reddit_connected');
      const usernameParam = urlParams.get('username');
      const errorParam = urlParams.get('error');

      if (errorParam) {
        console.error('OAuth error:', errorParam);
        showNotification(`Connection failed: ${errorParam}`, 'error');
        window.history.replaceState({}, '', window.location.pathname);
        return;
      }

      if (redditConnectedParam === 'true' && usernameParam) {
        console.log('✅ Reddit OAuth success:', { username: usernameParam });
        setRedditUsername(usernameParam);
        setRedditConnected(true);
        updateUser({
          reddit_connected: true,
          reddit_username: usernameParam
        });
        showNotification(`Reddit connected! Welcome u/${usernameParam}!`, 'success');
        window.history.replaceState({}, '', window.location.pathname);
        
        // Force check connection status after OAuth
        setTimeout(async () => {
          try {
            console.log('Making OAuth verification request...');
            const response = await makeAuthenticatedRequest('/api/reddit/connection-status');
            const result = await response.json();
            console.log('OAuth verification result:', result);
            if (result.success && result.connected) {
              setRedditConnected(true);
              setRedditUsername(result.reddit_username);
              console.log('✅ OAuth connection confirmed via API');
            }
          } catch (error) {
            console.error('Failed to verify OAuth connection:', error);
          }
        }, 1000);
        return;
      }

      // Check existing Reddit connection status
      console.log('Checking existing Reddit connection...');
      try {
        const response = await makeAuthenticatedRequest('/api/reddit/connection-status');
        console.log('Connection check response status:', response.status);
        const result = await response.json();
        console.log('Connection check result:', result);
        
        if (result.success && result.connected && result.reddit_username) {
          setRedditConnected(true);
          setRedditUsername(result.reddit_username);
          updateUser({
            reddit_connected: true,
            reddit_username: result.reddit_username
          });
          console.log('✅ Existing Reddit connection verified:', result.reddit_username);
        } else {
          setRedditConnected(false);
          setRedditUsername('');
          console.log('❌ No Reddit connection found', result);
        }
      } catch (error) {
        console.error('Failed to check Reddit connection:', error);
        setRedditConnected(false);
        setRedditUsername('');
      }

      // Load saved profile







      // Load saved profile
      try {
        const savedProfile = localStorage.getItem('redditUserProfile');
        if (savedProfile) {
          const profile = JSON.parse(savedProfile);
          setUserProfile(profile);
        }
      } catch (error) {
        console.error('Error loading profile:', error);
      }

      // Test backend connection
      try {
        const healthResponse = await makeAuthenticatedRequest('/health');
        const healthData = await healthResponse.json();
        if (healthData.success || healthData.status === 'healthy') {
          setBackendConnected(true);
          console.log('✅ Backend connection verified');
        }
      } catch (error) {
        console.error('Backend connection failed:', error);
        setBackendConnected(false);
      }
      
    } catch (error) {
      console.error('App initialization failed:', error);
      showNotification('App initialization failed', 'error');
    }
  };

  // Only initialize when user changes and is authenticated
  if (user?.email && !user.email.includes('mock')) {
    initApp();
  }
}, [user?.email, makeAuthenticatedRequest, updateUser, showNotification]);

  const saveUserProfile = useCallback(() => {
    try {
      const profileToSave = { ...userProfile, isConfigured: true };
      localStorage.setItem('redditUserProfile', JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('Profile saved successfully!', 'success');
      
      const domainConfig = domainConfigs[profileToSave.domain];
      if (domainConfig) {
        setAutoPostConfig(prev => ({
          ...prev,
          subreddits: domainConfig.subreddits.slice(0, 3)
        }));
      }
    } catch (error) {
      showNotification('Failed to save profile', 'error');
    }
  }, [userProfile, showNotification]);

  const handleRedditConnect = useCallback(async () => {
    try {
      setLoading(true);
      showNotification('Connecting to Reddit...', 'info');
      
      console.log('🔗 Starting Reddit OAuth for user:', user?.email);

      const response = await makeAuthenticatedRequest('/api/oauth/reddit/authorize');
      const result = await response.json();
      
      if (result.success && result.redirect_url) {
        console.log('✅ Redirecting to Reddit OAuth:', result.redirect_url);
        window.location.href = result.redirect_url;
      } else {
        console.error('❌ OAuth authorization failed:', result);
        showNotification(result.error || 'Failed to start Reddit authorization', 'error');
      }
    } catch (error) {
      console.error('❌ Connection error:', error);
      showNotification('Connection failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAuthenticatedRequest, user, showNotification]);

  const testConnection = useCallback(async () => {
    try {
      setLoading(true);
      const response = await makeAuthenticatedRequest('/api/reddit/test-connection');
      const result = await response.json();
      
      if (result.success) {
        showNotification(`Connection test successful for ${result.username}!`, 'success');
      } else {
        showNotification('Connection test failed: ' + result.error, 'error');
      }
    } catch (error) {
      showNotification('Test failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAuthenticatedRequest, showNotification]);

  const generateContent = useCallback(async () => {
    if (!userProfile.businessType) {
      showNotification('Please configure your profile first', 'error');
      return;
    }

    try {
      setManualPost(prev => ({ ...prev, isGenerating: true }));
      showNotification('Generating content with REAL AI...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/test-auto-post', {
        method: 'POST',
        body: JSON.stringify({
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          language: userProfile.language,
          subreddits: [manualPost.subreddit],
          content_style: userProfile.contentStyle
        })
      });

      const result = await response.json();

      if (result.success) {
        setManualPost(prev => ({
          ...prev,
          title: result.post_details?.title || 'Generated Title',
          content: result.content_preview
        }));
        showNotification(`Content generated using ${result.ai_service}!`, 'success');
      } else {
        showNotification(result.error || 'AI content generation failed', 'error');
      }
    } catch (error) {
      showNotification('AI generation failed: ' + error.message, 'error');
    } finally {
      setManualPost(prev => ({ ...prev, isGenerating: false }));
    }
  }, [userProfile, manualPost.subreddit, makeAuthenticatedRequest, showNotification]);

  const handleManualPost = useCallback(async (e) => {
    e.preventDefault();
    
    if (!manualPost.title || !manualPost.content) {
      showNotification('Please enter both title and content', 'error');
      return;
    }

    if (!redditConnected) {
      showNotification('Please connect your Reddit account first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Posting to Reddit...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/reddit/post', {
        method: 'POST',
        body: JSON.stringify({
          subreddit: manualPost.subreddit,
          title: manualPost.title,
          content: manualPost.content,
          contentType: 'text'
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        showNotification(`Post created successfully as ${redditUsername}!`, 'success');
        if (result.post_url) {
          showNotification(`View post: ${result.post_url}`, 'info');
        }
        
        setPerformanceData(prev => ({
          ...prev,
          postsToday: prev.postsToday + 1
        }));
        
        setManualPost({
          subreddit: 'test',
          title: '',
          content: '',
          isGenerating: false
        });
      } else {
        showNotification(result.error || 'Posting failed', 'error');
      }
    } catch (error) {
      showNotification('Posting failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [manualPost, makeAuthenticatedRequest, redditUsername, redditConnected, showNotification]);

  const startAutoPosting = useCallback(async () => {
    if (!userProfile.isConfigured) {
      showNotification('Please configure your profile first', 'error');
      setActiveTab('setup');
      return;
    }

    if (!redditConnected) {
      showNotification('Please connect your Reddit account first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Setting up REAL automation...', 'info');
      
      const config = {
        domain: userProfile.domain,
        business_type: userProfile.businessType,
        business_description: userProfile.businessDescription,
        target_audience: userProfile.targetAudience,
        language: userProfile.language,
        subreddits: autoPostConfig.subreddits,
        posts_per_day: autoPostConfig.postsPerDay,
        posting_times: autoPostConfig.postingTimes,
        content_style: userProfile.contentStyle
      };

      const response = await makeAuthenticatedRequest('/api/automation/setup-auto-posting', {
        method: 'POST',
        body: JSON.stringify(config)
      });
      
      const result = await response.json();
      
      if (result.success) {
        setAutoPostConfig(prev => ({ ...prev, enabled: true }));
        showNotification(`Auto-posting started for ${redditUsername}!`, 'success');
        if (result.next_post_time) {
          showNotification(`Next post: ${result.next_post_time}`, 'info');
        }
      } else {
        showNotification(result.error || 'Automation setup failed', 'error');
      }
    } catch (error) {
      showNotification('Setup failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [userProfile, redditConnected, autoPostConfig, makeAuthenticatedRequest, redditUsername, showNotification]);

  const addTestTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 2);
    const testTime = now.toTimeString().slice(0, 5);
    if (!autoPostConfig.postingTimes.includes(testTime)) {
      setAutoPostConfig(prev => ({
        ...prev,
        postingTimes: [...prev.postingTimes, testTime].sort()
      }));
      showNotification('Test time added (+2 minutes)', 'info');
    }
  };

  return (
    <div style={{ 
      fontFamily: 'system-ui, -apple-system, sans-serif',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      display: 'flex'
    }}>
      {/* Notifications */}
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 10000, display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}>
        {notifications.map(notification => (
          <div 
            key={notification.id}
            style={{
              padding: '16px 20px',
              borderRadius: '12px',
              backdropFilter: 'blur(10px)',
              color: 'white',
              fontWeight: '500',
              boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
              background: notification.type === 'success' ? 'rgba(34, 197, 94, 0.9)' :
                         notification.type === 'error' ? 'rgba(239, 68, 68, 0.9)' :
                         'rgba(59, 130, 246, 0.9)',
              borderLeft: `4px solid ${notification.type === 'success' ? '#22c55e' : notification.type === 'error' ? '#ef4444' : '#3b82f6'}`,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              gap: '12px'
            }}
          >
            <span>{notification.message}</span>
            <button 
              onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
              style={{ background: 'none', border: 'none', color: 'white', fontSize: '18px', cursor: 'pointer', padding: '4px' }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(5px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999 }}>
          <div style={{ background: 'white', padding: '40px', borderRadius: '16px', textAlign: 'center', boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)' }}>
            <div style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #667eea', borderRadius: '50%', width: '40px', height: '40px', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
            <p style={{ marginTop: '16px', color: '#666' }}>Processing...</p>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div style={{ width: '280px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', height: '100vh', position: 'fixed', display: 'flex', flexDirection: 'column', boxShadow: '2px 0 20px rgba(0, 0, 0, 0.1)' }}>
        <div style={{ padding: '32px 24px', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', textAlign: 'center', background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
          <h2 style={{ fontSize: '24px', fontWeight: '700', color: 'white', margin: 0, marginBottom: '4px' }}>Reddit Auto</h2>
          <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Welcome, {user?.name}</div>
        </div>
        
        <nav style={{ flex: 1, padding: '24px 16px' }}>
          {[
            { id: 'setup', icon: '⚙️', label: 'Setup' },
            { id: 'manual', icon: '✍️', label: 'Manual Post' },
            { id: 'schedule', icon: '📅', label: 'Schedule' },
            { id: 'status', icon: '📈', label: 'Status' }
          ].map(tab => (
            <button 
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '16px 20px',
                border: 'none',
                background: activeTab === tab.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'none',
                color: activeTab === tab.id ? 'white' : '#666',
                textAlign: 'left',
                borderRadius: '12px',
                cursor: 'pointer',
                marginBottom: '8px',
                fontSize: '16px',
                transform: activeTab === tab.id ? 'translateX(4px)' : 'none',
                boxShadow: activeTab === tab.id ? '0 4px 15px rgba(102, 126, 234, 0.4)' : 'none'
              }}
            >
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>


        








{/* Reddit Connection Section - No Mock Data */}
        <div style={{ 
          padding: '20px 24px', 
          borderTop: '1px solid rgba(0, 0, 0, 0.05)',
          background: 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(240,240,255,0.05))',
          backdropFilter: 'blur(10px)'
        }}>
          {redditConnected ? (
            <div>
              {/* Connected Status Card */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '16px 20px',
                borderRadius: '12px',
                fontSize: '15px',
                fontWeight: '600',
                background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.1))',
                color: '#047857',
                border: '2px solid rgba(34, 197, 94, 0.3)',
                boxShadow: '0 4px 20px rgba(34, 197, 94, 0.15)',
                marginBottom: '12px'
              }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                  borderRadius: '50%',
                  boxShadow: '0 0 8px rgba(34, 197, 94, 0.5)',
                  animation: 'pulse 2s infinite'
                }}></div>
                <span style={{ 
                  fontSize: '16px',
                  textShadow: '0 1px 2px rgba(0,0,0,0.1)'
                }}>✅ Reddit Connected</span>
              </div>
              
              {/* Real Username Display */}
              {redditUsername && (
                <div style={{ 
                  fontSize: '13px', 
                  color: '#059669',
                  fontWeight: '500',
                  margin: '0 0 16px 32px',
                  fontFamily: 'monospace',
                  background: 'rgba(34, 197, 94, 0.08)',
                  padding: '6px 12px',
                  borderRadius: '20px',
                  display: 'inline-block'
                }}>
                  u/{redditUsername}
                </div>
              )}
              
              {/* Test Connection Button */}
              <button 
                onClick={testConnection}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  fontSize: '13px',
                  fontWeight: '600',
                  background: loading ? 
                    'linear-gradient(135deg, #d1d5db, #9ca3af)' : 
                    'linear-gradient(135deg, #22c55e, #16a34a)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '10px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  boxShadow: loading ? 
                    'none' : 
                    '0 4px 15px rgba(34, 197, 94, 0.3)',
                  transform: loading ? 'none' : 'translateY(0)',
                  transition: 'all 0.3s ease',
                  textShadow: '0 1px 2px rgba(0,0,0,0.2)'
                }}
                onMouseOver={(e) => {
                  if (!loading) {
                    e.target.style.transform = 'translateY(-1px)';
                    e.target.style.boxShadow = '0 6px 20px rgba(34, 197, 94, 0.4)';
                  }
                }}
                onMouseOut={(e) => {
                  if (!loading) {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 4px 15px rgba(34, 197, 94, 0.3)';
                  }
                }}
              >
                {loading ? 'Testing...' : '🔍 Test Connection'}
              </button>
            </div>
          ) : (
            <div>
              {/* Disconnected Status Card */}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '16px 20px',
                borderRadius: '12px',
                fontSize: '15px',
                fontWeight: '600',
                background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.1))',
                color: '#dc2626',
                border: '2px solid rgba(239, 68, 68, 0.3)',
                boxShadow: '0 4px 20px rgba(239, 68, 68, 0.15)',
                marginBottom: '12px'
              }}>
                <div style={{
                  width: '12px',
                  height: '12px',
                  background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                  borderRadius: '50%',
                  boxShadow: '0 0 8px rgba(239, 68, 68, 0.5)',
                  animation: 'pulse 2s infinite'
                }}></div>
                <span style={{ 
                  fontSize: '16px',
                  textShadow: '0 1px 2px rgba(0,0,0,0.1)'
                }}>❌ Reddit Not Connected</span>
              </div>
              
              {/* Connection Required Message */}
              <div style={{
                fontSize: '12px',
                color: '#dc2626',
                textAlign: 'center',
                marginBottom: '16px',
                padding: '8px 12px',
                background: 'rgba(239, 68, 68, 0.08)',
                borderRadius: '8px',
                border: '1px dashed rgba(239, 68, 68, 0.3)'
              }}>
                🔐 One-time Reddit authorization required
              </div>
              
              {/* Connect Button - Extra Highlighted */}
              <button 
                onClick={handleRedditConnect} 
                disabled={loading}
                style={{
                  width: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '12px',
                  padding: '16px 20px',
                  fontSize: '16px',
                  fontWeight: '700',
                  background: loading ? 
                    'linear-gradient(135deg, #d1d5db, #9ca3af)' : 
                    'linear-gradient(135deg, #ef4444, #dc2626)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '12px',
                  cursor: loading ? 'not-allowed' : 'pointer',
                  boxShadow: loading ? 
                    'none' : 
                    '0 6px 25px rgba(239, 68, 68, 0.4)',
                  transform: loading ? 'none' : 'translateY(0)',
                  transition: 'all 0.3s ease',
                  textShadow: '0 1px 2px rgba(0,0,0,0.3)',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseOver={(e) => {
                  if (!loading) {
                    e.target.style.transform = 'translateY(-2px) scale(1.02)';
                    e.target.style.boxShadow = '0 8px 30px rgba(239, 68, 68, 0.5)';
                  }
                }}
                onMouseOut={(e) => {
                  if (!loading) {
                    e.target.style.transform = 'translateY(0) scale(1)';
                    e.target.style.boxShadow = '0 6px 25px rgba(239, 68, 68, 0.4)';
                  }
                }}
              >
                {/* Animated Glow Effect */}
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: '-100%',
                  width: '100%',
                  height: '100%',
                  background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent)',
                  animation: loading ? 'none' : 'shimmer 3s infinite',
                  zIndex: 1
                }}></div>
                
                <span style={{ fontSize: '20px', zIndex: 2 }}>🔗</span>
                <span style={{ zIndex: 2 }}>
                  {loading ? 'Connecting...' : 'Connect Reddit Account'}
                </span>
              </button>
              
              {/* Help Text */}
              <div style={{
                fontSize: '11px',
                color: '#6b7280',
                textAlign: 'center',
                marginTop: '10px',
                lineHeight: '1.4'
              }}>
                Safe OAuth connection • No password required
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}




      
      <div style={{ flex: 1, marginLeft: '280px', background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
        <header style={{ padding: '32px 40px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '8px' }}>Reddit Automation Dashboard</h1>
            <p style={{ fontSize: '16px', color: '#666' }}>AI-powered Reddit automation for {redditUsername || user?.name || 'your account'}</p>
            <div style={{ fontSize: '12px', color: '#95a5a6', display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
              Status: {backendConnected ? 'Live Backend' : 'Offline'}
            </div>
          </div>
          
          <div>
            {userProfile.isConfigured && (
              <button 
                onClick={startAutoPosting}
                disabled={loading || !redditConnected}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  padding: '16px 32px',
                  border: 'none',
                  borderRadius: '12px',
                  fontSize: '16px',
                  fontWeight: '600',
                  cursor: loading || !redditConnected ? 'not-allowed' : 'pointer',
                  background: loading || !redditConnected ? '#bdc3c7' : 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white',
                  boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)'
                }}
              >
                <span>🚀</span>
                <span>Start Auto-Post</span>
              </button>
            )}
          </div>
        </header>

        {/* Tab Content */}
        <div style={{ padding: '32px 40px' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', borderRadius: '20px', padding: '32px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)', border: '1px solid rgba(255, 255, 255, 0.2)', maxWidth: '1000px', margin: '0 auto' }}>
            
            {activeTab === 'setup' && (
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#333', marginBottom: '32px' }}>Profile Configuration</h2>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                  <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Business Domain</label>
                  <select 
                    value={userProfile.domain}
                    onChange={(e) => {
                      const domain = e.target.value;
                      const config = domainConfigs[domain];
                      setUserProfile(prev => ({
                        ...prev,
                        domain,
                        businessType: config?.sampleBusiness || prev.businessType
                      }));
                    }}
                    style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}
                  >
                    {Object.entries(domainConfigs).map(([key, config]) => (
                      <option key={key} value={key}>
                        {config.icon} {config.description}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                  <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Business Type</label>
                  <input
                    type="text"
                    value={userProfile.businessType}
                    onChange={(e) => setUserProfile(prev => ({ ...prev, businessType: e.target.value }))}
                    placeholder={domainConfigs[userProfile.domain]?.sampleBusiness}
                    style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}
                  />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                  <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Business Description</label>
                  <textarea
                    value={userProfile.businessDescription}
                    onChange={(e) => setUserProfile(prev => ({ ...prev, businessDescription: e.target.value }))}
                    placeholder="Describe your business or service..."
                    rows="3"
                    style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white', resize: 'vertical' }}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Target Audience</label>
                    <select 
                      value={userProfile.targetAudience}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, targetAudience: e.target.value }))}
                      style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}
                    >
                      {Object.entries(targetAudienceOptions).map(([key, option]) => (
                        <option key={key} value={key}>
                          {option.icon} {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Content Style</label>
                    <select 
                      value={userProfile.contentStyle}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, contentStyle: e.target.value }))}
                      style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}
                    >
                      {Object.entries(contentStyleOptions).map(([key, style]) => (
                        <option key={key} value={key}>
                          {style}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div style={{ textAlign: 'center', marginTop: '32px' }}>
                  <button 
                    onClick={saveUserProfile}
                    disabled={!userProfile.businessType}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '12px',
                      padding: '16px 32px',
                      border: 'none',
                      borderRadius: '12px',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: userProfile.businessType ? 'pointer' : 'not-allowed',
                      background: userProfile.businessType ? 'linear-gradient(135deg, #667eea, #764ba2)' : '#bdc3c7',
                      color: 'white',
                      boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)',
                      margin: '0 auto'
                    }}
                  >
                    Save Configuration
                  </button>
                </div>

                {userProfile.isConfigured && (
                  <div style={{
                    marginTop: '20px',
                    padding: '15px',
                    backgroundColor: '#d4edda',
                    borderRadius: '12px',
                    border: '1px solid #c3e6cb'
                  }}>
                    <div style={{ color: '#155724', fontWeight: 'bold', marginBottom: '5px' }}>
                      Profile Configured Successfully
                    </div>
                    <div style={{ color: '#155724', fontSize: '14px' }}>
                      Ready for manual posting and automation setup.
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Manual Post Tab */}
            {activeTab === 'manual' && (
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#333', marginBottom: '32px' }}>Manual Posting with AI</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '20px', marginBottom: '20px', alignItems: 'end' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Subreddit</label>
                    <select
                      value={manualPost.subreddit}
                      onChange={(e) => setManualPost(prev => ({ ...prev, subreddit: e.target.value }))}
                      style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}
                    >
                      {domainConfigs[userProfile.domain]?.subreddits.map(sub => (
                        <option key={sub} value={sub}>r/{sub}</option>
                      ))}
                    </select>
                  </div>

                  <button 
                    onClick={generateContent}
                    disabled={manualPost.isGenerating || !userProfile.isConfigured}
                    style={{
                      padding: '16px 32px',
                      border: 'none',
                      borderRadius: '12px',
                      fontSize: '16px',
                      fontWeight: '600',
                      cursor: (manualPost.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer',
                      background: (manualPost.isGenerating || !userProfile.isConfigured) ? '#bdc3c7' : 'linear-gradient(135deg, #667eea, #764ba2)',
                      color: 'white',
                      boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)'
                    }}
                  >
                    {manualPost.isGenerating ? 'Generating...' : 'Generate with AI'}
                  </button>
                </div>

                <form onSubmit={handleManualPost}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Post Title</label>
                    <input
                      type="text"
                      value={manualPost.title}
                      onChange={(e) => setManualPost(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="Enter your post title..."
                      style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}
                      required
                    />
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Post Content</label>
                    <textarea
                      value={manualPost.content}
                      onChange={(e) => setManualPost(prev => ({ ...prev, content: e.target.value }))}
                      placeholder="Enter your post content..."
                      rows="8"
                      style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white', resize: 'vertical' }}
                      required
                    />
                  </div>

                  <div style={{ textAlign: 'center' }}>
                    <button 
                      type="submit" 
                      disabled={loading || !redditConnected || !manualPost.title || !manualPost.content}
                      style={{
                        padding: '16px 32px',
                        border: 'none',
                        borderRadius: '12px',
                        fontSize: '16px',
                        fontWeight: '600',
                        cursor: (loading || !redditConnected || !manualPost.title || !manualPost.content) ? 'not-allowed' : 'pointer',
                        background: (loading || !redditConnected || !manualPost.title || !manualPost.content) ? '#bdc3c7' : 'linear-gradient(135deg, #34d399, #10b981)',
                        color: 'white',
                        boxShadow: '0 4px 15px rgba(52, 211, 153, 0.3)'
                      }}
                    >
                      {loading ? 'Posting...' : `Post as ${redditUsername || user?.name || 'Reddit User'}`}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Schedule Tab */}
            {activeTab === 'schedule' && (
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#333', marginBottom: '32px' }}>Auto-Post Schedule</h2>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                  <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Posts Per Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={autoPostConfig.postsPerDay}
                    onChange={(e) => setAutoPostConfig(prev => ({ ...prev, postsPerDay: parseInt(e.target.value) || 1 }))}
                    style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white', width: '200px' }}
                  />
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <h4 style={{ marginBottom: '16px' }}>Posting Times</h4>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
                    <input
                      type="time"
                      onChange={(e) => {
                        if (e.target.value && !autoPostConfig.postingTimes.includes(e.target.value)) {
                          setAutoPostConfig(prev => ({
                            ...prev,
                            postingTimes: [...prev.postingTimes, e.target.value].sort()
                          }));
                        }
                      }}
                      style={{ padding: '8px 12px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '6px', fontSize: '14px' }}
                    />
                    <button
                      onClick={addTestTime}
                      type="button"
                      style={{
                        padding: '10px 16px',
                        backgroundColor: '#f59e0b',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '14px',
                        cursor: 'pointer'
                      }}
                    >
                      Add Test Time (+2min)
                    </button>
                  </div>

                  {autoPostConfig.postingTimes.length > 0 && (
                    <div>
                      <h5 style={{ marginTop: '20px', marginBottom: '12px' }}>
                        Scheduled Times ({autoPostConfig.postingTimes.length})
                      </h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {autoPostConfig.postingTimes.map(time => (
                          <div 
                            key={time} 
                            style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              padding: '6px 12px',
                              background: 'white',
                              border: '1px solid rgba(34, 197, 94, 0.3)',
                              borderRadius: '16px',
                              color: '#16a34a',
                              fontSize: '14px',
                              fontWeight: '500'
                            }}
                          >
                            <span>{time}</span>
                            <button 
                              onClick={() => setAutoPostConfig(prev => ({
                                ...prev,
                                postingTimes: prev.postingTimes.filter(t => t !== time)
                              }))}
                              style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '16px', cursor: 'pointer' }}
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                <div>
                  <h4 style={{ marginBottom: '16px' }}>Target Subreddits</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '12px' }}>
                    {(domainConfigs[userProfile.domain]?.subreddits || ['test']).map(sub => (
                      <label 
                        key={sub} 
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          padding: '12px 16px',
                          background: 'white',
                          border: '2px solid #e5e7eb',
                          borderRadius: '8px',
                          cursor: 'pointer'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={autoPostConfig.subreddits.includes(sub)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setAutoPostConfig(prev => ({ ...prev, subreddits: [...prev.subreddits, sub] }));
                            } else {
                              setAutoPostConfig(prev => ({ ...prev, subreddits: prev.subreddits.filter(s => s !== sub) }));
                            }
                          }}
                        />
                        <span>r/{sub}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Status Tab */}
            {activeTab === 'status' && (
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#333', marginBottom: '32px' }}>System Status & Analytics</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)' }}>
                    <h3 style={{ marginTop: 0 }}>Reddit Connection</h3>
                    <div style={{
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      backgroundColor: redditConnected ? '#d4edda' : '#f8d7da',
                      color: redditConnected ? '#155724' : '#721c24',
                      display: 'inline-block'
                    }}>
                      {redditConnected ? 'Connected' : 'Disconnected'}
                    </div>
                    {redditUsername && (
                      <p style={{ margin: '10px 0 0 0', color: '#666' }}>
                        Connected as: u/{redditUsername}
                      </p>
                    )}
                  </div>

                  <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)' }}>
                    <h3 style={{ marginTop: 0 }}>Profile Status</h3>
                    <div style={{
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      backgroundColor: userProfile.isConfigured ? '#d4edda' : '#f8d7da',
                      color: userProfile.isConfigured ? '#155724' : '#721c24',
                      display: 'inline-block'
                    }}>
                      {userProfile.isConfigured ? 'Configured' : 'Not Configured'}
                    </div>
                    {userProfile.isConfigured && (
                      <p style={{ margin: '10px 0 0 0', color: '#666' }}>
                        Domain: {userProfile.domain}
                      </p>
                    )}
                  </div>

                  <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)' }}>
                    <h3 style={{ marginTop: 0 }}>Automation Status</h3>
                    <div style={{
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 'bold',
                      backgroundColor: autoPostConfig.enabled ? '#d4edda' : '#f8d7da',
                      color: autoPostConfig.enabled ? '#155724' : '#721c24',
                      display: 'inline-block'
                    }}>
                      {autoPostConfig.enabled ? 'Active' : 'Inactive'}
                    </div>
                    {autoPostConfig.enabled && (
                      <p style={{ margin: '10px 0 0 0', color: '#666' }}>
                        {autoPostConfig.postsPerDay} posts/day, {autoPostConfig.postingTimes.length} time slots
                      </p>
                    )}
                  </div>
                </div>

                <div style={{ 
                  padding: '20px', 
                  backgroundColor: '#f8f9fa', 
                  borderRadius: '12px'
                }}>
                  <h3 style={{ marginTop: 0 }}>Performance Metrics</h3>
                  <div style={{ 
                    display: 'grid', 
                    gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', 
                    gap: '20px',
                    textAlign: 'center'
                  }}>
                    <div>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#22c55e' }}>
                        {performanceData.postsToday}
                      </div>
                      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Posts Today</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#3b82f6' }}>
                        {performanceData.totalKarma}
                      </div>
                      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Total Karma</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#f59e0b' }}>
                        {performanceData.successRate}%
                      </div>
                      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Success Rate</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <RedditAutomation />
    </ErrorBoundary>
  );
}