import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';
import InstagramComponent from './INSTA';

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'https://agentic-u5lx.onrender.com';

const SocialMediaAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState('facebook');
  const [activePlatform, setActivePlatform] = useState('facebook');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  // Facebook state
  const [facebookConnected, setFacebookConnected] = useState(false);
  const [facebookUsername, setFacebookUsername] = useState('');
  const [facebookPages, setFacebookPages] = useState([]);
  
  // Instagram state
  const [instagramConnected, setInstagramConnected] = useState(false);
  const [instagramUsername, setInstagramUsername] = useState('');
  
  // Common states
  const [userProfile, setUserProfile] = useState({
    domain: 'tech', businessType: 'AI automation platform', businessDescription: 'We help businesses automate their social media presence',
    targetAudience: 'tech_professionals', contentStyle: 'engaging', isConfigured: false
  });
  
  const [manualPost, setManualPost] = useState({ platform: 'facebook', title: '', content: '', pageId: '', imageUrl: '', isGenerating: false });
  const [autoPostConfig, setAutoPostConfig] = useState({ enabled: false, postsPerDay: 3, postingTimes: [], pages: [], hashtags: [] });
  const [performanceData, setPerformanceData] = useState({ postsToday: 0, totalEngagement: 0, successRate: 95 });

  const domainConfigs = {
    education: { icon: '🎓', description: 'Educational services', sampleBusiness: 'JEE coaching institute' },
    restaurant: { icon: '🍽️', description: 'Food & restaurants', sampleBusiness: 'Traditional Indian restaurant' },
    tech: { icon: '💻', description: 'Technology & programming', sampleBusiness: 'AI automation platform' },
    health: { icon: '💚', description: 'Health & wellness', sampleBusiness: 'Fitness coaching center' },
    business: { icon: '💼', description: 'Business & entrepreneurship', sampleBusiness: 'Business consulting firm' }
  };

  const targetAudienceOptions = {
    'indian_students': { label: 'Indian Students', icon: '🎓' }, 'food_lovers': { label: 'Food Lovers', icon: '🍕' },
    'tech_professionals': { label: 'Tech Professionals', icon: '💻' }, 'health_conscious': { label: 'Health Conscious', icon: '💚' },
    'entrepreneurs': { label: 'Entrepreneurs', icon: '💼' }, 'general_users': { label: 'General Users', icon: '👥' }
  };

  const contentStyleOptions = {
    'engaging': 'Engaging & Interactive', 'informative': 'Informative & Educational', 'promotional': 'Promotional & Marketing',
    'helpful': 'Helpful & Supportive', 'casual': 'Casual & Friendly', 'professional': 'Professional & Formal'
  };

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, message, type };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notification.id)), 5000);
  }, []);

  // Initialize app
  useEffect(() => {
    if (!user?.email || user.email.includes('mock')) return;
    
    const initKey = `social_init_${user.email}`;
    if (localStorage.getItem(initKey)) return;
    localStorage.setItem(initKey, 'true');
    
    const initApp = async () => {
      // Handle OAuth callbacks
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

      // Check existing connections
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

      // Load saved profile
      try {
        const savedProfile = localStorage.getItem('socialUserProfile');
        if (savedProfile) {
          const profile = JSON.parse(savedProfile);
          if (!JSON.stringify(profile).toLowerCase().includes('mock')) {
            setUserProfile(profile);
          }
        }
      } catch (error) {
        console.error('Error loading profile:', error);
      }
    };

    initApp();
  }, []);

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

  const generateContent = useCallback(async () => {
    if (!userProfile.businessType) {
      showNotification('Please configure your profile first', 'error');
      return;
    }

    try {
      setManualPost(prev => ({ ...prev, isGenerating: true }));
      showNotification('Generating content with REAL AI...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/content/generate', {
        method: 'POST',
        body: JSON.stringify({
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          content_style: userProfile.contentStyle
        })
      });

      const result = await response.json();

      if (result.success) {
        setManualPost(prev => ({ ...prev, title: result.title, content: result.content }));
        showNotification(`Content generated using ${result.ai_service}!`, 'success');
      } else {
        showNotification(result.error || 'AI content generation failed', 'error');
      }
    } catch (error) {
      showNotification('AI generation failed: ' + error.message, 'error');
    } finally {
      setManualPost(prev => ({ ...prev, isGenerating: false }));
    }
  }, [userProfile, makeAuthenticatedRequest, showNotification]);

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

    if (manualPost.platform === 'instagram' && !manualPost.imageUrl) {
      showNotification('Instagram requires an image URL', 'error');
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
        if (result.post_url) showNotification(`View post: ${result.post_url}`, 'info');
        
        setPerformanceData(prev => ({ ...prev, postsToday: prev.postsToday + 1 }));
        setManualPost({ platform: manualPost.platform, title: '', content: '', pageId: '', imageUrl: '', isGenerating: false });
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
        domain: userProfile.domain,
        business_type: userProfile.businessType,
        business_description: userProfile.businessDescription,
        target_audience: userProfile.targetAudience,
        language: userProfile.language,
        content_style: userProfile.contentStyle,
        posts_per_day: autoPostConfig.postsPerDay,
        posting_times: autoPostConfig.postingTimes,
        ...(platform === 'facebook' ? { pages: autoPostConfig.pages } : { hashtags: autoPostConfig.hashtags })
      };

      const response = await makeAuthenticatedRequest(`/api/automation/${platform}/setup`, {
        method: 'POST',
        body: JSON.stringify(config)
      });
      
      const result = await response.json();
      
      if (result.success) {
        setAutoPostConfig(prev => ({ ...prev, enabled: true }));
        const username = platform === 'facebook' ? facebookUsername : instagramUsername;
        showNotification(`${platform} auto-posting started for ${username}!`, 'success');
      } else {
        showNotification(result.error || 'Automation setup failed', 'error');
      }
    } catch (error) {
      showNotification('Setup failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [userProfile, facebookConnected, instagramConnected, autoPostConfig, makeAuthenticatedRequest, facebookUsername, instagramUsername, showNotification]);

  const ConnectionCard = ({ platform, connected, username, onConnect }) => (
    <div style={{ padding: '20px', background: 'rgba(255,255,255,0.1)', borderRadius: '12px', marginBottom: '16px' }}>
      {connected ? (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', borderRadius: '10px', background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(16, 185, 129, 0.1))', color: '#047857', marginBottom: '12px' }}>
            <div style={{ width: '12px', height: '12px', background: '#22c55e', borderRadius: '50%', animation: 'pulse 2s infinite' }}></div>
            <span style={{ fontSize: '16px', fontWeight: '600' }}>✅ {platform} Connected</span>
          </div>
          {username && <div style={{ fontSize: '13px', color: '#059669', fontWeight: '500', margin: '0 0 16px 32px', background: 'rgba(34, 197, 94, 0.08)', padding: '6px 12px', borderRadius: '20px', display: 'inline-block' }}>{platform === 'facebook' ? username : `@${username}`}</div>}
        </div>
      ) : (
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', borderRadius: '10px', background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.15), rgba(220, 38, 38, 0.1))', color: '#dc2626', marginBottom: '12px' }}>
            <div style={{ width: '12px', height: '12px', background: '#ef4444', borderRadius: '50%', animation: 'pulse 2s infinite' }}></div>
            <span style={{ fontSize: '16px', fontWeight: '600' }}>❌ {platform} Not Connected</span>
          </div>
          <button onClick={onConnect} disabled={loading} style={{ width: '100%', padding: '12px 16px', fontSize: '14px', fontWeight: '600', background: loading ? '#d1d5db' : 'linear-gradient(135deg, #ef4444, #dc2626)', color: 'white', border: 'none', borderRadius: '10px', cursor: loading ? 'not-allowed' : 'pointer', boxShadow: '0 4px 15px rgba(239, 68, 68, 0.3)' }}>
            {loading ? 'Connecting...' : `Connect ${platform}`}
          </button>
        </div>
      )}
    </div>
  );

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', display: 'flex' }}>
      {/* Notifications */}
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 10000, display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}>
        {notifications.map(notification => (
          <div key={notification.id} style={{ padding: '16px 20px', borderRadius: '12px', backdropFilter: 'blur(10px)', color: 'white', fontWeight: '500', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)', background: notification.type === 'success' ? 'rgba(34, 197, 94, 0.9)' : notification.type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(59, 130, 246, 0.9)', borderLeft: `4px solid ${notification.type === 'success' ? '#22c55e' : notification.type === 'error' ? '#ef4444' : '#3b82f6'}`, display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
            <span>{notification.message}</span>
            <button onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))} style={{ background: 'none', border: 'none', color: 'white', fontSize: '18px', cursor: 'pointer', padding: '4px' }}>×</button>
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
          <h2 style={{ fontSize: '24px', fontWeight: '700', color: 'white', margin: 0, marginBottom: '4px' }}>Social Auto</h2>
          <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>Welcome, {user?.name}</div>
        </div>
        
        <nav style={{ flex: 1, padding: '24px 16px' }}>
          {[
            { id: 'setup', icon: '⚙️', label: 'Setup' },
            { id: 'facebook', icon: '📘', label: 'Facebook' },
            { id: 'instagram', icon: '📸', label: 'Instagram' },
            { id: 'manual', icon: '✍️', label: 'Manual Post' },
            { id: 'schedule', icon: '📅', label: 'Schedule' },
            { id: 'status', icon: '📈', label: 'Status' }
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '12px', padding: '16px 20px', border: 'none', background: activeTab === tab.id ? 'linear-gradient(135deg, #667eea, #764ba2)' : 'none', color: activeTab === tab.id ? 'white' : '#666', textAlign: 'left', borderRadius: '12px', cursor: 'pointer', marginBottom: '8px', fontSize: '16px', transform: activeTab === tab.id ? 'translateX(4px)' : 'none', boxShadow: activeTab === tab.id ? '0 4px 15px rgba(102, 126, 234, 0.4)' : 'none' }}>
              <span>{tab.icon}</span>
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>

        {/* Connection Status */}
        <div style={{ padding: '20px 24px', borderTop: '1px solid rgba(0, 0, 0, 0.05)' }}>
          <ConnectionCard platform="Facebook" connected={facebookConnected} username={facebookUsername} onConnect={() => handleConnect('facebook')} />
          <ConnectionCard platform="Instagram" connected={instagramConnected} username={instagramUsername} onConnect={() => handleConnect('instagram')} />
        </div>
      </div>

      {/* Main Content */}
      <div style={{ flex: 1, marginLeft: '280px', background: 'rgba(255, 255, 255, 0.1)', backdropFilter: 'blur(10px)' }}>
        <header style={{ padding: '32px 40px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(10px)', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '8px' }}>Social Media Automation Dashboard</h1>
            <p style={{ fontSize: '16px', color: '#666' }}>AI-powered Facebook & Instagram automation</p>
          </div>
          
          <div style={{ display: 'flex', gap: '12px' }}>
            {userProfile.isConfigured && (
              <>
                <button onClick={() => startAutomation('facebook')} disabled={loading || !facebookConnected} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px', border: 'none', borderRadius: '10px', fontSize: '14px', fontWeight: '600', cursor: loading || !facebookConnected ? 'not-allowed' : 'pointer', background: loading || !facebookConnected ? '#bdc3c7' : 'linear-gradient(135deg, #4267B2, #365899)', color: 'white', boxShadow: '0 4px 15px rgba(66, 103, 178, 0.3)' }}>
                  <span>🚀</span><span>Start FB Auto</span>
                </button>
                <button onClick={() => startAutomation('instagram')} disabled={loading || !instagramConnected} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '12px 24px', border: 'none', borderRadius: '10px', fontSize: '14px', fontWeight: '600', cursor: loading || !instagramConnected ? 'not-allowed' : 'pointer', background: loading || !instagramConnected ? '#bdc3c7' : 'linear-gradient(135deg, #E4405F, #C13584)', color: 'white', boxShadow: '0 4px 15px rgba(228, 64, 95, 0.3)' }}>
                  <span>🚀</span><span>Start IG Auto</span>
                </button>
              </>
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
                  <select value={userProfile.domain} onChange={(e) => { const domain = e.target.value; const config = domainConfigs[domain]; setUserProfile(prev => ({ ...prev, domain, businessType: config?.sampleBusiness || prev.businessType })); }} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}>
                    {Object.entries(domainConfigs).map(([key, config]) => (
                      <option key={key} value={key}>{config.icon} {config.description}</option>
                    ))}
                  </select>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                  <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Business Type</label>
                  <input type="text" value={userProfile.businessType} onChange={(e) => setUserProfile(prev => ({ ...prev, businessType: e.target.value }))} placeholder={domainConfigs[userProfile.domain]?.sampleBusiness} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }} />
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                  <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Business Description</label>
                  <textarea value={userProfile.businessDescription} onChange={(e) => setUserProfile(prev => ({ ...prev, businessDescription: e.target.value }))} placeholder="Describe your business or service..." rows="3" style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white', resize: 'vertical' }} />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Target Audience</label>
                    <select value={userProfile.targetAudience} onChange={(e) => setUserProfile(prev => ({ ...prev, targetAudience: e.target.value }))} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}>
                      {Object.entries(targetAudienceOptions).map(([key, option]) => (
                        <option key={key} value={key}>{option.icon} {option.label}</option>
                      ))}
                    </select>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Content Style</label>
                    <select value={userProfile.contentStyle} onChange={(e) => setUserProfile(prev => ({ ...prev, contentStyle: e.target.value }))} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}>
                      {Object.entries(contentStyleOptions).map(([key, style]) => (
                        <option key={key} value={key}>{style}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div style={{ textAlign: 'center', marginTop: '32px' }}>
                  <button onClick={saveUserProfile} disabled={!userProfile.businessType} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', padding: '16px 32px', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '600', cursor: userProfile.businessType ? 'pointer' : 'not-allowed', background: userProfile.businessType ? 'linear-gradient(135deg, #667eea, #764ba2)' : '#bdc3c7', color: 'white', boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)', margin: '0 auto' }}>
                    Save Configuration
                  </button>
                </div>

                {userProfile.isConfigured && (
                  <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#d4edda', borderRadius: '12px', border: '1px solid #c3e6cb' }}>
                    <div style={{ color: '#155724', fontWeight: 'bold', marginBottom: '5px' }}>Profile Configured Successfully</div>
                    <div style={{ color: '#155724', fontSize: '14px' }}>Ready for Facebook & Instagram automation setup.</div>
                  </div>
                )}
              </div>
            )}

            {(activeTab === 'facebook' || activeTab === 'instagram') && (
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#333', marginBottom: '32px' }}>{activeTab === 'facebook' ? 'Facebook' : 'Instagram'} Management</h2>
                
                {activeTab === 'facebook' ? (
                  facebookConnected ? (
                    <div>
                      <div style={{ marginBottom: '24px', padding: '20px', background: '#f8f9fa', borderRadius: '12px' }}>
                        <h3 style={{ marginTop: 0 }}>Connected as: {facebookUsername}</h3>
                        {facebookPages.length > 0 && (
                          <div>
                            <h4>Your Pages:</h4>
                            {facebookPages.map(page => (
                              <div key={page.id} style={{ padding: '8px 12px', margin: '4px 0', background: 'white', borderRadius: '8px', border: '1px solid #ddd' }}>
                                📄 {page.name}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                      <InstagramComponent platform="facebook" userProfile={userProfile} />
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', padding: '60px 20px' }}>
                      <div style={{ fontSize: '64px', marginBottom: '20px' }}>📘</div>
                      <h3>Connect Your Facebook Account</h3>
                      <p style={{ marginBottom: '30px', color: '#666' }}>Connect your Facebook account to start automated posting</p>
                      <button onClick={() => handleConnect('facebook')} style={{ padding: '16px 32px', fontSize: '16px', background: 'linear-gradient(135deg, #4267B2, #365899)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer' }}>
                        Connect Facebook
                      </button>
                    </div>
                  )
                ) : (
                  instagramConnected ? (
                    <div>
                      <div style={{ marginBottom: '24px', padding: '20px', background: '#f8f9fa', borderRadius: '12px' }}>
                        <h3 style={{ marginTop: 0 }}>Connected as: @{instagramUsername}</h3>
                      </div>
                      <InstagramComponent platform="instagram" userProfile={userProfile} />
                    </div>
                  ) : (
                    <div style={{ textAlign: 'center', padding: '60px 20px' }}>
                      <div style={{ fontSize: '64px', marginBottom: '20px' }}>📸</div>
                      <h3>Connect Your Instagram Account</h3>
                      <p style={{ marginBottom: '30px', color: '#666' }}>Connect your Instagram account to start automated posting</p>
                      <button onClick={() => handleConnect('instagram')} style={{ padding: '16px 32px', fontSize: '16px', background: 'linear-gradient(135deg, #E4405F, #C13584)', color: 'white', border: 'none', borderRadius: '12px', cursor: 'pointer' }}>
                        Connect Instagram
                      </button>
                    </div>
                  )
                )}
              </div>
            )}

            {activeTab === 'manual' && (
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#333', marginBottom: '32px' }}>Manual Posting</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto auto', gap: '20px', marginBottom: '20px', alignItems: 'end' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Platform</label>
                    <select value={manualPost.platform} onChange={(e) => setManualPost(prev => ({ ...prev, platform: e.target.value }))} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}>
                      <option value="facebook">📘 Facebook</option>
                      <option value="instagram">📸 Instagram</option>
                    </select>
                  </div>

                  <button onClick={generateContent} disabled={manualPost.isGenerating || !userProfile.isConfigured} style={{ padding: '16px 32px', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '600', cursor: (manualPost.isGenerating || !userProfile.isConfigured) ? 'not-allowed' : 'pointer', background: (manualPost.isGenerating || !userProfile.isConfigured) ? '#bdc3c7' : 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', boxShadow: '0 4px 15px rgba(102, 126, 234, 0.3)' }}>
                    {manualPost.isGenerating ? 'Generating...' : 'Generate with AI'}
                  </button>
                </div>

                <form onSubmit={handleManualPost}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Post Title</label>
                    <input type="text" value={manualPost.title} onChange={(e) => setManualPost(prev => ({ ...prev, title: e.target.value }))} placeholder="Enter your post title..." style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }} required />
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                    <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Post Content</label>
                    <textarea value={manualPost.content} onChange={(e) => setManualPost(prev => ({ ...prev, content: e.target.value }))} placeholder="Enter your post content..." rows="8" style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white', resize: 'vertical' }} required />
                  </div>

                  {manualPost.platform === 'instagram' && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                      <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Image URL (Required for Instagram)</label>
                      <input type="url" value={manualPost.imageUrl} onChange={(e) => setManualPost(prev => ({ ...prev, imageUrl: e.target.value }))} placeholder="https://example.com/image.jpg" style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }} required />
                    </div>
                  )}

                  {manualPost.platform === 'facebook' && facebookPages.length > 0 && (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                      <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Facebook Page</label>
                      <select value={manualPost.pageId} onChange={(e) => setManualPost(prev => ({ ...prev, pageId: e.target.value }))} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white' }}>
                        <option value="">Select a page</option>
                        {facebookPages.map(page => (
                          <option key={page.id} value={page.id}>{page.name}</option>
                        ))}
                      </select>
                    </div>
                  )}

                  <div style={{ textAlign: 'center' }}>
                    <button type="submit" disabled={loading || (manualPost.platform === 'facebook' ? !facebookConnected : !instagramConnected) || !manualPost.title || !manualPost.content || (manualPost.platform === 'instagram' && !manualPost.imageUrl)} style={{ padding: '16px 32px', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '600', cursor: 'pointer', background: 'linear-gradient(135deg, #34d399, #10b981)', color: 'white', boxShadow: '0 4px 15px rgba(52, 211, 153, 0.3)' }}>
                      {loading ? 'Posting...' : `Post to ${manualPost.platform}`}
                    </button>
                  </div>
                </form>
              </div>
            )}

            {activeTab === 'schedule' && (
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#333', marginBottom: '32px' }}>Automation Schedule</h2>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '20px' }}>
                  <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Posts Per Day</label>
                  <input type="number" min="1" max="10" value={autoPostConfig.postsPerDay} onChange={(e) => setAutoPostConfig(prev => ({ ...prev, postsPerDay: parseInt(e.target.value) || 1 }))} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', fontSize: '14px', background: 'white', width: '200px' }} />
                </div>

                <div style={{ marginBottom: '24px' }}>
                  <h4 style={{ marginBottom: '16px' }}>Posting Times</h4>
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
                    <input type="time" onChange={(e) => { if (e.target.value && !autoPostConfig.postingTimes.includes(e.target.value)) { setAutoPostConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, e.target.value].sort() })); } }} style={{ padding: '8px 12px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '6px', fontSize: '14px' }} />
                  </div>

                  {autoPostConfig.postingTimes.length > 0 && (
                    <div>
                      <h5 style={{ marginTop: '20px', marginBottom: '12px' }}>Scheduled Times ({autoPostConfig.postingTimes.length})</h5>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {autoPostConfig.postingTimes.map(time => (
                          <div key={time} style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '6px 12px', background: 'white', border: '1px solid rgba(34, 197, 94, 0.3)', borderRadius: '16px', color: '#16a34a', fontSize: '14px', fontWeight: '500' }}>
                            <span>{time}</span>
                            <button onClick={() => setAutoPostConfig(prev => ({ ...prev, postingTimes: prev.postingTimes.filter(t => t !== time) }))} style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '16px', cursor: 'pointer' }}>×</button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'status' && (
              <div>
                <h2 style={{ fontSize: '28px', fontWeight: '700', color: '#333', marginBottom: '32px' }}>System Status & Analytics</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)' }}>
                    <h3 style={{ marginTop: 0 }}>Facebook Connection</h3>
                    <div style={{ padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold', backgroundColor: facebookConnected ? '#d4edda' : '#f8d7da', color: facebookConnected ? '#155724' : '#721c24', display: 'inline-block' }}>
                      {facebookConnected ? 'Connected' : 'Disconnected'}
                    </div>
                    {facebookUsername && <p style={{ margin: '10px 0 0 0', color: '#666' }}>Connected as: {facebookUsername}</p>}
                  </div>

                  <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)' }}>
                    <h3 style={{ marginTop: 0 }}>Instagram Connection</h3>
                    <div style={{ padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold', backgroundColor: instagramConnected ? '#d4edda' : '#f8d7da', color: instagramConnected ? '#155724' : '#721c24', display: 'inline-block' }}>
                      {instagramConnected ? 'Connected' : 'Disconnected'}
                    </div>
                    {instagramUsername && <p style={{ margin: '10px 0 0 0', color: '#666' }}>Connected as: @{instagramUsername}</p>}
                  </div>

                  <div style={{ background: 'white', borderRadius: '12px', padding: '20px', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)' }}>
                    <h3 style={{ marginTop: 0 }}>Profile Status</h3>
                    <div style={{ padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 'bold', backgroundColor: userProfile.isConfigured ? '#d4edda' : '#f8d7da', color: userProfile.isConfigured ? '#155724' : '#721c24', display: 'inline-block' }}>
                      {userProfile.isConfigured ? 'Configured' : 'Not Configured'}
                    </div>
                    {userProfile.isConfigured && <p style={{ margin: '10px 0 0 0', color: '#666' }}>Domain: {userProfile.domain}</p>}
                  </div>
                </div>

                <div style={{ padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '12px' }}>
                  <h3 style={{ marginTop: 0 }}>Performance Metrics</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '20px', textAlign: 'center' }}>
                    <div>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#22c55e' }}>{performanceData.postsToday}</div>
                      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Posts Today</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#3b82f6' }}>{performanceData.totalEngagement}</div>
                      <div style={{ fontSize: '14px', color: '#6b7280', fontWeight: '500' }}>Total Engagement</div>
                    </div>
                    <div>
                      <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px', color: '#f59e0b' }}>{performanceData.successRate}%</div>
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
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.5; }
        }
      `}</style>
    </div>
  );
};

export default SocialMediaAutomation;