import React, { useState, useEffect, useCallback } from 'react';

// Error Boundary Component
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
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Something went wrong.</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
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
    language: 'en',
    contentStyle: 'engaging',
    isConfigured: false
  });

  const [manualPost, setManualPost] = useState({
    subreddit: 'test',
    title: '',
    content: '',
    generatedContent: '',
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
      subreddits: ['JEE', 'NEET', 'IndianStudents', 'india', 'AskReddit', 'StudyTips'],
      sampleBusiness: 'JEE coaching institute in Delhi',
      icon: '🎓',
      description: 'Educational services and exam preparation'
    },
    restaurant: {
      subreddits: ['IndianFood', 'food', 'bangalore', 'mumbai', 'delhi', 'recipes'],
      sampleBusiness: 'Traditional Indian restaurant in Mumbai',
      icon: '🍽️',
      description: 'Food, restaurants, and culinary experiences'
    },
    tech: {
      subreddits: ['developersIndia', 'programming', 'india', 'bangalore', 'coding', 'webdev'],
      sampleBusiness: 'AI automation platform for businesses',
      icon: '💻',
      description: 'Technology, programming, and software development'
    },
    health: {
      subreddits: ['fitness', 'HealthyFood', 'india', 'mentalhealth', 'nutrition', 'wellness'],
      sampleBusiness: 'Fitness coaching and nutrition center',
      icon: '💚',
      description: 'Health, fitness, and wellness services'
    },
    business: {
      subreddits: ['entrepreneur', 'IndiaInvestments', 'business', 'india', 'startup', 'smallbusiness'],
      sampleBusiness: 'Business consulting firm for startups',
      icon: '💼',
      description: 'Business, entrepreneurship, and investments'
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

  const subredditOptions = [
    'test', 'india', 'developersIndia', 'programming', 'AskReddit',
    'explainlikeimfive', 'NoStupidQuestions', 'bangalore', 'mumbai',
    'JEE', 'NEET', 'IndianStudents', 'IndianFood', 'food'
  ];

  // FIXED: Unique notification ID generation
  const showNotification = useCallback((message, type = 'success') => {
    console.log(`📢 ${type.toUpperCase()}: ${message}`);
    const notification = { 
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, // FIXED: Unique ID
      message, 
      type 
    };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  }, []);

  // Enhanced API request with proper error handling
  const makeAPIRequest = useCallback(async (endpoint, method = 'GET', data = null) => {
    try {
      console.log(`🌐 API Request: ${method} ${endpoint}`);
      
      const headers = {
        'Content-Type': 'application/json'
      };

      if (sessionId) {
        headers['x-session-id'] = sessionId;
      }

      const config = { method, headers };
      if (data && method !== 'GET') {
        config.body = JSON.stringify({ ...data, use_real_ai: true, test_mode: false });
      }

      try {
        const response = await fetch(`http://localhost:8000${endpoint}`, config);
        const result = await response.json();
        
        if (result.success) {
          setBackendConnected(true);
          setConnectionError('');
          return result;
        } else {
          console.warn('API request failed:', result);
          return result;
        }
      } catch (backendError) {
        console.warn('Backend not available:', backendError.message);
        setBackendConnected(false);
        setConnectionError('Backend not available - check if server is running on port 8000');
        throw backendError;
      }
    } catch (error) {
      console.error('API Request failed:', error);
      return { success: false, error: error.message };
    }
  }, [sessionId]);

  // Initialize app
  useEffect(() => {
    const initApp = async () => {
      try {
        console.log('🚀 Initializing Reddit Automation App...');
        
        // Handle OAuth callback
        const urlParams = new URLSearchParams(window.location.search);
        const redditConnectedParam = urlParams.get('reddit_connected');
        const usernameParam = urlParams.get('username');
        const sessionIdParam = urlParams.get('session_id');

        if (redditConnectedParam === 'true' && sessionIdParam) {
          setSessionId(sessionIdParam);
          setRedditUsername(usernameParam || 'demo_user');
          setRedditConnected(true);
          showNotification(`🎉 Reddit connected! Welcome ${usernameParam}!`, 'success');
          console.log(`✅ OAuth success: ${usernameParam} connected`);
          window.history.replaceState({}, '', window.location.pathname);
        } else {
          const savedSessionId = localStorage.getItem('reddit_session_id');
          const savedUsername = localStorage.getItem('reddit_username');
          
          if (savedSessionId) {
            setSessionId(savedSessionId);
            if (savedUsername) {
              setRedditUsername(savedUsername);
              setRedditConnected(true);
            }
          } else {
            const response = await makeAPIRequest('/api/auth/create-session', 'POST');
            if (response.success) {
              setSessionId(response.session_id);
              localStorage.setItem('reddit_session_id', response.session_id);
            }
          }
        }

        const savedProfile = localStorage.getItem('redditUserProfile');
        if (savedProfile) {
          setUserProfile(JSON.parse(savedProfile));
        }

        const healthResponse = await makeAPIRequest('/health');
        if (healthResponse.success) {
          setBackendConnected(true);
          console.log('✅ Backend connected');
        }

        console.log('✅ App initialization completed');
      } catch (error) {
        console.error('❌ App initialization failed:', error);
        showNotification('App initialization failed', 'error');
      }
    };

    initApp();
  }, [makeAPIRequest, showNotification]);

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
      console.error('Failed to save profile:', error);
      showNotification('Failed to save profile', 'error');
    }
  }, [userProfile, domainConfigs, showNotification]);

  const handleRedditConnect = useCallback(async () => {
    try {
      setLoading(true);
      showNotification('Connecting to Reddit...', 'info');
      
      if (!sessionId) {
        const sessionResponse = await makeAPIRequest('/api/auth/create-session', 'POST');
        if (sessionResponse.success) {
          setSessionId(sessionResponse.session_id);
          localStorage.setItem('reddit_session_id', sessionResponse.session_id);
        }
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
  }, [sessionId, makeAPIRequest, showNotification]);

  const testConnection = useCallback(async () => {
    try {
      setLoading(true);
      const response = await makeAPIRequest('/api/reddit/test-connection');
      if (response.success) {
        showNotification(`✅ Connection test successful for ${response.username}!`, 'success');
      } else {
        showNotification('Connection test failed: ' + response.error, 'error');
      }
    } catch (error) {
      showNotification('Test failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAPIRequest, showNotification]);

  const generateContent = useCallback(async () => {
    if (!userProfile.businessType) {
      showNotification('Please configure your profile first', 'error');
      return;
    }

    try {
      setManualPost(prev => ({ ...prev, isGenerating: true }));
      showNotification('🤖 Generating content with REAL AI...', 'info');
      
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
          generatedContent: response.content_preview,
          title: response.post_details?.title || 'Generated Title',
          content: response.content_preview
        }));
        const aiService = response.ai_service || 'AI';
        showNotification(`✅ Content generated using ${aiService}!`, 'success');
      } else {
        showNotification(response.error || 'Content generation failed', 'error');
      }
    } catch (error) {
      showNotification('Generation failed: ' + error.message, 'error');
    } finally {
      setManualPost(prev => ({ ...prev, isGenerating: false }));
    }
  }, [userProfile, manualPost.subreddit, makeAPIRequest, showNotification]);

  const handleManualPost = useCallback(async (e) => {
    e.preventDefault();
    
    if (!manualPost.title || !manualPost.content) {
      showNotification('Please enter both title and content', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('📮 Posting to Reddit...', 'info');
      
      const response = await makeAPIRequest('/api/reddit/post', 'POST', {
        subreddit: manualPost.subreddit,
        title: manualPost.title,
        content: manualPost.content,
        contentType: 'text'
      });
      
      if (response.success) {
        showNotification(`🎉 Post created successfully as ${redditUsername}!`, 'success');
        if (response.post_url) {
          showNotification(`🔗 View post: ${response.post_url}`, 'info');
        }
        
        setPerformanceData(prev => ({
          ...prev,
          postsToday: prev.postsToday + 1
        }));
        
        setManualPost({
          subreddit: 'test',
          title: '',
          content: '',
          generatedContent: '',
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
  }, [manualPost, makeAPIRequest, redditUsername, showNotification]);

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
      showNotification('🚀 Setting up REAL automation...', 'info');
      
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
        showNotification(`🎯 Auto-posting started for ${redditUsername}!`, 'success');
        if (response.next_post_time) {
          showNotification(`⏰ Next post: ${response.next_post_time}`, 'info');
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

  const debugConnection = useCallback(() => {
    console.log('🐛 === DEBUG CONNECTION INFO ===');
    console.log('Backend connected:', backendConnected);
    console.log('Session ID:', sessionId);
    console.log('Reddit connected:', redditConnected);
    console.log('Reddit username:', redditUsername);
    console.log('Connection error:', connectionError);
    console.log('Profile configured:', userProfile.isConfigured);
    console.log('=== END DEBUG INFO ===');
    showNotification('Debug info logged to console', 'info');
  }, [backendConnected, sessionId, redditConnected, redditUsername, connectionError, userProfile, showNotification]);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Notifications */}
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 1000 }}>
        {notifications.map(notification => (
          <div 
            key={notification.id} 
            style={{
              padding: '12px 16px',
              marginBottom: '8px',
              borderRadius: '6px',
              backgroundColor: notification.type === 'success' ? '#d4edda' : 
                              notification.type === 'error' ? '#f8d7da' : 
                              notification.type === 'warning' ? '#fff3cd' : '#d1ecf1',
              border: `1px solid ${notification.type === 'success' ? '#c3e6cb' : 
                                  notification.type === 'error' ? '#f5c6cb' : 
                                  notification.type === 'warning' ? '#ffeaa7' : '#bee5eb'}`,
              color: notification.type === 'success' ? '#155724' : 
                     notification.type === 'error' ? '#721c24' : 
                     notification.type === 'warning' ? '#856404' : '#0c5460',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              maxWidth: '350px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '14px' }}>{notification.message}</span>
              <button 
                onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '18px',
                  cursor: 'pointer',
                  marginLeft: '12px',
                  color: 'inherit'
                }}
              >
                ×
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 9999
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            textAlign: 'center',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #007bff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 15px'
            }}></div>
            <p style={{ margin: 0, color: '#666' }}>Processing...</p>
          </div>
        </div>
      )}

      <div style={{ display: 'flex' }}>
        {/* Sidebar */}
        <div style={{
          width: '280px',
          backgroundColor: '#2c3e50',
          color: 'white',
          padding: '20px',
          minHeight: '100vh',
          boxShadow: '2px 0 10px rgba(0,0,0,0.1)'
        }}>
          <div style={{ marginBottom: '30px', textAlign: 'center' }}>
            <h2 style={{ margin: '0 0 5px 0', fontSize: '24px', fontWeight: 'bold' }}>Reddit Auto</h2>
            <div style={{ fontSize: '14px', color: '#bdc3c7' }}>REAL AI-Powered Platform</div>
            
            <div style={{ marginTop: '15px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                padding: '6px 10px',
                backgroundColor: backendConnected ? '#27ae60' : '#e74c3c',
                borderRadius: '4px',
                marginBottom: '5px',
                fontSize: '12px'
              }}>
                <span style={{
                  width: '6px',
                  height: '6px',
                  backgroundColor: 'white',
                  borderRadius: '50%',
                  marginRight: '6px'
                }}></span>
                Backend: {backendConnected ? 'Connected' : 'Offline'}
              </div>
              
              {connectionError && (
                <div style={{
                  padding: '6px 10px',
                  backgroundColor: '#e74c3c',
                  borderRadius: '4px',
                  fontSize: '11px',
                  marginBottom: '5px'
                }}>
                  {connectionError}
                </div>
              )}
            </div>
          </div>
          
          <nav style={{ marginBottom: '30px' }}>
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
                  display: 'block',
                  width: '100%',
                  padding: '12px 16px',
                  margin: '5px 0',
                  backgroundColor: activeTab === tab.id ? '#3498db' : 'transparent',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                <span style={{ marginRight: '10px' }}>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>

          <div>
            {redditConnected ? (
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '8px 12px',
                  backgroundColor: '#27ae60',
                  borderRadius: '6px',
                  marginBottom: '8px'
                }}>
                  <span style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#2ecc71',
                    borderRadius: '50%',
                    marginRight: '8px'
                  }}></span>
                  <span style={{ fontSize: '14px' }}>Reddit Connected</span>
                </div>
                {redditUsername && (
                  <div style={{ fontSize: '12px', color: '#bdc3c7', marginBottom: '8px' }}>
                    u/{redditUsername}
                  </div>
                )}
                <button 
                  onClick={testConnection}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '6px 12px',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    marginBottom: '5px'
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
                  padding: '12px 16px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <span>🔗</span>
                <span>{loading ? 'Connecting...' : 'Connect Reddit'}</span>
              </button>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: '20px' }}>
          <header style={{
            backgroundColor: 'white',
            padding: '20px 30px',
            borderRadius: '8px',
            marginBottom: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h1 style={{ margin: '0 0 5px 0', fontSize: '28px', color: '#2c3e50' }}>
                Reddit Automation Dashboard
              </h1>
              <p style={{ margin: '0 0 10px 0', color: '#7f8c8d', fontSize: '16px' }}>
                REAL AI-powered Reddit automation for {redditUsername || 'your account'}
              </p>
              <div style={{ fontSize: '12px', color: '#95a5a6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                Status: {backendConnected ? 'Live Backend' : 'Offline'}
                <button 
                  onClick={debugConnection}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: '#e74c3c',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '10px'
                  }}
                >
                  Debug
                </button>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '10px' }}>
              {userProfile.isConfigured && (
                <button 
                  onClick={startAutoPosting}
                  disabled={loading || !redditConnected}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: loading || !redditConnected ? '#bdc3c7' : '#27ae60',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: loading || !redditConnected ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <span>🚀</span>
                  <span>Start Auto-Post</span>
                </button>
              )}
            </div>
          </header>

          {/* Tab Content */}
          <main>
            {activeTab === 'setup' && (
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>Profile Configuration</h2>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>
                    Business Domain *
                  </label>
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
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  >
                    {Object.entries(domainConfigs).map(([key, config]) => (
                      <option key={key} value={key}>
                        {config.icon} {config.description}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>
                    Business Type *
                  </label>
                  <input
                    type="text"
                    value={userProfile.businessType}
                    onChange={(e) => setUserProfile(prev => ({
                      ...prev,
                      businessType: e.target.value
                    }))}
                    placeholder={domainConfigs[userProfile.domain]?.sampleBusiness}
                    style={{
                      width: '100%',
                      padding: '10px',
                              showNotification(`🎉 Post created successfully as ${redditUsername}!`, 'success');
        if (response.post_url) {
          showNotification(`🔗 View post: ${response.post_url}`, 'info');
        }
        
        setPerformanceData(prev => ({
          ...prev,
          postsToday: prev.postsToday + 1
        }));
        
        setManualPost({
          subreddit: 'test',
          title: '',
          content: '',
          generatedContent: '',
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
  }, [manualPost, makeAPIRequest, redditUsername, showNotification]);

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
      showNotification('🚀 Setting up REAL automation...', 'info');
      
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
        showNotification(`🎯 Auto-posting started for ${redditUsername}!`, 'success');
        if (response.next_post_time) {
          showNotification(`⏰ Next post: ${response.next_post_time}`, 'info');
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

  const debugConnection = useCallback(() => {
    console.log('🐛 === DEBUG CONNECTION INFO ===');
    console.log('Backend connected:', backendConnected);
    console.log('Session ID:', sessionId);
    console.log('Reddit connected:', redditConnected);
    console.log('Reddit username:', redditUsername);
    console.log('Connection error:', connectionError);
    console.log('Profile configured:', userProfile.isConfigured);
    console.log('=== END DEBUG INFO ===');
    showNotification('Debug info logged to console', 'info');
  }, [backendConnected, sessionId, redditConnected, redditUsername, connectionError, userProfile, showNotification]);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Notifications */}
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 1000 }}>
        {notifications.map(notification => (
          <div 
            key={notification.id} 
            style={{
              padding: '12px 16px',
              marginBottom: '8px',
              borderRadius: '6px',
              backgroundColor: notification.type === 'success' ? '#d4edda' : 
                              notification.type === 'error' ? '#f8d7da' : 
                              notification.type === 'warning' ? '#fff3cd' : '#d1ecf1',
              border: `1px solid ${notification.type === 'success' ? '#c3e6cb' : 
                                  notification.type === 'error' ? '#f5c6cb' : 
                                  notification.type === 'warning' ? '#ffeaa7' : '#bee5eb'}`,
              color: notification.type === 'success' ? '#155724' : 
                     notification.type === 'error' ? '#721c24' : 
                     notification.type === 'warning' ? '#856404' : '#0c5460',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              maxWidth: '350px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '14px' }}>{notification.message}</span>
              <button 
                onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '18px',
                  cursor: 'pointer',
                  marginLeft: '12px',
                  color: 'inherit'
                }}
              >
                ×
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 9999
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            textAlign: 'center',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #007bff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 15px'
            }}></div>
            <p style={{ margin: 0, color: '#666' }}>Processing...</p>
          </div>
        </div>
      )}

      <div style={{ display: 'flex' }}>
        {/* Sidebar */}
        <div style={{
          width: '280px',
          backgroundColor: '#2c3e50',
          color: 'white',
          padding: '20px',
          minHeight: '100vh',
          boxShadow: '2px 0 10px rgba(0,0,0,0.1)'
        }}>
          <div style={{ marginBottom: '30px', textAlign: 'center' }}>
            <h2 style={{ margin: '0 0 5px 0', fontSize: '24px', fontWeight: 'bold' }}>Reddit Auto</h2>
            <div style={{ fontSize: '14px', color: '#bdc3c7' }}>REAL AI-Powered Platform</div>
            
            <div style={{ marginTop: '15px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                padding: '6px 10px',
                backgroundColor: backendConnected ? '#27ae60' : '#e74c3c',
                borderRadius: '4px',
                marginBottom: '5px',
                fontSize: '12px'
              }}>
                <span style={{
                  width: '6px',
                  height: '6px',
                  backgroundColor: 'white',
                  borderRadius: '50%',
                  marginRight: '6px'
                }}></span>
                Backend: {backendConnected ? 'Connected' : 'Offline'}
              </div>
              
              {connectionError && (
                <div style={{
                  padding: '6px 10px',
                  backgroundColor: '#e74c3c',
                  borderRadius: '4px',
                  fontSize: '11px',
                  marginBottom: '5px'
                }}>
                  {connectionError}
                </div>
              )}
            </div>
          </div>
          
          <nav style={{ marginBottom: '30px' }}>
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
                  display: 'block',
                  width: '100%',
                  padding: '12px 16px',
                  margin: '5px 0',
                  backgroundColor: activeTab === tab.id ? '#3498db' : 'transparent',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                <span style={{ marginRight: '10px' }}>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>

          <div>
            {redditConnected ? (
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '8px 12px',
                  backgroundColor: '#27ae60',
                  borderRadius: '6px',
                  marginBottom: '8px'
                }}>
                  <span style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#2ecc71',
                    borderRadius: '50%',
                    marginRight: '8px'
                  }}></span>
                  <span style={{ fontSize: '14px' }}>Reddit Connected</span>
                </div>
                {redditUsername && (
                  <div style={{ fontSize: '12px', color: '#bdc3c7', marginBottom: '8px' }}>
                    u/{redditUsername}
                  </div>
                )}
                <button 
                  onClick={testConnection}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '6px 12px',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    marginBottom: '5px'
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
                  padding: '12px 16px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <span>🔗</span>
                <span>{loading ? 'Connecting...' : 'Connect Reddit'}</span>
              </button>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: '20px' }}>
          <header style={{
            backgroundColor: 'white',
            padding: '20px 30px',
            borderRadius: '8px',
            marginBottom: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h1 style={{ margin: '0 0 5px 0', fontSize: '28px', color: '#2c3e50' }}>
                Reddit Automation Dashboard
              </h1>
              <p style={{ margin: '0 0 10px 0', color: '#7f8c8d', fontSize: '16px' }}>
                REAL AI-powered Reddit automation for {redditUsername || 'your account'}
              </p>
              <div style={{ fontSize: '12px', color: '#95a5a6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                Status: {backendConnected ? 'Live Backend' : 'Offline'}
                <button 
                  onClick={debugConnection}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: '#e74c3c',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '10px'
                  }}
                >
                  Debug
                </button>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '10px' }}>
              {userProfile.isConfigured && (
                <button 
                  onClick={startAutoPosting}
                  disabled={loading || !redditConnected}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: loading || !redditConnected ? '#bdc3c7' : '#27ae60',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: loading || !redditConnected ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <span>🚀</span>
                  <span>Start Auto-Post</span>
                </button>
              )}
            </div>
          </header>

          {/* Tab Content */}
          <main>
            {activeTab === 'setup' && (
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>Profile Configuration</h2>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>
                    Business Domain *
                  </label>
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
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  >
                    {Object.entries(domainConfigs).map(([key, config]) => (
                      <option key={key} value={key}>
                        {config.icon} {config.description}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>
                    Business Type *
                  </label>
                  <input
                    type="text"
                    value={userProfile.businessType}
                    onChange={(e) => setUserProfile(prev => ({
                      ...prev,
                      businessType: e.target.value
                    }))}
                    placeholder={domainConfigs[userProfile.domain]?.sampleBusiness}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                    required
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>
                    Target Audience
                  </label>
                  <select 
                    value={userProfile.targetAudience}
                    onChange={(e) => setUserProfile(prev => ({
                      ...prev,
                      targetAudience: e.target.value
                    }))}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  >
                    {Object.entries(targetAudienceOptions).map(([key, option]) => (
                      <option key={key} value={key}>
                        {option.icon} {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <button 
                  onClick={saveUserProfile}
                  disabled={!userProfile.businessType}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: userProfile.businessType ? '#27ae60' : '#bdc3c7',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: userProfile.businessType ? 'pointer' : 'not-allowed',
                    fontSize: '14px'
                  }}
                >
                  Save Configuration
                </button>

                {userProfile.isConfigured && (
                  <div style={{
                    marginTop: '20px',
                    padding: '15px',
                    backgroundColor: '#d4edda',
                    borderRadius: '6px',
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
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>Manual Posting with REAL AI</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '20px', marginBottom: '20px', alignItems: 'end' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>Subreddit</label>
                    <select
                      value={manualPost.subreddit}
                      onChange={(e) => setManualPost(prev => ({
                        ...prev,
                        subreddit: e.target.value
                      }))}
                      style={{
                        width: '100%',
                        padding: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px'
                      }}
                    >
                      {subredditOptions.map(sub => (
                        <option key={sub} value={sub}>r/{sub}</option>
                      ))}
                    </select>
                  </div>

                  <button 
                    onClick={generateContent}
                    disabled={manualPost.isGenerating || !userProfile.isConfigured}
                    style={{
                      padding: '12px 20px',
                      backgroundColor: (manualPost.isGenerating || !userProfile.isConfigured) ? '#bdc3c7' : '#3498db',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: (manualPost.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    {manualPost.isGenerating ? 'Generating...' : 'Generate with AI'}
                  </button>
                </div>

                <form onSubmit={handleManualPost}>
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>Post Title</label>
                    <input
                      type="text"
                      value={manualPost.title}
                      onChange={(e) => setManualPost(prev => ({
                        ...prev,
                        title: e.target.value
                      }))}
                      placeholder="Enter your post title..."
                      style={{
                        width: '100%',
                        padding: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px'
                      }}
                      required
                    />
                  </div>

                  <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>Post Content</label>
                    <textarea
                      value={manualPost.content}
                      onChange={(e) => setManualPost(prev => ({
                        ...prev,
                        content: e.target.value
                      }))}
                      placeholder="Enter your post content..."
                      rows="8"
                      style={{
                        width: '100%',
                        padding: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px',
                        resize: 'vertical'
                      }}
                      required
                    />
                  </div>

                  <button 
                    type="submit" 
                    disabled={loading || !redditConnected || !manualPost.title || !manualPost.content}
                    style={{
                      padding: '12px 24px',
                      backgroundColor: (loading || !redditConnected || !manualPost.title || !manualPost.content) ? '#bdc3c7' : '#27ae60',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: (loading || !redditConnected || !manualPost.title || !manualPost.content) ? 'not-allowed' : 'pointer',
                      fontSize: '16px',
                      fontWeight: 'bold'
                    }}
                  >
                    {loading ? 'Posting...' : `Post as ${redditUsername || 'Reddit User'}`}
                  </button>
                </form>
              </div>
            )}

            {activeTab === 'schedule' && (
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>Auto-Post Schedule</h2>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>Posts Per Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={autoPostConfig.postsPerDay}
                    onChange={(e) => setAutoPostConfig(prev => ({
                      ...prev,
                      postsPerDay: parseInt(e.target.value) || 1
                    }))}
                    style={{
                      width: '200px',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <h4 style={{ color: '#2c3e50', marginBottom: '10px' }}>Posting Times</h4>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '15px' }}>
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
                      style={{
                        padding: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px'
                      }}
                    />
                    <button
                      onClick={() => {
                        const now = new Date();
                        now.setMinutes(now.getMinutes() + 2);
                        const testTime = now.toTimeString().slice(0, 5);
                        if (!autoPostConfig.postingTimes.includes(testTime)) {
                          setAutoPostConfig(prev => ({
                            ...prev,
                            postingTimes: [...prev.postingTimes, testTime].sort()
                          }));
                        }
                      }}
                      type="button"
                      style={{
                        padding: '10px 16px',
                        backgroundColor: '#f39c12',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px'
                      }}
                    >
                      Add Test Time (+2min)
                    </button>
                  </div>

                  {autoPostConfig.postingTimes.length > 0 && (
                    <div>
                      <h5 style={{ color: '#2c3e50' }}>Scheduled Times ({autoPostConfig.postingTimes.length})</h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {autoPostConfig.postingTimes.map(time => (
                          <div key={time} style={{
                            display: 'flex',
                            alignItems: 'center',
                            backgroundColor: '#ecf0f1',
                            padding: '6px 12px',
                            borderRadius: '20px',
                            fontSize: '14px'
                          }}>
                            <span>{time}</span>
                            <button 
                              onClick={() => setAutoPostConfig(prev => ({
                                ...prev,
                                postingTimes: prev.postingTimes.filter(t => t !== time)
                              }))}
                              style={{
                                background: 'none',
                                border: 'none',
                                marginLeft: '8px',
                                cursor: 'pointer',
                                fontSize: '16px',
                                color: '#e74c3c'
                              }}
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'status' && (
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>System Status & Analytics</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  <div style={{
                    padding: '20px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '6px',
                    border: '1px solid #e9ecef'
                  }}>
                    <h3 style={{ marginTop: 0, color: '#2c3e50' }}>Reddit Connection</h3>
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

                  <div style={{
                    padding: '20px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '6px',
                    border: '1px solid #e9ecef'
                  }}>
                    <h3 style={{ marginTop: 0, color: '#2c3e50' }}>Profile Status</h3>
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
                      <p style={{ margin: '10px 0 0 0', color: '#        showNotification(`🎉 Post created successfully as ${redditUsername}!`, 'success');
        if (response.post_url) {
          showNotification(`🔗 View post: ${response.post_url}`, 'info');
        }
        
        setPerformanceData(prev => ({
          ...prev,
          postsToday: prev.postsToday + 1
        }));
        
        setManualPost({
          subreddit: 'test',
          title: '',
          content: '',
          generatedContent: '',
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
  }, [manualPost, makeAPIRequest, redditUsername, showNotification]);

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
      showNotification('🚀 Setting up REAL automation...', 'info');
      
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
        showNotification(`🎯 Auto-posting started for ${redditUsername}!`, 'success');
        if (response.next_post_time) {
          showNotification(`⏰ Next post: ${response.next_post_time}`, 'info');
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

  const debugConnection = useCallback(() => {
    console.log('🐛 === DEBUG CONNECTION INFO ===');
    console.log('Backend connected:', backendConnected);
    console.log('Session ID:', sessionId);
    console.log('Reddit connected:', redditConnected);
    console.log('Reddit username:', redditUsername);
    console.log('Connection error:', connectionError);
    console.log('Profile configured:', userProfile.isConfigured);
    console.log('=== END DEBUG INFO ===');
    showNotification('Debug info logged to console', 'info');
  }, [backendConnected, sessionId, redditConnected, redditUsername, connectionError, userProfile, showNotification]);

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', minHeight: '100vh', backgroundColor: '#f5f5f5' }}>
      {/* Notifications */}
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 1000 }}>
        {notifications.map(notification => (
          <div 
            key={notification.id} 
            style={{
              padding: '12px 16px',
              marginBottom: '8px',
              borderRadius: '6px',
              backgroundColor: notification.type === 'success' ? '#d4edda' : 
                              notification.type === 'error' ? '#f8d7da' : 
                              notification.type === 'warning' ? '#fff3cd' : '#d1ecf1',
              border: `1px solid ${notification.type === 'success' ? '#c3e6cb' : 
                                  notification.type === 'error' ? '#f5c6cb' : 
                                  notification.type === 'warning' ? '#ffeaa7' : '#bee5eb'}`,
              color: notification.type === 'success' ? '#155724' : 
                     notification.type === 'error' ? '#721c24' : 
                     notification.type === 'warning' ? '#856404' : '#0c5460',
              boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              maxWidth: '350px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '14px' }}>{notification.message}</span>
              <button 
                onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
                style={{
                  background: 'none',
                  border: 'none',
                  fontSize: '18px',
                  cursor: 'pointer',
                  marginLeft: '12px',
                  color: 'inherit'
                }}
              >
                ×
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 9999
        }}>
          <div style={{
            backgroundColor: 'white',
            padding: '30px',
            borderRadius: '8px',
            textAlign: 'center',
            boxShadow: '0 4px 20px rgba(0,0,0,0.3)'
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '4px solid #f3f3f3',
              borderTop: '4px solid #007bff',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite',
              margin: '0 auto 15px'
            }}></div>
            <p style={{ margin: 0, color: '#666' }}>Processing...</p>
          </div>
        </div>
      )}

      <div style={{ display: 'flex' }}>
        {/* Sidebar */}
        <div style={{
          width: '280px',
          backgroundColor: '#2c3e50',
          color: 'white',
          padding: '20px',
          minHeight: '100vh',
          boxShadow: '2px 0 10px rgba(0,0,0,0.1)'
        }}>
          <div style={{ marginBottom: '30px', textAlign: 'center' }}>
            <h2 style={{ margin: '0 0 5px 0', fontSize: '24px', fontWeight: 'bold' }}>Reddit Auto</h2>
            <div style={{ fontSize: '14px', color: '#bdc3c7' }}>REAL AI-Powered Platform</div>
            
            <div style={{ marginTop: '15px' }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                padding: '6px 10px',
                backgroundColor: backendConnected ? '#27ae60' : '#e74c3c',
                borderRadius: '4px',
                marginBottom: '5px',
                fontSize: '12px'
              }}>
                <span style={{
                  width: '6px',
                  height: '6px',
                  backgroundColor: 'white',
                  borderRadius: '50%',
                  marginRight: '6px'
                }}></span>
                Backend: {backendConnected ? 'Connected' : 'Offline'}
              </div>
              
              {connectionError && (
                <div style={{
                  padding: '6px 10px',
                  backgroundColor: '#e74c3c',
                  borderRadius: '4px',
                  fontSize: '11px',
                  marginBottom: '5px'
                }}>
                  {connectionError}
                </div>
              )}
            </div>
          </div>
          
          <nav style={{ marginBottom: '30px' }}>
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
                  display: 'block',
                  width: '100%',
                  padding: '12px 16px',
                  margin: '5px 0',
                  backgroundColor: activeTab === tab.id ? '#3498db' : 'transparent',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                <span style={{ marginRight: '10px' }}>{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>

          <div>
            {redditConnected ? (
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  padding: '8px 12px',
                  backgroundColor: '#27ae60',
                  borderRadius: '6px',
                  marginBottom: '8px'
                }}>
                  <span style={{
                    width: '8px',
                    height: '8px',
                    backgroundColor: '#2ecc71',
                    borderRadius: '50%',
                    marginRight: '8px'
                  }}></span>
                  <span style={{ fontSize: '14px' }}>Reddit Connected</span>
                </div>
                {redditUsername && (
                  <div style={{ fontSize: '12px', color: '#bdc3c7', marginBottom: '8px' }}>
                    u/{redditUsername}
                  </div>
                )}
                <button 
                  onClick={testConnection}
                  disabled={loading}
                  style={{
                    width: '100%',
                    padding: '6px 12px',
                    backgroundColor: '#4CAF50',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '12px',
                    marginBottom: '5px'
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
                  padding: '12px 16px',
                  backgroundColor: '#3498db',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '14px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '8px'
                }}
              >
                <span>🔗</span>
                <span>{loading ? 'Connecting...' : 'Connect Reddit'}</span>
              </button>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div style={{ flex: 1, padding: '20px' }}>
          <header style={{
            backgroundColor: 'white',
            padding: '20px 30px',
            borderRadius: '8px',
            marginBottom: '20px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center'
          }}>
            <div>
              <h1 style={{ margin: '0 0 5px 0', fontSize: '28px', color: '#2c3e50' }}>
                Reddit Automation Dashboard
              </h1>
              <p style={{ margin: '0 0 10px 0', color: '#7f8c8d', fontSize: '16px' }}>
                REAL AI-powered Reddit automation for {redditUsername || 'your account'}
              </p>
              <div style={{ fontSize: '12px', color: '#95a5a6', display: 'flex', alignItems: 'center', gap: '8px' }}>
                Status: {backendConnected ? 'Live Backend' : 'Offline'}
                <button 
                  onClick={debugConnection}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: '#e74c3c',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    fontSize: '10px'
                  }}
                >
                  Debug
                </button>
              </div>
            </div>
            
            <div style={{ display: 'flex', gap: '10px' }}>
              {userProfile.isConfigured && (
                <button 
                  onClick={startAutoPosting}
                  disabled={loading || !redditConnected}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: loading || !redditConnected ? '#bdc3c7' : '#27ae60',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: loading || !redditConnected ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  <span>🚀</span>
                  <span>Start Auto-Post</span>
                </button>
              )}
            </div>
          </header>

          {/* Tab Content */}
          <main>
            {activeTab === 'setup' && (
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>Profile Configuration</h2>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>
                    Business Domain *
                  </label>
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
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  >
                    {Object.entries(domainConfigs).map(([key, config]) => (
                      <option key={key} value={key}>
                        {config.icon} {config.description}
                      </option>
                    ))}
                  </select>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>
                    Business Type *
                  </label>
                  <input
                    type="text"
                    value={userProfile.businessType}
                    onChange={(e) => setUserProfile(prev => ({
                      ...prev,
                      businessType: e.target.value
                    }))}
                    placeholder={domainConfigs[userProfile.domain]?.sampleBusiness}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                    required
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>
                    Target Audience
                  </label>
                  <select 
                    value={userProfile.targetAudience}
                    onChange={(e) => setUserProfile(prev => ({
                      ...prev,
                      targetAudience: e.target.value
                    }))}
                    style={{
                      width: '100%',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  >
                    {Object.entries(targetAudienceOptions).map(([key, option]) => (
                      <option key={key} value={key}>
                        {option.icon} {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                <button 
                  onClick={saveUserProfile}
                  disabled={!userProfile.businessType}
                  style={{
                    padding: '12px 20px',
                    backgroundColor: userProfile.businessType ? '#27ae60' : '#bdc3c7',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: userProfile.businessType ? 'pointer' : 'not-allowed',
                    fontSize: '14px'
                  }}
                >
                  Save Configuration
                </button>

                {userProfile.isConfigured && (
                  <div style={{
                    marginTop: '20px',
                    padding: '15px',
                    backgroundColor: '#d4edda',
                    borderRadius: '6px',
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
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>Manual Posting with REAL AI</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '20px', marginBottom: '20px', alignItems: 'end' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>Subreddit</label>
                    <select
                      value={manualPost.subreddit}
                      onChange={(e) => setManualPost(prev => ({
                        ...prev,
                        subreddit: e.target.value
                      }))}
                      style={{
                        width: '100%',
                        padding: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px'
                      }}
                    >
                      {subredditOptions.map(sub => (
                        <option key={sub} value={sub}>r/{sub}</option>
                      ))}
                    </select>
                  </div>

                  <button 
                    onClick={generateContent}
                    disabled={manualPost.isGenerating || !userProfile.isConfigured}
                    style={{
                      padding: '12px 20px',
                      backgroundColor: (manualPost.isGenerating || !userProfile.isConfigured) ? '#bdc3c7' : '#3498db',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: (manualPost.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer',
                      fontSize: '14px'
                    }}
                  >
                    {manualPost.isGenerating ? 'Generating...' : 'Generate with AI'}
                  </button>
                </div>

                <form onSubmit={handleManualPost}>
                  <div style={{ marginBottom: '15px' }}>
                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>Post Title</label>
                    <input
                      type="text"
                      value={manualPost.title}
                      onChange={(e) => setManualPost(prev => ({
                        ...prev,
                        title: e.target.value
                      }))}
                      placeholder="Enter your post title..."
                      style={{
                        width: '100%',
                        padding: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px'
                      }}
                      required
                    />
                  </div>

                  <div style={{ marginBottom: '20px' }}>
                    <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>Post Content</label>
                    <textarea
                      value={manualPost.content}
                      onChange={(e) => setManualPost(prev => ({
                        ...prev,
                        content: e.target.value
                      }))}
                      placeholder="Enter your post content..."
                      rows="8"
                      style={{
                        width: '100%',
                        padding: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px',
                        resize: 'vertical'
                      }}
                      required
                    />
                  </div>

                  <button 
                    type="submit" 
                    disabled={loading || !redditConnected || !manualPost.title || !manualPost.content}
                    style={{
                      padding: '12px 24px',
                      backgroundColor: (loading || !redditConnected || !manualPost.title || !manualPost.content) ? '#bdc3c7' : '#27ae60',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: (loading || !redditConnected || !manualPost.title || !manualPost.content) ? 'not-allowed' : 'pointer',
                      fontSize: '16px',
                      fontWeight: 'bold'
                    }}
                  >
                    {loading ? 'Posting...' : `Post as ${redditUsername || 'Reddit User'}`}
                  </button>
                </form>
              </div>
            )}

            {activeTab === 'schedule' && (
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>Auto-Post Schedule</h2>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '6px', fontWeight: 'bold', color: '#34495e' }}>Posts Per Day</label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={autoPostConfig.postsPerDay}
                    onChange={(e) => setAutoPostConfig(prev => ({
                      ...prev,
                      postsPerDay: parseInt(e.target.value) || 1
                    }))}
                    style={{
                      width: '200px',
                      padding: '10px',
                      border: '1px solid #ddd',
                      borderRadius: '4px',
                      fontSize: '14px'
                    }}
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <h4 style={{ color: '#2c3e50', marginBottom: '10px' }}>Posting Times</h4>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'center', marginBottom: '15px' }}>
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
                      style={{
                        padding: '10px',
                        border: '1px solid #ddd',
                        borderRadius: '4px',
                        fontSize: '14px'
                      }}
                    />
                    <button
                      onClick={() => {
                        const now = new Date();
                        now.setMinutes(now.getMinutes() + 2);
                        const testTime = now.toTimeString().slice(0, 5);
                        if (!autoPostConfig.postingTimes.includes(testTime)) {
                          setAutoPostConfig(prev => ({
                            ...prev,
                            postingTimes: [...prev.postingTimes, testTime].sort()
                          }));
                        }
                      }}
                      type="button"
                      style={{
                        padding: '10px 16px',
                        backgroundColor: '#f39c12',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        cursor: 'pointer',
                        fontSize: '14px'
                      }}
                    >
                      Add Test Time (+2min)
                    </button>
                  </div>

                  {autoPostConfig.postingTimes.length > 0 && (
                    <div>
                      <h5 style={{ color: '#2c3e50' }}>Scheduled Times ({autoPostConfig.postingTimes.length})</h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {autoPostConfig.postingTimes.map(time => (
                          <div key={time} style={{
                            display: 'flex',
                            alignItems: 'center',
                            backgroundColor: '#ecf0f1',
                            padding: '6px 12px',
                            borderRadius: '20px',
                            fontSize: '14px'
                          }}>
                            <span>{time}</span>
                            <button 
                              onClick={() => setAutoPostConfig(prev => ({
                                ...prev,
                                postingTimes: prev.postingTimes.filter(t => t !== time)
                              }))}
                              style={{
                                background: 'none',
                                border: 'none',
                                marginLeft: '8px',
                                cursor: 'pointer',
                                fontSize: '16px',
                                color: '#e74c3c'
                              }}
                            >
                              ×
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'status' && (
              <div style={{ backgroundColor: 'white', padding: '25px', borderRadius: '8px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                <h2 style={{ marginBottom: '20px', color: '#2c3e50' }}>System Status & Analytics</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  <div style={{
                    padding: '20px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '6px',
                    border: '1px solid #e9ecef'
                  }}>
                    <h3 style={{ marginTop: 0, color: '#2c3e50' }}>Reddit Connection</h3>
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

                  <div style={{
                    padding: '20px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '6px',
                    border: '1px solid #e9ecef'
                  }}>
                    <h3 style={{ marginTop: 0, color: '#2c3e50' }}>Profile Status</h3>
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

                  <div style={{
                    padding: '20px',
                    backgroundColor: '#f8f9fa',
                    borderRadius: '6px',
                    border: '1px solid #e9ecef'
                  }}>
                    <h3 style={{ marginTop: 0, color: '#2c3e50' }}>Automation Status</h3>
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

                <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '6px', marginBottom: '20px' }}>
                  <h3 style={{ marginTop: 0, color: '#2c3e50' }}>Today's Performance</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '20px' }}>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#27ae60' }}>
                        {performanceData.postsToday}
                      </div>
                      <div style={{ color: '#7f8c8d', fontSize: '14px' }}>Posts Today</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#3498db' }}>
                        {performanceData.totalKarma}
                      </div>
                      <div style={{ color: '#7f8c8d', fontSize: '14px' }}>Total Karma</div>
                    </div>
                    <div style={{ textAlign: 'center' }}>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#e67e22' }}>
                        {performanceData.successRate}%
                      </div>
                      <div style={{ color: '#7f8c8d', fontSize: '14px' }}>Success Rate</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </main>
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
};

export default function App() {
  return (
    <ErrorBoundary>
      <RedditAutomation />
    </ErrorBoundary>
  );
}
                      import React, { useState, useEffect, useCallback } from 'react';

// Error Boundary Component
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
      return (
        <div style={{ padding: '20px', textAlign: 'center' }}>
          <h2>Something went wrong.</h2>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      );
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
    language: 'en',
    contentStyle: 'engaging',
    isConfigured: false
  });

  const [manualPost, setManualPost] = useState({
    subreddit: 'test',
    title: '',
    content: '',
    generatedContent: '',
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
      subreddits: ['JEE', 'NEET', 'IndianStudents', 'india', 'AskReddit', 'StudyTips'],
      sampleBusiness: 'JEE coaching institute in Delhi',
      icon: '🎓',
      description: 'Educational services and exam preparation'
    },
    restaurant: {
      subreddits: ['IndianFood', 'food', 'bangalore', 'mumbai', 'delhi', 'recipes'],
      sampleBusiness: 'Traditional Indian restaurant in Mumbai',
      icon: '🍽️',
      description: 'Food, restaurants, and culinary experiences'
    },
    tech: {
      subreddits: ['developersIndia', 'programming', 'india', 'bangalore', 'coding', 'webdev'],
      sampleBusiness: 'AI automation platform for businesses',
      icon: '💻',
      description: 'Technology, programming, and software development'
    },
    health: {
      subreddits: ['fitness', 'HealthyFood', 'india', 'mentalhealth', 'nutrition', 'wellness'],
      sampleBusiness: 'Fitness coaching and nutrition center',
      icon: '💚',
      description: 'Health, fitness, and wellness services'
    },
    business: {
      subreddits: ['entrepreneur', 'IndiaInvestments', 'business', 'india', 'startup', 'smallbusiness'],
      sampleBusiness: 'Business consulting firm for startups',
      icon: '💼',
      description: 'Business, entrepreneurship, and investments'
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

  const subredditOptions = [
    'test', 'india', 'developersIndia', 'programming', 'AskReddit',
    'explainlikeimfive', 'NoStupidQuestions', 'bangalore', 'mumbai',
    'JEE', 'NEET', 'IndianStudents', 'IndianFood', 'food'
  ];

  // FIXED: Unique notification ID generation
  const showNotification = useCallback((message, type = 'success') => {
    console.log(`📢 ${type.toUpperCase()}: ${message}`);
    const notification = { 
      id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, // FIXED: Unique ID
      message, 
      type 
    };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== notification.id));
    }, 5000);
  }, []);

  // Enhanced API request with proper error handling
  const makeAPIRequest = useCallback(async (endpoint, method = 'GET', data = null) => {
    try {
      console.log(`🌐 API Request: ${method} ${endpoint}`);
      
      const headers = {
        'Content-Type': 'application/json'
      };

      if (sessionId) {
        headers['x-session-id'] = sessionId;
      }

      const config = { method, headers };
      if (data && method !== 'GET') {
        config.body = JSON.stringify({ ...data, use_real_ai: true, test_mode: false });
      }

      try {
        const response = await fetch(`http://localhost:8000${endpoint}`, config);
        const result = await response.json();
        
        if (result.success) {
          setBackendConnected(true);
          setConnectionError('');
          return result;
        } else {
          console.warn('API request failed:', result);
          return result;
        }
      } catch (backendError) {
        console.warn('Backend not available:', backendError.message);
        setBackendConnected(false);
        setConnectionError('Backend not available - check if server is running on port 8000');
        throw backendError;
      }
    } catch (error) {
      console.error('API Request failed:', error);
      return { success: false, error: error.message };
    }
  }, [sessionId]);

  // Initialize app
  useEffect(() => {
    const initApp = async () => {
      try {
        console.log('🚀 Initializing Reddit Automation App...');
        
        // Handle OAuth callback
        const urlParams = new URLSearchParams(window.location.search);
        const redditConnectedParam = urlParams.get('reddit_connected');
        const usernameParam = urlParams.get('username');
        const sessionIdParam = urlParams.get('session_id');

        if (redditConnectedParam === 'true' && sessionIdParam) {
          setSessionId(sessionIdParam);
          setRedditUsername(usernameParam || 'demo_user');
          setRedditConnected(true);
          showNotification(`🎉 Reddit connected! Welcome ${usernameParam}!`, 'success');
          console.log(`✅ OAuth success: ${usernameParam} connected`);
          window.history.replaceState({}, '', window.location.pathname);
        } else {
          const savedSessionId = localStorage.getItem('reddit_session_id');
          const savedUsername = localStorage.getItem('reddit_username');
          
          if (savedSessionId) {
            setSessionId(savedSessionId);
            if (savedUsername) {
              setRedditUsername(savedUsername);
              setRedditConnected(true);
            }
          } else {
            const response = await makeAPIRequest('/api/auth/create-session', 'POST');
            if (response.success) {
              setSessionId(response.session_id);
              localStorage.setItem('reddit_session_id', response.session_id);
            }
          }
        }

        const savedProfile = localStorage.getItem('redditUserProfile');
        if (savedProfile) {
          setUserProfile(JSON.parse(savedProfile));
        }

        const healthResponse = await makeAPIRequest('/health');
        if (healthResponse.success) {
          setBackendConnected(true);
          console.log('✅ Backend connected');
        }

        console.log('✅ App initialization completed');
      } catch (error) {
        console.error('❌ App initialization failed:', error);
        showNotification('App initialization failed', 'error');
      }
    };

    initApp();
  }, [makeAPIRequest, showNotification]);

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
      console.error('Failed to save profile:', error);
      showNotification('Failed to save profile', 'error');
    }
  }, [userProfile, domainConfigs, showNotification]);

  const handleRedditConnect = useCallback(async () => {
    try {
      setLoading(true);
      showNotification('Connecting to Reddit...', 'info');
      
      if (!sessionId) {
        const sessionResponse = await makeAPIRequest('/api/auth/create-session', 'POST');
        if (sessionResponse.success) {
          setSessionId(sessionResponse.session_id);
          localStorage.setItem('reddit_session_id', sessionResponse.session_id);
        }
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
  }, [sessionId, makeAPIRequest, showNotification]);

  const testConnection = useCallback(async () => {
    try {
      setLoading(true);
      const response = await makeAPIRequest('/api/reddit/test-connection');
      if (response.success) {
        showNotification(`✅ Connection test successful for ${response.username}!`, 'success');
      } else {
        showNotification('Connection test failed: ' + response.error, 'error');
      }
    } catch (error) {
      showNotification('Test failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAPIRequest, showNotification]);

  const generateContent = useCallback(async () => {
    if (!userProfile.businessType) {
      showNotification('Please configure your profile first', 'error');
      return;
    }

    try {
      setManualPost(prev => ({ ...prev, isGenerating: true }));
      showNotification('🤖 Generating content with REAL AI...', 'info');
      
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
          generatedContent: response.content_preview,
          title: response.post_details?.title || 'Generated Title',
          content: response.content_preview
        }));
        const aiService = response.ai_service || 'AI';
        showNotification(`✅ Content generated using ${aiService}!`, 'success');
      } else {
        showNotification(response.error || 'Content generation failed', 'error');
      }
    } catch (error) {
      showNotification('Generation failed: ' + error.message, 'error');
    } finally {
      setManualPost(prev => ({ ...prev, isGenerating: false }));
    }
  }, [userProfile, manualPost.subreddit, makeAPIRequest, showNotification]);

  const handleManualPost = useCallback(async (e) => {
    e.preventDefault();
    
    if (!manualPost.title || !manualPost.content) {
      showNotification('Please enter both title and content', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('📮 Posting to Reddit...', 'info');
      
      const response = await makeAPIRequest('/api/reddit/post', 'POST', {
        subreddit: manualPost.subreddit,
        title: manualPost.title,
        content: manualPost.content,
        contentType: 'text'
      });
      
      if (response.success) {
        showNotification(`🎉 Post created successfully as ${redditUsername}!`, 'success');
        if (response.post_url) {
          showNotification(`🔗 View post: ${response.post_url}`, 'info');