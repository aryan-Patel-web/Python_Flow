import React, { useState, useEffect, useCallback } from 'react';
// Add this near the top of your component
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://agentic-u5lx.onrender.com';
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
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [backendConnected, setBackendConnected] = useState(false);
  const [redditConnected, setRedditConnected] = useState(false);
  const [redditUsername, setRedditUsername] = useState('');
  const [sessionId, setSessionId] = useState(null);
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




  // FIXED: Enhanced API request with session recovery


  const makeAPIRequest = useCallback(async (endpoint, method = 'GET', data = null) => {
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (sessionId) {
        headers['x-session-id'] = sessionId;
      }

      const config = { method, headers };
      if (data && method !== 'GET') {
        config.body = JSON.stringify({ ...data, use_real_ai: true, test_mode: false });
      }

      const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
      const result = await response.json();
      
      if (response.ok && result.success !== false) {
        setBackendConnected(true);
        setConnectionError('');
        return result;
      } else {
        // Handle authentication errors
        if (result.error === "User authentication required") {
          await recoverSession();
        }
        return result;
      }
    } catch (error) {
      setBackendConnected(false);
      setConnectionError('Backend not available');
      return { success: false, error: error.message };
    }
  }, [sessionId]);

  // FIXED: Session recovery function
  const recoverSession = useCallback(async () => {
    try {
      console.log('🔄 Session recovery started...');
      
      // Check backend session state
      const debugResponse = await fetch(`${API_BASE_URL}/api/debug/sessions`);
      const debugData = await debugResponse.json();
      
      // If our session doesn't exist, create new one
      if (sessionId && !debugData.user_sessions[sessionId]) {
        console.log('❌ Session lost, creating new session...');
        
        const response = await fetch(`${API_BASE_URL}/api/auth/create-session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        
        const result = await response.json();
        if (result.success) {
          setSessionId(result.session_id);
          localStorage.setItem('reddit_session_id', result.session_id);
          
          // Reset Reddit connection state
          setRedditConnected(false);
          setRedditUsername('');
          localStorage.removeItem('reddit_username');
          showNotification('Session recovered - please reconnect Reddit', 'info');
        }
      }
    } catch (error) {
      console.error('Session recovery failed:', error);
    }
  }, [sessionId, showNotification]);

  // FIXED: Initialize app with better session handling
  useEffect(() => {
    const initApp = async () => {
      try {
        // Handle OAuth callback first
        const urlParams = new URLSearchParams(window.location.search);
        const redditConnectedParam = urlParams.get('reddit_connected');
        const usernameParam = urlParams.get('username');
        const sessionIdParam = urlParams.get('session_id');

        if (redditConnectedParam === 'true' && sessionIdParam) {
          setSessionId(sessionIdParam);
          setRedditUsername(usernameParam || '');
          setRedditConnected(true);
          localStorage.setItem('reddit_session_id', sessionIdParam);
          localStorage.setItem('reddit_username', usernameParam || '');
          showNotification(`Reddit connected! Welcome ${usernameParam}!`, 'success');
          window.history.replaceState({}, '', window.location.pathname);
        } else {
          // Try to restore session from localStorage
          const savedSessionId = localStorage.getItem('reddit_session_id');
          const savedUsername = localStorage.getItem('reddit_username');
          
          if (savedSessionId && savedUsername) {
            // Verify session with backend
            try {
              const response = await fetch(`${API_BASE_URL}/api/auth/session-info`, {
                headers: { 'x-session-id': savedSessionId }
              });
              const result = await response.json();
              
              if (result.success && result.reddit_connected) {
                setSessionId(savedSessionId);
                setRedditUsername(result.reddit_username);
                setRedditConnected(true);
              } else {
                // Session invalid, create new one
                await createNewSession();
              }
            } catch (error) {
              await createNewSession();
            }
          } else {
            await createNewSession();
          }
        }

        // Load saved profile
        const savedProfile = localStorage.getItem('redditUserProfile');
        if (savedProfile) {
          setUserProfile(JSON.parse(savedProfile));
        }

        // Test backend connection
        try {
          const healthResponse = await fetch(`${API_BASE_URL}/health`);
          const healthData = await healthResponse.json();
          if (healthData.success) {
            setBackendConnected(true);
          }
        } catch (error) {
          setBackendConnected(false);
        }
      } catch (error) {
        console.error('App initialization failed:', error);
        showNotification('App initialization failed', 'error');
      }
    };

    const createNewSession = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/create-session`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();
        if (result.success) {
          setSessionId(result.session_id);
          localStorage.setItem('reddit_session_id', result.session_id);
        }
      } catch (error) {
        console.error('Session creation failed:', error);
      }
    };

    initApp();
  }, [showNotification]);

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
      
      if (!sessionId) {
        await recoverSession();
        return;
      }

      const response = await makeAPIRequest('/api/oauth/reddit/authorize', 'GET', { session_id: sessionId });
      if (response.success && response.redirect_url) {
        window.location.href = response.redirect_url;
      } else {
        showNotification(response.error || 'Failed to start Reddit authorization', 'error');
      }
    } catch (error) {
      showNotification('Connection failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [sessionId, makeAPIRequest, recoverSession, showNotification]);

  const testConnection = useCallback(async () => {
    try {
      setLoading(true);
      const response = await makeAPIRequest('/api/reddit/test-connection');
      if (response.success) {
        showNotification(`Connection test successful for ${response.username}!`, 'success');
      } else {
        showNotification('Connection test failed: ' + response.error, 'error');
      }
    } catch (error) {
      showNotification('Test failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAPIRequest, showNotification]);

  // FIXED: Real AI content generation
  const generateContent = useCallback(async () => {
    if (!userProfile.businessType) {
      showNotification('Please configure your profile first', 'error');
      return;
    }

    try {
      setManualPost(prev => ({ ...prev, isGenerating: true }));
      showNotification('Generating content with REAL AI...', 'info');
      
      // Try backend first
      const response = await makeAPIRequest('/api/automation/test-auto-post', 'POST', {
        domain: userProfile.domain,
        business_type: userProfile.businessType,
        business_description: userProfile.businessDescription,
        target_audience: userProfile.targetAudience,
        language: userProfile.language,
        subreddits: [manualPost.subreddit],
        content_style: userProfile.contentStyle
      });

      if (response.success) {
        setManualPost(prev => ({
          ...prev,
          title: response.post_details?.title || 'Generated Title',
          content: response.content_preview
        }));
        showNotification(`Content generated using ${response.ai_service}!`, 'success');
      } else {
        // Fallback: Direct Mistral API call
        await generateWithMistral();
      }
    } catch (error) {
      await generateWithMistral();
    } finally {
      setManualPost(prev => ({ ...prev, isGenerating: false }));
    }
  }, [userProfile, manualPost.subreddit, makeAPIRequest, showNotification]);

  // Direct Mistral API fallback
  const generateWithMistral = async () => {
    try {
      const mistralKey = process.env.REACT_APP_MISTRAL_API_KEY;
      if (!mistralKey) {
        showNotification('AI service unavailable - configure REACT_APP_MISTRAL_API_KEY', 'error');
        return;
      }

      const response = await fetch('https://api.mistral.ai/v1/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${mistralKey}`
        },
        body: JSON.stringify({
          model: 'mistral-medium',
          messages: [{
            role: 'user',
            content: `Generate a Reddit post for a ${userProfile.businessType} in the ${userProfile.domain} domain. Target audience: ${userProfile.targetAudience}. Style: ${userProfile.contentStyle}. Include title and content.`
          }],
          max_tokens: 500
        })
      });

      const data = await response.json();
      const content = data.choices?.[0]?.message?.content || 'Generated content using Mistral API';
      
      setManualPost(prev => ({
        ...prev,
        title: 'AI Generated Title',
        content: content
      }));
      showNotification('Content generated using direct Mistral API!', 'success');
    } catch (error) {
      showNotification('AI generation failed: ' + error.message, 'error');
    }
  };

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
      
      const response = await makeAPIRequest('/api/reddit/post', 'POST', {
        subreddit: manualPost.subreddit,
        title: manualPost.title,
        content: manualPost.content,
        contentType: 'text'
      });
      
      if (response.success) {
        showNotification(`Post created successfully as ${redditUsername}!`, 'success');
        if (response.post_url) {
          showNotification(`View post: ${response.post_url}`, 'info');
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
        showNotification(response.error || 'Posting failed', 'error');
      }
    } catch (error) {
      showNotification('Posting failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [manualPost, makeAPIRequest, redditUsername, redditConnected, showNotification]);

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

      const response = await makeAPIRequest('/api/automation/setup-auto-posting', 'POST', config);
      
      if (response.success) {
        setAutoPostConfig(prev => ({ ...prev, enabled: true }));
        showNotification(`Auto-posting started for ${redditUsername}!`, 'success');
        if (response.next_post_time) {
          showNotification(`Next post: ${response.next_post_time}`, 'info');
        }
      } else {
        showNotification(response.error || 'Automation setup failed', 'error');
      }
    } catch (error) {
      showNotification('Setup failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [userProfile, redditConnected, autoPostConfig, makeAPIRequest, redditUsername, showNotification]);

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
          <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>REAL AI-Powered Platform</div>
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

        <div style={{ padding: '24px', borderTop: '1px solid rgba(0, 0, 0, 0.1)' }}>
          {redditConnected ? (
            <div>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '12px 16px',
                borderRadius: '8px',
                fontSize: '14px',
                fontWeight: '500',
                background: 'rgba(34, 197, 94, 0.1)',
                color: '#16a34a'
              }}>
                <span style={{ width: '8px', height: '8px', backgroundColor: '#22c55e', borderRadius: '50%' }}></span>
                <span>Reddit Connected</span>
              </div>
              {redditUsername && (
                <div style={{ fontSize: '12px', color: '#666', margin: '8px 0' }}>
                  u/{redditUsername}
                </div>
              )}
              <button 
                onClick={testConnection}
                disabled={loading}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  marginTop: '8px',
                  fontSize: '12px',
                  background: 'linear-gradient(135deg, #667eea, #764ba2)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer'
                }}
              >
                Test Connection
              </button>
            </div>
          ) : (
            <button 
              onClick={handleRedditConnect} 
              disabled={loading}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '12px',
                background: 'linear-gradient(135deg, #667eea, #764ba2)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              <span>🔗</span>
              <span>{loading ? 'Connecting...' : 'Connect Reddit'}</span>
            </button>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, marginLeft: '280px', background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
        <header style={{ padding: '32px 40px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '8px' }}>Reddit Automation Dashboard</h1>
            <p style={{ fontSize: '16px', color: '#666' }}>REAL AI-powered Reddit automation for {redditUsername || 'your account'}</p>
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
                      {loading ? 'Posting...' : `Post as ${redditUsername || 'Reddit User'}`}
                    </button>
                  </div>
                </form>
              </div>
            )}

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

      <style jsx>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};

export default function App() {
  return (
    <ErrorBoundary>
      <RedditAutomation />
    </ErrorBoundary>
  );
}