import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'https://agentic-u5lx.onrender.com';

const DOMAIN_CONFIGS = {
  education: { icon: '🎓', description: 'Educational services', sampleBusiness: 'JEE coaching institute' },
  restaurant: { icon: '🍽️', description: 'Food & restaurants', sampleBusiness: 'Traditional Indian restaurant' },
  tech: { icon: '💻', description: 'Technology & programming', sampleBusiness: 'AI automation platform' },
  health: { icon: '💚', description: 'Health & wellness', sampleBusiness: 'Fitness coaching center' },
  business: { icon: '💼', description: 'Business & entrepreneurship', sampleBusiness: 'Business consulting firm' }
};

const TARGET_AUDIENCES = {
  'indian_students': { label: 'Indian Students', icon: '🎓' },
  'food_lovers': { label: 'Food Lovers', icon: '🍕' },
  'tech_professionals': { label: 'Tech Professionals', icon: '💻' },
  'health_conscious': { label: 'Health Conscious', icon: '💚' },
  'entrepreneurs': { label: 'Entrepreneurs', icon: '💼' },
  'general_users': { label: 'General Users', icon: '👥' }
};

const CONTENT_STYLES = {
  'engaging': 'Engaging & Interactive',
  'informative': 'Informative & Educational',
  'promotional': 'Promotional & Marketing',
  'helpful': 'Helpful & Supportive',
  'casual': 'Casual & Friendly',
  'professional': 'Professional & Formal'
};

const ConnectionCard = ({ platform, connected, username, pages, onConnect, onTest, loading, color }) => (
  <div style={{ padding: '20px', background: 'rgba(255,255,255,0.1)', borderRadius: '16px', marginBottom: '16px', border: `2px solid ${color}30` }}>
    {connected ? (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', borderRadius: '10px', background: 'rgba(34, 197, 94, 0.15)', color: '#047857', marginBottom: '12px', fontSize: '16px', fontWeight: '700' }}>
          <div style={{ width: '10px', height: '10px', background: '#22c55e', borderRadius: '50%' }}></div>
          ✅ {platform} Connected
        </div>
        {username && <div style={{ fontSize: '14px', color: '#059669', margin: '0 0 12px 18px', background: 'rgba(34, 197, 94, 0.1)', padding: '6px 12px', borderRadius: '16px', display: 'inline-block', fontWeight: '600' }}>{platform === 'Facebook' ? username : `@${username}`}</div>}
        {pages && pages.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{ fontSize: '12px', color: '#6b7280', marginBottom: '6px', fontWeight: '600' }}>Connected Pages ({pages.length}):</div>
            {pages.slice(0, 2).map(page => (
              <div key={page.id} style={{ fontSize: '11px', color: '#4b5563', margin: '2px 0 2px 18px', background: 'rgba(59, 130, 246, 0.1)', padding: '2px 8px', borderRadius: '10px', display: 'inline-block', marginRight: '6px' }}>📄 {page.name}</div>
            ))}
            {pages.length > 2 && <div style={{ fontSize: '11px', color: '#6b7280', marginLeft: '18px' }}>+{pages.length - 2} more pages</div>}
          </div>
        )}
        <button onClick={onTest} disabled={loading} style={{ width: '100%', padding: '10px 16px', fontSize: '14px', fontWeight: '700', background: loading ? '#d1d5db' : 'linear-gradient(135deg, #22c55e, #16a34a)', color: 'white', border: 'none', borderRadius: '10px', cursor: loading ? 'not-allowed' : 'pointer' }}>
          {loading ? 'Testing...' : 'Test Connection'}
        </button>
      </div>
    ) : (
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', borderRadius: '10px', background: 'rgba(239, 68, 68, 0.15)', color: '#dc2626', marginBottom: '12px', fontSize: '16px', fontWeight: '700' }}>
          <div style={{ width: '10px', height: '10px', background: '#ef4444', borderRadius: '50%' }}></div>
          ❌ {platform} Not Connected
        </div>
        <button onClick={onConnect} disabled={loading} style={{ width: '100%', padding: '10px 16px', fontSize: '14px', fontWeight: '700', background: loading ? '#d1d5db' : `linear-gradient(135deg, ${color}, ${color}dd)`, color: 'white', border: 'none', borderRadius: '10px', cursor: loading ? 'not-allowed' : 'pointer' }}>
          {loading ? 'Connecting...' : `Connect ${platform}`}
        </button>
      </div>
    )}
  </div>
);

const SocialMediaAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  const [facebookConnected, setFacebookConnected] = useState(false);
  const [facebookUsername, setFacebookUsername] = useState('');
  const [facebookPages, setFacebookPages] = useState([]);
  const [instagramConnected, setInstagramConnected] = useState(false);
  const [instagramUsername, setInstagramUsername] = useState('');
  
  const [userProfile, setUserProfile] = useState({
    domain: 'tech',
    businessType: 'AI automation platform',
    businessDescription: 'We help businesses automate their social media presence',
    targetAudience: 'tech_professionals',
    contentStyle: 'engaging',
    isConfigured: false
  });
  
  const [manualPost, setManualPost] = useState({
    platform: 'facebook',
    title: '',
    content: '',
    pageId: '',
    imageUrl: '',
    isGenerating: false
  });
  
  const [autoPostConfig, setAutoPostConfig] = useState({
    facebook: { enabled: false, postsPerDay: 3, postingTimes: [] },
    instagram: { enabled: false, postsPerDay: 2, postingTimes: [] }
  });
  
  const [performanceData, setPerformanceData] = useState({
    postsToday: 0,
    totalEngagement: 0,
    successRate: 95
  });

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, message, type };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notification.id)), 5000);
  }, []);

  useEffect(() => {
    if (!user?.email) return;
    
    const initKey = `social_init_${user.email}`;
    if (localStorage.getItem(initKey)) return;
    localStorage.setItem(initKey, 'true');
    
    const initApp = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const fbConnected = urlParams.get('facebook_connected');
      const igConnected = urlParams.get('instagram_connected');
      const username = urlParams.get('username');
      const error = urlParams.get('error');

      if (error) {
        showNotification(`Connection failed: ${error}`, 'error');
        window.history.replaceState({}, '', window.location.pathname);
        return;
      }

      if (fbConnected === 'true' && username) {
        setFacebookConnected(true);
        setFacebookUsername(username);
        updateUser({ facebook_connected: true, facebook_username: username });
        showNotification(`Facebook connected! Welcome ${username}!`, 'success');
        window.history.replaceState({}, '', window.location.pathname);
        return;
      }

      if (igConnected === 'true' && username) {
        setInstagramConnected(true);
        setInstagramUsername(username);
        updateUser({ instagram_connected: true, instagram_username: username });
        showNotification(`Instagram connected! Welcome @${username}!`, 'success');
        window.history.replaceState({}, '', window.location.pathname);
        return;
      }

      try {
        const [fbResponse, igResponse] = await Promise.all([
          makeAuthenticatedRequest('/api/facebook/connection-status'),
          makeAuthenticatedRequest('/api/instagram/connection-status')
        ]);
        
        const fbResult = await fbResponse.json();
        const igResult = await igResponse.json();
        
        if (fbResult.success && fbResult.connected) {
          setFacebookConnected(true);
          setFacebookUsername(fbResult.username);
          setFacebookPages(fbResult.pages || []);
        }
        
        if (igResult.success && igResult.connected) {
          setInstagramConnected(true);
          setInstagramUsername(igResult.username);
        }
      } catch (error) {
        console.error('Failed to check connections:', error);
      }

      try {
        const savedProfile = localStorage.getItem('socialUserProfile');
        if (savedProfile) {
          const profile = JSON.parse(savedProfile);
          setUserProfile(profile);
        }
      } catch (error) {
        console.error('Error loading profile:', error);
      }
    };

    initApp();
  }, [user, makeAuthenticatedRequest, updateUser, showNotification]);

  const handleConnect = useCallback(async (platform) => {
    try {
      setLoading(true);
      showNotification(`Connecting to ${platform}...`, 'info');
      
      const response = await makeAuthenticatedRequest(`/api/oauth/${platform}/authorize`);
      const result = await response.json();
      
      if (result.success && result.redirect_url) {
        window.location.href = result.redirect_url;
      } else {
        showNotification(result.error || `Failed to start ${platform} authorization`, 'error');
      }
    } catch (error) {
      showNotification(`Connection failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAuthenticatedRequest, showNotification]);

  const testConnection = useCallback(async (platform) => {
    try {
      setLoading(true);
      const response = await makeAuthenticatedRequest(`/api/${platform}/connection-status`);
      const result = await response.json();
      
      if (result.success && result.connected) {
        showNotification(`${platform} connection verified for ${result.username}!`, 'success');
      } else {
        showNotification(`${platform} not connected`, 'error');
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
      showNotification('Generating human-like content with AI...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/test-auto-post', {
        method: 'POST',
        body: JSON.stringify({
          platform: manualPost.platform,
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          content_style: userProfile.contentStyle
        })
      });

      const result = await response.json();

      if (result.success) {
        setManualPost(prev => ({
          ...prev,
          title: result.post_details?.title || result.content_preview.split('\n')[0] || 'Generated Title',
          content: result.content_preview
        }));
        showNotification(`Human-like content generated using ${result.ai_service}! (${result.human_score || 95}% human authenticity)`, 'success');
      } else {
        showNotification(result.error || 'AI content generation failed', 'error');
      }
    } catch (error) {
      showNotification('AI generation failed: ' + error.message, 'error');
    } finally {
      setManualPost(prev => ({ ...prev, isGenerating: false }));
    }
  }, [userProfile, manualPost.platform, makeAuthenticatedRequest, showNotification]);

  const handleManualPost = useCallback(async (e) => {
    e.preventDefault();
    
    if (!manualPost.title || !manualPost.content) {
      showNotification('Please enter both title and content', 'error');
      return;
    }

    const platformConnected = manualPost.platform === 'facebook' ? facebookConnected : instagramConnected;
    if (!platformConnected) {
      showNotification(`Please connect your ${manualPost.platform} account first`, 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification(`Posting to ${manualPost.platform}...`, 'info');
      
      const postData = {
        platform: manualPost.platform,
        title: manualPost.title,
        content: manualPost.content,
        page_id: manualPost.pageId,
        image_url: manualPost.imageUrl
      };
      
      const response = await makeAuthenticatedRequest('/api/post/manual', {
        method: 'POST',
        body: JSON.stringify(postData)
      });
      
      const result = await response.json();
      
      if (result.success) {
        const username = manualPost.platform === 'facebook' ? facebookUsername : instagramUsername;
        showNotification(`Post created successfully as ${username}!`, 'success');
        if (result.post_url) {
          showNotification(`View post: ${result.post_url}`, 'info');
        }
        
        setPerformanceData(prev => ({ ...prev, postsToday: prev.postsToday + 1 }));
        setManualPost({
          platform: manualPost.platform,
          title: '',
          content: '',
          pageId: '',
          imageUrl: '',
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
  }, [manualPost, makeAuthenticatedRequest, facebookConnected, instagramConnected, facebookUsername, instagramUsername, showNotification]);

  const saveUserProfile = useCallback(() => {
    try {
      const profileToSave = { ...userProfile, isConfigured: true };
      localStorage.setItem('socialUserProfile', JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('Profile saved successfully!', 'success');
    } catch (error) {
      showNotification('Failed to save profile', 'error');
    }
  }, [userProfile, showNotification]);

  const startAutomation = useCallback(async (platform) => {
    if (!userProfile.isConfigured) {
      showNotification('Please configure your profile first', 'error');
      setActiveTab('setup');
      return;
    }

    const platformConnected = platform === 'facebook' ? facebookConnected : instagramConnected;
    if (!platformConnected) {
      showNotification(`Please connect your ${platform} account first`, 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification(`Setting up ${platform} automation...`, 'info');
      
      const config = {
        platform,
        domain: userProfile.domain,
        business_type: userProfile.businessType,
        business_description: userProfile.businessDescription,
        target_audience: userProfile.targetAudience,
        language: userProfile.language,
        content_style: userProfile.contentStyle,
        posts_per_day: autoPostConfig[platform].postsPerDay,
        posting_times: autoPostConfig[platform].postingTimes
      };

      const response = await makeAuthenticatedRequest('/api/automation/setup-auto-posting', {
        method: 'POST',
        body: JSON.stringify(config)
      });
      
      const result = await response.json();
      
      if (result.success) {
        setAutoPostConfig(prev => ({
          ...prev,
          [platform]: { ...prev[platform], enabled: true }
        }));
        const username = platform === 'facebook' ? facebookUsername : instagramUsername;
        showNotification(`${platform} auto-posting started for ${username}! Next post: ${result.next_post_time || 'scheduled'}`, 'success');
      } else {
        showNotification(result.error || 'Automation setup failed', 'error');
      }
    } catch (error) {
      showNotification('Setup failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [userProfile, facebookConnected, instagramConnected, autoPostConfig, makeAuthenticatedRequest, facebookUsername, instagramUsername, showNotification]);

  const addTime = (platform) => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 5);
    const testTime = now.toTimeString().slice(0, 5);
    if (!autoPostConfig[platform].postingTimes.includes(testTime)) {
      setAutoPostConfig(prev => ({
        ...prev,
        [platform]: {
          ...prev[platform],
          postingTimes: [...prev[platform].postingTimes, testTime].sort()
        }
      }));
      showNotification(`Test time added for ${platform} (+5 minutes)`, 'info');
    }
  };

  const removeTime = (platform, time) => {
    setAutoPostConfig(prev => ({
      ...prev,
      [platform]: {
        ...prev[platform],
        postingTimes: prev[platform].postingTimes.filter(t => t !== time)
      }
    }));
  };

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex' }}>
      
      {/* Notifications */}
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 10000, display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}>
        {notifications.map(notification => (
          <div key={notification.id} style={{ padding: '16px 20px', borderRadius: '12px', backdropFilter: 'blur(15px)', color: 'white', fontWeight: '600', boxShadow: '0 8px 25px rgba(0, 0, 0, 0.3)', background: notification.type === 'success' ? 'rgba(34, 197, 94, 0.9)' : notification.type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(59, 130, 246, 0.9)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px', fontSize: '14px', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
            <span>{notification.message}</span>
            <button onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))} style={{ background: 'none', border: 'none', color: 'white', fontSize: '18px', cursor: 'pointer', padding: '4px', opacity: 0.8 }}>×</button>
          </div>
        ))}
      </div>

      {/* Loading Overlay */}
      {loading && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(8px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999 }}>
          <div style={{ background: 'white', padding: '40px', borderRadius: '16px', textAlign: 'center', boxShadow: '0 15px 50px rgba(0, 0, 0, 0.3)' }}>
            <div style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #667eea', borderRadius: '50%', width: '50px', height: '50px', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
            <p style={{ marginTop: '20px', color: '#666', fontSize: '16px', fontWeight: '600' }}>Processing your request...</p>
          </div>
        </div>
      )}

      {/* Sidebar */}
      <div style={{ width: '320px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(15px)', height: '100vh', position: 'fixed', display: 'flex', flexDirection: 'column', boxShadow: '4px 0 25px rgba(0, 0, 0, 0.1)', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
        
        <div style={{ padding: '40px 28px', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', textAlign: 'center', background: 'linear-gradient(135deg, #667eea, #764ba2)' }}>
          <h2 style={{ fontSize: '26px', fontWeight: '700', color: 'white', margin: 0, marginBottom: '6px' }}>Facebook & Instagram</h2>
          <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Multi-Platform Automation</div>
          <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.8)', marginTop: '4px' }}>Welcome, {user?.name}</div>
        </div>
        
        <nav style={{ flex: 1, padding: '28px 20px' }}>
          {[
            { id: 'setup', icon: '⚙️', label: 'Profile Setup', desc: 'Configure AI settings' },
            { id: 'manual', icon: '✍️', label: 'Manual Post', desc: 'Create & post now' },
            { id: 'schedule', icon: '📅', label: 'Auto Schedule', desc: 'Set posting times' },
            { id: 'status', icon: '📊', label: 'Analytics', desc: 'Performance metrics' }
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '16px', padding: '20px 24px', border: 'none', background: activeTab === tab.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'none', color: activeTab === tab.id ? 'white' : '#666', textAlign: 'left', borderRadius: '16px', cursor: 'pointer', marginBottom: '12px', fontSize: '16px', transform: activeTab === tab.id ? 'translateX(6px)' : 'none', boxShadow: activeTab === tab.id ? '0 6px 20px rgba(102, 126, 234, 0.4)' : 'none', transition: 'all 0.3s ease' }}>
              <span style={{ fontSize: '20px' }}>{tab.icon}</span>
              <div>
                <div style={{ fontWeight: '600', fontSize: '16px' }}>{tab.label}</div>
                <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '2px' }}>{tab.desc}</div>
              </div>
            </button>
          ))}
        </nav>

        {/* Connection Status */}
        <div style={{ padding: '24px 28px', borderTop: '1px solid rgba(0, 0, 0, 0.05)' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#374151', marginBottom: '16px' }}>Platform Connections</h3>
          <ConnectionCard
            platform="Facebook"
            connected={facebookConnected}
            username={facebookUsername}
            pages={facebookPages}
            onConnect={() => handleConnect('facebook')}
            onTest={() => testConnection('facebook')}
            loading={loading}
            color="#4267B2"
          />
          <ConnectionCard
            platform="Instagram"
            connected={instagramConnected}
            username={instagramUsername}
            onConnect={() => handleConnect('instagram')}
            onTest={() => testConnection('instagram')}
            loading={loading}
            color="#E4405F"
          />
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, marginLeft: '320px', background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)' }}>
        
        <header style={{ padding: '40px 48px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(15px)', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '36px', fontWeight: '700', color: '#333', marginBottom: '8px' }}>Social Media Automation</h1>
            <p style={{ fontSize: '18px', color: '#666', margin: 0 }}>AI-powered Facebook & Instagram automation with human-like content</p>
          </div>
          
          <div style={{ display: 'flex', gap: '16px' }}>
            {userProfile.isConfigured && (
              <>
                <button onClick={() => startAutomation('facebook')} disabled={loading || !facebookConnected} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '16px 28px', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: loading || !facebookConnected ? 'not-allowed' : 'pointer', background: loading || !facebookConnected ? '#bdc3c7' : 'linear-gradient(135deg, #4267B2, #365899)', color: 'white', boxShadow: '0 6px 20px rgba(66, 103, 178, 0.4)', transition: 'all 0.3s ease' }}>
                  <span>📘</span><span>Start FB Auto</span>
                </button>
                <button onClick={() => startAutomation('instagram')} disabled={loading || !instagramConnected} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '16px 28px', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: loading || !instagramConnected ? 'not-allowed' : 'pointer', background: loading || !instagramConnected ? '#bdc3c7' : 'linear-gradient(135deg, #E4405F, #C13584)', color: 'white', boxShadow: '0 6px 20px rgba(228, 64, 95, 0.4)', transition: 'all 0.3s ease' }}>
                  <span>📸</span><span>Start IG Auto</span>
                </button>
              </>
            )}
          </div>
        </header>

        {/* Tab Content */}
        <div style={{ padding: '40px 48px' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(15px)', borderRadius: '24px', padding: '40px', boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)', border: '1px solid rgba(255, 255, 255, 0.2)', maxWidth: '1200px', margin: '0 auto' }}>
            
            {/* Setup Tab */}
            {activeTab === 'setup' && (
              <div>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '40px', textAlign: 'center' }}>AI Profile Configuration</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Business Domain</label>
                    <select value={userProfile.domain} onChange={(e) => { const domain = e.target.value; const config = DOMAIN_CONFIGS[domain]; setUserProfile(prev => ({ ...prev, domain, businessType: config?.sampleBusiness || prev.businessType })); }} style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500' }}>
                      {Object.entries(DOMAIN_CONFIGS).map(([key, config]) => (
                        <option key={key} value={key}>{config.icon} {config.description}</option>
                      ))}
                    </select>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Content Style</label>
                    <select value={userProfile.contentStyle} onChange={(e) => setUserProfile(prev => ({ ...prev, contentStyle: e.target.value }))} style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500' }}>
                      {Object.entries(CONTENT_STYLES).map(([key, style]) => (
                        <option key={key} value={key}>{style}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
                  <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Business Type</label>
                  <input type="text" value={userProfile.businessType} onChange={(e) => setUserProfile(prev => ({ ...prev, businessType: e.target.value }))} placeholder={DOMAIN_CONFIGS[userProfile.domain]?.sampleBusiness} style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500' }} />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
                  <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Business Description</label>
                  <textarea value={userProfile.businessDescription} onChange={(e) => setUserProfile(prev => ({ ...prev, businessDescription: e.target.value }))} placeholder="Describe your business, services, and unique value proposition..." rows="4" style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', resize: 'vertical', fontWeight: '500', lineHeight: 1.5 }} />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '32px' }}>
                  <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Target Audience</label>
                  <select value={userProfile.targetAudience} onChange={(e) => setUserProfile(prev => ({ ...prev, targetAudience: e.target.value }))} style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500' }}>
                    {Object.entries(TARGET_AUDIENCES).map(([key, option]) => (
                      <option key={key} value={key}>{option.icon} {option.label}</option>
                    ))}
                  </select>
                </div>

                <div style={{ textAlign: 'center', marginTop: '40px' }}>
                  <button onClick={saveUserProfile} disabled={!userProfile.businessType} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', padding: '20px 40px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: userProfile.businessType ? 'pointer' : 'not-allowed', background: userProfile.businessType ? 'linear-gradient(135deg, #667eea, #764ba2)' : '#bdc3c7', color: 'white', boxShadow: '0 6px 20px rgba(102, 126, 234, 0.4)', margin: '0 auto', transition: 'all 0.3s ease' }}>
                    <span>✅</span>Save Configuration
                  </button>
                </div>

                {userProfile.isConfigured && (
                  <div style={{ marginTop: '24px', padding: '20px', backgroundColor: 'rgba(34, 197, 94, 0.1)', borderRadius: '16px', border: '2px solid rgba(34, 197, 94, 0.3)' }}>
                    <div style={{ color: '#155724', fontWeight: '700', marginBottom: '8px', fontSize: '18px' }}>Profile Configured Successfully!</div>
                    <div style={{ color: '#155724', fontSize: '16px' }}>AI is ready for human-like content generation on Facebook & Instagram.</div>
                  </div>
                )}
              </div>
            )}

            {/* Manual Post Tab */}
            {activeTab === 'manual' && (
              <div>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '40px', textAlign: 'center' }}>Create & Post with AI</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '24px', marginBottom: '24px', alignItems: 'end' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Platform</label>
                    <select value={manualPost.platform} onChange={(e) => setManualPost(prev => ({ ...prev, platform: e.target.value }))} style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500' }}>
                      <option value="facebook">📘 Facebook</option>
                      <option value="instagram">📸 Instagram</option>
                    </select>
                  </div>

                  <button onClick={generateContent} disabled={manualPost.isGenerating || !userProfile.isConfigured} style={{ padding: '20px 32px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: (manualPost.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer', background: (manualPost.isGenerating || !userProfile.isConfigured) ? '#bdc3c7' : 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', boxShadow: '0 6px 20px rgba(102, 126, 234, 0.4)', transition: 'all 0.3s ease' }}>
                    {manualPost.isGenerating ? 'Generating...' : '🤖 Generate Human-like Content'}
                  </button>
                </div>

                <form onSubmit={handleManualPost}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
                    <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Post Title</label>
                    <input type="text" value={manualPost.title} onChange={(e) => setManualPost(prev => ({ ...prev, title: e.target.value }))} placeholder="Enter your post title..." style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500' }} required />
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
                    <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Post Content</label>
                    <textarea value={manualPost.content} onChange={(e) => setManualPost(prev => ({ ...prev, content: e.target.value }))} placeholder="Enter your post content or generate with AI..." rows="10" style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', resize: 'vertical', fontWeight: '500', lineHeight: 1.6 }} required />
                  </div>

                  {manualPost.platform === 'facebook' && facebookPages.length > 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '24px' }}>
                      <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Facebook Page</label>
                      <select value={manualPost.pageId} onChange={(e) => setManualPost(prev => ({ ...prev, pageId: e.target.value }))} style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500' }}>
                        <option value="">Select a page</option>
                        {facebookPages.map(page => (
                          <option key={page.id} value={page.id}>{page.name}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '32px' }}>
                    <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Image URL (Optional)</label>
                    <input type="url" value={manualPost.imageUrl} onChange={(e) => setManualPost(prev => ({ ...prev, imageUrl: e.target.value }))} placeholder="https://example.com/image.jpg" style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500' }} />
                  </div>

                  <div style={{ textAlign: 'center' }}>
                    <button type="submit" disabled={loading || (manualPost.platform === 'facebook' ? !facebookConnected : !instagramConnected) || !manualPost.title || !manualPost.content} style={{ padding: '20px 40px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: 'pointer', background: 'linear-gradient(135deg, #34d399, #10b981)', color: 'white', boxShadow: '0 6px 20px rgba(52, 211, 153, 0.4)', transition: 'all 0.3s ease' }}>
                      {loading ? 'Posting...' : `🚀 Post to ${manualPost.platform}`}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {/* Schedule Tab */}
            {activeTab === 'schedule' && (
              <div>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '40px', textAlign: 'center' }}>Auto-Post Schedule Configuration</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                  {['facebook', 'instagram'].map(platform => (
                    <div key={platform} style={{ padding: '32px', background: 'rgba(255,255,255,0.7)', borderRadius: '20px', border: `3px solid ${platform === 'facebook' ? '#4267B2' : '#E4405F'}` }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                        <span style={{ fontSize: '40px' }}>{platform === 'facebook' ? '📘' : '📸'}</span>
                        <h3 style={{ margin: 0, color: platform === 'facebook' ? '#4267B2' : '#E4405F', fontSize: '24px', fontWeight: '700' }}>{platform === 'facebook' ? 'Facebook' : 'Instagram'} Schedule</h3>
                      </div>
                      
                      <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', fontSize: '16px', fontWeight: '700', marginBottom: '12px', color: '#374151' }}>Posts Per Day</label>
                        <input type="number" min="1" max={platform === 'facebook' ? 5 : 3} value={autoPostConfig[platform].postsPerDay} onChange={(e) => setAutoPostConfig(prev => ({ ...prev, [platform]: { ...prev[platform], postsPerDay: parseInt(e.target.value) || 1 } }))} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', width: '100px', fontSize: '16px', fontWeight: '600' }} />
                        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '6px' }}>Recommended: {platform === 'instagram' ? '1-2' : '2-3'} posts per day</div>
                      </div>

                      <div style={{ marginBottom: '20px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                          <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Posting Times</label>
                          <button type="button" onClick={() => addTime(platform)} style={{ padding: '8px 16px', fontSize: '12px', background: platform === 'facebook' ? '#4267B2' : '#E4405F', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>Add +5min</button>
                        </div>
                        
                        <input type="time" onChange={(e) => { if (e.target.value && !autoPostConfig[platform].postingTimes.includes(e.target.value)) { setAutoPostConfig(prev => ({ ...prev, [platform]: { ...prev[platform], postingTimes: [...prev[platform].postingTimes, e.target.value].sort() } })); e.target.value = ''; } }} style={{ padding: '10px 12px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '8px', fontSize: '14px', marginBottom: '12px', width: '100%' }} />

                        {autoPostConfig[platform].postingTimes.length > 0 && (
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {autoPostConfig[platform].postingTimes.map(time => (
                              <span key={time} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 12px', background: 'white', border: `2px solid ${platform === 'facebook' ? '#4267B2' : '#E4405F'}40`, borderRadius: '16px', color: platform === 'facebook' ? '#4267B2' : '#E4405F', fontSize: '13px', fontWeight: '600' }}>
                                {time}
                                <button onClick={() => removeTime(platform, time)} style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '16px', cursor: 'pointer', padding: '0', lineHeight: '1' }}>×</button>
                              </span>
                            ))}
                          </div>
                        )}
                      </div>

                      <div style={{ padding: '16px', backgroundColor: `${platform === 'facebook' ? '#4267B2' : '#E4405F'}15`, borderRadius: '12px', marginTop: '20px' }}>
                        <h4 style={{ margin: '0 0 8px 0', color: platform === 'facebook' ? '#4267B2' : '#E4405F', fontSize: '16px', fontWeight: '700' }}>Automation Status:</h4>
                        <div style={{ fontSize: '14px', color: '#374151', fontWeight: '500' }}>
                          {autoPostConfig[platform].enabled ? (
                            <span style={{ color: '#22c55e' }}>✅ Active - {autoPostConfig[platform].postsPerDay} posts/day</span>
                          ) : (
                            <span style={{ color: '#ef4444' }}>⏸️ Inactive - Configure and start automation</span>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Status Tab */}
            {activeTab === 'status' && (
              <div>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '40px', textAlign: 'center' }}>Platform Status & Analytics</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '40px' }}>
                  <div style={{ background: 'white', borderRadius: '16px', padding: '28px', boxShadow: '0 6px 20px rgba(0, 0, 0, 0.08)', border: '2px solid #4267B230' }}>
                    <h3 style={{ marginTop: 0, fontSize: '20px', fontWeight: '700', color: '#4267B2' }}>📘 Facebook Connection</h3>
                    <div style={{ padding: '8px 16px', borderRadius: '20px', fontSize: '14px', fontWeight: '700', backgroundColor: facebookConnected ? '#d4edda' : '#f8d7da', color: facebookConnected ? '#155724' : '#721c24', display: 'inline-block', marginBottom: '12px' }}>
                      {facebookConnected ? 'Connected' : 'Disconnected'}
                    </div>
                    {facebookUsername && <p style={{ margin: '12px 0 0 0', color: '#666', fontSize: '16px' }}>Connected as: <strong>{facebookUsername}</strong></p>}
                    {facebookPages.length > 0 && <p style={{ margin: '8px 0 0 0', color: '#666', fontSize: '14px' }}>{facebookPages.length} pages available</p>}
                  </div>

                  <div style={{ background: 'white', borderRadius: '16px', padding: '28px', boxShadow: '0 6px 20px rgba(0, 0, 0, 0.08)', border: '2px solid #E4405F30' }}>
                    <h3 style={{ marginTop: 0, fontSize: '20px', fontWeight: '700', color: '#E4405F' }}>📸 Instagram Connection</h3>
                    <div style={{ padding: '8px 16px', borderRadius: '20px', fontSize: '14px', fontWeight: '700', backgroundColor: instagramConnected ? '#d4edda' : '#f8d7da', color: instagramConnected ? '#155724' : '#721c24', display: 'inline-block', marginBottom: '12px' }}>
                      {instagramConnected ? 'Connected' : 'Disconnected'}
                    </div>
                    {instagramUsername && <p style={{ margin: '12px 0 0 0', color: '#666', fontSize: '16px' }}>Connected as: <strong>@{instagramUsername}</strong></p>}
                  </div>

                  <div style={{ background: 'white', borderRadius: '16px', padding: '28px', boxShadow: '0 6px 20px rgba(0, 0, 0, 0.08)', border: '2px solid #667eea30' }}>
                    <h3 style={{ marginTop: 0, fontSize: '20px', fontWeight: '700', color: '#667eea' }}>🤖 AI Profile Status</h3>
                    <div style={{ padding: '8px 16px', borderRadius: '20px', fontSize: '14px', fontWeight: '700', backgroundColor: userProfile.isConfigured ? '#d4edda' : '#f8d7da', color: userProfile.isConfigured ? '#155724' : '#721c24', display: 'inline-block', marginBottom: '12px' }}>
                      {userProfile.isConfigured ? 'Configured' : 'Not Configured'}
                    </div>
                    {userProfile.isConfigured && (
                      <div style={{ fontSize: '14px', color: '#666' }}>
                        <p style={{ margin: '8px 0' }}>Domain: <strong>{userProfile.domain}</strong></p>
                        <p style={{ margin: '8px 0' }}>Style: <strong>{userProfile.contentStyle}</strong></p>
                      </div>
                    )}
                  </div>
                </div>

                <div style={{ padding: '32px', backgroundColor: '#f8f9fa', borderRadius: '20px', border: '2px solid rgba(102, 126, 234, 0.2)' }}>
                  <h3 style={{ marginTop: 0, fontSize: '24px', fontWeight: '700', color: '#667eea', textAlign: 'center', marginBottom: '32px' }}>📊 Performance Metrics</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '24px', textAlign: 'center' }}>
                    <div style={{ padding: '20px', background: 'white', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.05)' }}>
                      <div style={{ fontSize: '36px', fontWeight: '700', marginBottom: '8px', color: '#22c55e' }}>{performanceData.postsToday}</div>
                      <div style={{ fontSize: '16px', color: '#6b7280', fontWeight: '600' }}>Posts Today</div>
                    </div>
                    <div style={{ padding: '20px', background: 'white', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.05)' }}>
                      <div style={{ fontSize: '36px', fontWeight: '700', marginBottom: '8px', color: '#3b82f6' }}>{performanceData.totalEngagement}</div>
                      <div style={{ fontSize: '16px', color: '#6b7280', fontWeight: '600' }}>Total Engagement</div>
                    </div>
                    <div style={{ padding: '20px', background: 'white', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0, 0, 0, 0.05)' }}>
                      <div style={{ fontSize: '36px', fontWeight: '700', marginBottom: '8px', color: '#f59e0b' }}>{performanceData.successRate}%</div>
                      <div style={{ fontSize: '16px', color: '#6b7280', fontWeight: '600' }}>Success Rate</div>
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
};

export default SocialMediaAutomation;