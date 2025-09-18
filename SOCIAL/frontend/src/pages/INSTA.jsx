import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const API_BASE_URL = (typeof import.meta !== 'undefined' && import.meta.env?.VITE_API_URL) || 'https://agentic-u5lx.onrender.com';

const POPULAR_HASHTAGS = {
  business: ['#entrepreneur', '#business', '#startup', '#success', '#motivation'],
  food: ['#foodie', '#delicious', '#foodporn', '#yummy', '#instafood'],
  fitness: ['#fitness', '#workout', '#health', '#gym', '#fitlife'],
  tech: ['#technology', '#innovation', '#coding', '#startup', '#ai'],
  lifestyle: ['#lifestyle', '#daily', '#inspiration', '#goals', '#mindset']
};

const CONTENT_TYPES = {
  carousel: 'Multi-image carousel post',
  single: 'Single image post',
  video: 'Video content',
  story: 'Instagram Story'
};

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

const InstagramAutomation = () => {
  const { user, makeAuthenticatedRequest, updateUser } = useAuth();
  
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [instagramConnected, setInstagramConnected] = useState(false);
  const [instagramUsername, setInstagramUsername] = useState('');
  const [accountType, setAccountType] = useState('personal');
  
  // User Profile Configuration
  const [userProfile, setUserProfile] = useState({
    domain: 'tech',
    businessType: 'AI automation platform',
    businessDescription: 'We help businesses automate their Instagram presence',
    targetAudience: 'tech_professionals',
    contentStyle: 'engaging',
    isConfigured: false
  });
  
  const [postCreator, setPostCreator] = useState({
    caption: '',
    hashtags: [],
    imagePrompt: '',
    generatedImage: '',
    contentType: 'single',
    isGeneratingContent: false,
    isGeneratingImage: false
  });
  
  const [automationConfig, setAutomationConfig] = useState({
    enabled: false,
    postsPerDay: 2,
    postingTimes: [],
    hashtagStrategy: 'auto',
    contentMix: { carousel: 40, single: 40, video: 20 },
    themes: []
  });

  const [performanceData, setPerformanceData] = useState({
    postsToday: 0,
    totalEngagement: 0,
    successRate: 95
  });

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`, message, type };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notification.id)), 4000);
  }, []);

  useEffect(() => {
    if (!user?.email) return;
    
    const initKey = `instagram_init_${user.email}`;
    if (localStorage.getItem(initKey)) return;
    localStorage.setItem(initKey, 'true');

    const checkInstagramConnection = async () => {
      const urlParams = new URLSearchParams(window.location.search);
      const igConnected = urlParams.get('instagram_connected');
      const username = urlParams.get('username');
      const error = urlParams.get('error');

      if (error) {
        showNotification(`Connection failed: ${error}`, 'error');
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
        const response = await makeAuthenticatedRequest('/api/instagram/connection-status');
        const result = await response.json();
        
        if (result.success && result.connected) {
          setInstagramConnected(true);
          setInstagramUsername(result.username);
          setAccountType(result.account_type || 'personal');
        }
      } catch (error) {
        console.error('Failed to check Instagram connection:', error);
      }

      // Load user profile from localStorage with user-specific key
      try {
        const savedProfile = localStorage.getItem(`instagramUserProfile_${user.email}`);
        if (savedProfile) {
          const profile = JSON.parse(savedProfile);
          setUserProfile(profile);
        }
      } catch (error) {
        console.error('Error loading profile:', error);
      }
    };

    checkInstagramConnection();
  }, [user, makeAuthenticatedRequest, updateUser, showNotification]);

  const handleInstagramConnect = useCallback(async () => {
    try {
      setLoading(true);
      showNotification('Connecting to Instagram...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/oauth/instagram/authorize');
      const result = await response.json();
      
      if (result.success && result.redirect_url) {
        window.location.href = result.redirect_url;
      } else {
        showNotification(result.error || 'Failed to start Instagram authorization', 'error');
      }
    } catch (error) {
      showNotification(`Connection failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAuthenticatedRequest, showNotification]);

  const testConnection = useCallback(async () => {
    try {
      setLoading(true);
      const response = await makeAuthenticatedRequest('/api/instagram/connection-status');
      const result = await response.json();
      
      if (result.success && result.connected) {
        showNotification(`Instagram connection verified for @${result.username}!`, 'success');
      } else {
        showNotification('Instagram not connected', 'error');
      }
    } catch (error) {
      showNotification('Test failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [makeAuthenticatedRequest, showNotification]);

  const saveUserProfile = useCallback(() => {
    try {
      const profileToSave = { ...userProfile, isConfigured: true };
      localStorage.setItem(`instagramUserProfile_${user.email}`, JSON.stringify(profileToSave));
      setUserProfile(profileToSave);
      showNotification('Profile saved successfully!', 'success');
    } catch (error) {
      showNotification('Failed to save profile', 'error');
    }
  }, [userProfile, user?.email, showNotification]);

  const generateInstagramContent = useCallback(async () => {
    if (!userProfile.businessType) {
      showNotification('Please configure your profile first', 'error');
      return;
    }

    try {
      setPostCreator(prev => ({ ...prev, isGeneratingContent: true }));
      showNotification('Generating Instagram content with AI...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/ai/generate-content', {
        method: 'POST',
        body: JSON.stringify({
          platform: 'instagram',
          content_type: postCreator.contentType,
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          content_style: userProfile.contentStyle
        })
      });

      const result = await response.json();

      if (result.success) {
        setPostCreator(prev => ({
          ...prev,
          caption: result.caption || result.content,
          imagePrompt: result.image_prompt || '',
          hashtags: result.hashtags || prev.hashtags
        }));
        showNotification(`Content generated! Human authenticity: ${result.human_score || 95}%`, 'success');
      } else {
        showNotification(result.error || 'Content generation failed', 'error');
      }
    } catch (error) {
      showNotification('AI generation failed: ' + error.message, 'error');
    } finally {
      setPostCreator(prev => ({ ...prev, isGeneratingContent: false }));
    }
  }, [makeAuthenticatedRequest, showNotification, postCreator.contentType, userProfile]);

  const generateInstagramImage = useCallback(async () => {
    if (!postCreator.imagePrompt) {
      showNotification('Please add an image description first', 'error');
      return;
    }

    try {
      setPostCreator(prev => ({ ...prev, isGeneratingImage: true }));
      showNotification('Generating image for Instagram post...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/ai/generate-image', {
        method: 'POST',
        body: JSON.stringify({
          prompt: postCreator.imagePrompt,
          platform: 'instagram',
          style: 'modern, engaging, high-quality'
        })
      });

      const result = await response.json();

      if (result.success) {
        setPostCreator(prev => ({ ...prev, generatedImage: result.image_url }));
        showNotification('Image generated successfully!', 'success');
      } else {
        showNotification(result.error || 'Image generation failed', 'error');
      }
    } catch (error) {
      showNotification('Image generation failed: ' + error.message, 'error');
    } finally {
      setPostCreator(prev => ({ ...prev, isGeneratingImage: false }));
    }
  }, [makeAuthenticatedRequest, showNotification, postCreator.imagePrompt]);

  const publishInstagramPost = useCallback(async () => {
    if (!postCreator.caption) {
      showNotification('Please add a caption to your post', 'error');
      return;
    }

    if (!instagramConnected) {
      showNotification('Please connect your Instagram account first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Publishing to Instagram...', 'info');
      
      const fullCaption = `${postCreator.caption}\n\n${postCreator.hashtags.join(' ')}`;
      
      const response = await makeAuthenticatedRequest('/api/instagram/post', {
        method: 'POST',
        body: JSON.stringify({
          caption: fullCaption,
          image_url: postCreator.generatedImage,
          content_type: postCreator.contentType
        })
      });

      const result = await response.json();

      if (result.success) {
        showNotification(`Posted successfully to @${instagramUsername}!`, 'success');
        if (result.post_url) {
          showNotification(`View post: ${result.post_url}`, 'info');
        }
        
        setPerformanceData(prev => ({ ...prev, postsToday: prev.postsToday + 1 }));
        setPostCreator({
          caption: '',
          hashtags: [],
          imagePrompt: '',
          generatedImage: '',
          contentType: 'single',
          isGeneratingContent: false,
          isGeneratingImage: false
        });
      } else {
        showNotification(result.error || 'Publishing failed', 'error');
      }
    } catch (error) {
      showNotification('Publishing failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [postCreator, instagramConnected, instagramUsername, makeAuthenticatedRequest, showNotification]);

  const addHashtag = (hashtag) => {
    if (hashtag && !postCreator.hashtags.includes(hashtag) && postCreator.hashtags.length < 30) {
      setPostCreator(prev => ({ ...prev, hashtags: [...prev.hashtags, hashtag] }));
    }
  };

  const removeHashtag = (hashtagToRemove) => {
    setPostCreator(prev => ({ ...prev, hashtags: prev.hashtags.filter(h => h !== hashtagToRemove) }));
  };

  const addTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 5);
    const testTime = now.toTimeString().slice(0, 5);
    if (!automationConfig.postingTimes.includes(testTime)) {
      setAutomationConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, testTime].sort() }));
      showNotification('Test time added (+5 minutes)', 'info');
    }
  };

  const removeTime = (time) => {
    setAutomationConfig(prev => ({ ...prev, postingTimes: prev.postingTimes.filter(t => t !== time) }));
  };

  const startAutomation = useCallback(async () => {
    if (!userProfile.isConfigured) {
      showNotification('Please configure your profile first', 'error');
      setActiveTab('setup');
      return;
    }

    if (!instagramConnected) {
      showNotification('Please connect your Instagram account first', 'error');
      return;
    }

    try {
      setLoading(true);
      showNotification('Setting up Instagram automation...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/setup-instagram', {
        method: 'POST',
        body: JSON.stringify({
          enabled: true,
          domain: userProfile.domain,
          business_type: userProfile.businessType,
          business_description: userProfile.businessDescription,
          target_audience: userProfile.targetAudience,
          content_style: userProfile.contentStyle,
          posts_per_day: automationConfig.postsPerDay,
          posting_times: automationConfig.postingTimes,
          hashtag_strategy: automationConfig.hashtagStrategy,
          content_mix: automationConfig.contentMix
        })
      });

      const result = await response.json();

      if (result.success) {
        setAutomationConfig(prev => ({ ...prev, enabled: true }));
        showNotification(`Instagram automation started for @${instagramUsername}!`, 'success');
      } else {
        showNotification(result.error || 'Automation setup failed', 'error');
      }
    } catch (error) {
      showNotification('Setup failed: ' + error.message, 'error');
    } finally {
      setLoading(false);
    }
  }, [instagramConnected, instagramUsername, userProfile, automationConfig, makeAuthenticatedRequest, showNotification]);

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, sans-serif', minHeight: '100vh', background: 'linear-gradient(135deg, #E4405F 0%, #C13584 100%)', display: 'flex' }}>
      
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 10000, display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}>
        {notifications.map(notification => (
          <div key={notification.id} style={{ padding: '16px 20px', borderRadius: '12px', backdropFilter: 'blur(15px)', color: 'white', fontWeight: '600', boxShadow: '0 8px 25px rgba(0, 0, 0, 0.3)', background: notification.type === 'success' ? 'rgba(34, 197, 94, 0.9)' : notification.type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(59, 130, 246, 0.9)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px', fontSize: '14px', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
            <span>{notification.message}</span>
            <button onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))} style={{ background: 'none', border: 'none', color: 'white', fontSize: '18px', cursor: 'pointer', padding: '4px', opacity: 0.8 }}>×</button>
          </div>
        ))}
      </div>

      {loading && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(8px)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 9999 }}>
          <div style={{ background: 'white', padding: '40px', borderRadius: '16px', textAlign: 'center', boxShadow: '0 15px 50px rgba(0, 0, 0, 0.3)' }}>
            <div style={{ border: '4px solid #f3f3f3', borderTop: '4px solid #E4405F', borderRadius: '50%', width: '50px', height: '50px', animation: 'spin 1s linear infinite', margin: '0 auto' }}></div>
            <p style={{ marginTop: '20px', color: '#666', fontSize: '16px', fontWeight: '600' }}>Processing Instagram request...</p>
          </div>
        </div>
      )}

      <div style={{ width: '320px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(15px)', height: '100vh', position: 'fixed', display: 'flex', flexDirection: 'column', boxShadow: '4px 0 25px rgba(0, 0, 0, 0.1)', border: '1px solid rgba(255, 255, 255, 0.2)' }}>
        
        <div style={{ padding: '40px 28px', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', textAlign: 'center', background: 'linear-gradient(135deg, #E4405F, #C13584)' }}>
          <div style={{ fontSize: '40px', marginBottom: '12px' }}>📸</div>
          <h2 style={{ fontSize: '26px', fontWeight: '700', color: 'white', margin: 0, marginBottom: '6px' }}>Instagram Automation</h2>
          <div style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.9)', fontWeight: '500' }}>AI-Powered Content Creation</div>
          <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.8)', marginTop: '4px' }}>Welcome, {user?.name}</div>
        </div>
        
        <nav style={{ flex: 1, padding: '28px 20px' }}>
          {[
            { id: 'setup', icon: '⚙️', label: 'Profile Setup', desc: 'Configure AI settings' },
            { id: 'connect', icon: '🔗', label: 'Connection', desc: 'Link Instagram account' },
            { id: 'create', icon: '🎨', label: 'Create Post', desc: 'AI content generation' },
            { id: 'automate', icon: '🤖', label: 'Automation', desc: 'Schedule & settings' },
            { id: 'analytics', icon: '📈', label: 'Analytics', desc: 'Performance insights' }
          ].map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{ width: '100%', display: 'flex', alignItems: 'center', gap: '16px', padding: '20px 24px', border: 'none', background: activeTab === tab.id ? 'linear-gradient(135deg, #E4405F, #C13584)' : 'none', color: activeTab === tab.id ? 'white' : '#666', textAlign: 'left', borderRadius: '16px', cursor: 'pointer', marginBottom: '12px', fontSize: '16px', transform: activeTab === tab.id ? 'translateX(6px)' : 'none', boxShadow: activeTab === tab.id ? '0 6px 20px rgba(228, 64, 95, 0.4)' : 'none', transition: 'all 0.3s ease' }}>
              <span style={{ fontSize: '20px' }}>{tab.icon}</span>
              <div>
                <div style={{ fontWeight: '600', fontSize: '16px' }}>{tab.label}</div>
                <div style={{ fontSize: '12px', opacity: 0.8, marginTop: '2px' }}>{tab.desc}</div>
              </div>
            </button>
          ))}
        </nav>

        <div style={{ padding: '24px 28px', borderTop: '1px solid rgba(0, 0, 0, 0.05)' }}>
          <h3 style={{ fontSize: '16px', fontWeight: '700', color: '#374151', marginBottom: '16px' }}>Instagram Status</h3>
          <div style={{ padding: '20px', background: 'rgba(255,255,255,0.1)', borderRadius: '16px', border: `2px solid ${instagramConnected ? '#22c55e' : '#ef4444'}30` }}>
            {instagramConnected ? (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', borderRadius: '10px', background: 'rgba(34, 197, 94, 0.15)', color: '#047857', marginBottom: '12px', fontSize: '16px', fontWeight: '700' }}>
                  <div style={{ width: '10px', height: '10px', background: '#22c55e', borderRadius: '50%' }}></div>
                  ✅ Instagram Connected
                </div>
                <div style={{ fontSize: '14px', color: '#059669', margin: '0 0 12px 18px', background: 'rgba(34, 197, 94, 0.1)', padding: '6px 12px', borderRadius: '16px', display: 'inline-block', fontWeight: '600' }}>@{instagramUsername}</div>
                <div style={{ fontSize: '12px', color: '#6b7280', marginLeft: '18px' }}>Account Type: {accountType}</div>
                <button onClick={testConnection} disabled={loading} style={{ width: '100%', padding: '10px 16px', fontSize: '14px', fontWeight: '700', background: loading ? '#d1d5db' : 'linear-gradient(135deg, #22c55e, #16a34a)', color: 'white', border: 'none', borderRadius: '10px', cursor: loading ? 'not-allowed' : 'pointer', marginTop: '12px' }}>
                  {loading ? 'Testing...' : 'Test Connection'}
                </button>
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '10px 16px', borderRadius: '10px', background: 'rgba(239, 68, 68, 0.15)', color: '#dc2626', marginBottom: '12px', fontSize: '16px', fontWeight: '700' }}>
                  <div style={{ width: '10px', height: '10px', background: '#ef4444', borderRadius: '50%' }}></div>
                  ❌ Instagram Not Connected
                </div>
                <button onClick={handleInstagramConnect} disabled={loading} style={{ width: '100%', padding: '10px 16px', fontSize: '14px', fontWeight: '700', background: loading ? '#d1d5db' : 'linear-gradient(135deg, #E4405F, #C13584)', color: 'white', border: 'none', borderRadius: '10px', cursor: loading ? 'not-allowed' : 'pointer' }}>
                  {loading ? 'Connecting...' : 'Connect Instagram'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      <div style={{ flex: 1, marginLeft: '320px', background: 'rgba(255, 255, 255, 0.05)', backdropFilter: 'blur(10px)' }}>
        
        <header style={{ padding: '40px 48px', background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(15px)', borderBottom: '1px solid rgba(0, 0, 0, 0.1)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '36px', fontWeight: '700', color: '#333', marginBottom: '8px' }}>Instagram Content Studio</h1>
            <p style={{ fontSize: '18px', color: '#666', margin: 0 }}>Create, schedule, and automate authentic Instagram content with AI</p>
          </div>
          
          <div style={{ display: 'flex', gap: '16px' }}>
            {userProfile.isConfigured && instagramConnected && (
              <button onClick={startAutomation} disabled={loading || automationConfig.enabled} style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '16px 28px', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: loading || automationConfig.enabled ? 'not-allowed' : 'pointer', background: loading || automationConfig.enabled ? '#bdc3c7' : 'linear-gradient(135deg, #E4405F, #C13584)', color: 'white', boxShadow: '0 6px 20px rgba(228, 64, 95, 0.4)', transition: 'all 0.3s ease' }}>
                <span>🚀</span><span>{automationConfig.enabled ? 'Automation Active' : 'Start Automation'}</span>
              </button>
            )}
          </div>
        </header>

        <div style={{ padding: '40px 48px' }}>
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(15px)', borderRadius: '24px', padding: '40px', boxShadow: '0 10px 40px rgba(0, 0, 0, 0.1)', border: '1px solid rgba(255, 255, 255, 0.2)', maxWidth: '1200px', margin: '0 auto' }}>
            
            {activeTab === 'setup' && (
              <div>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '40px', textAlign: 'center' }}>AI Profile Configuration</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '24px', marginBottom: '24px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
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
                  <button onClick={saveUserProfile} disabled={!userProfile.businessType} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '12px', padding: '20px 40px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: userProfile.businessType ? 'pointer' : 'not-allowed', background: userProfile.businessType ? 'linear-gradient(135deg, #E4405F, #C13584)' : '#bdc3c7', color: 'white', boxShadow: '0 6px 20px rgba(228, 64, 95, 0.4)', margin: '0 auto', transition: 'all 0.3s ease' }}>
                    <span>✅</span>Save Configuration
                  </button>
                </div>

                {userProfile.isConfigured && (
                  <div style={{ marginTop: '24px', padding: '20px', backgroundColor: 'rgba(34, 197, 94, 0.1)', borderRadius: '16px', border: '2px solid rgba(34, 197, 94, 0.3)' }}>
                    <div style={{ color: '#155724', fontWeight: '700', marginBottom: '8px', fontSize: '18px' }}>Profile Configured Successfully!</div>
                    <div style={{ color: '#155724', fontSize: '16px' }}>AI is ready for human-like content generation on Instagram.</div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'connect' && (
              <div style={{ textAlign: 'center' }}>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '20px' }}>Instagram Connection</h2>
                
                {instagramConnected ? (
                  <div>
                    <div style={{ fontSize: '80px', marginBottom: '20px' }}>✅</div>
                    <h3 style={{ fontSize: '24px', fontWeight: '600', color: '#22c55e', marginBottom: '16px' }}>Instagram Connected Successfully!</h3>
                    <div style={{ background: 'rgba(34, 197, 94, 0.1)', padding: '24px', borderRadius: '16px', marginBottom: '32px', border: '2px solid rgba(34, 197, 94, 0.3)' }}>
                      <p style={{ fontSize: '18px', color: '#155724', marginBottom: '8px', fontWeight: '600' }}>Connected Account: @{instagramUsername}</p>
                      <p style={{ fontSize: '16px', color: '#155724' }}>Account Type: {accountType}</p>
                    </div>
                  </div>
                ) : (
                  <div>
                    <div style={{ fontSize: '80px', marginBottom: '20px' }}>📸</div>
                    <h3 style={{ fontSize: '24px', fontWeight: '600', color: '#666', marginBottom: '24px' }}>Connect Your Instagram Account</h3>
                    <p style={{ fontSize: '16px', color: '#666', marginBottom: '32px', lineHeight: 1.6 }}>
                      Connect your Instagram account to start creating and scheduling authentic, AI-generated content that grows your following and engagement.
                    </p>
                    <button onClick={handleInstagramConnect} disabled={loading} style={{ padding: '20px 40px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: loading ? 'not-allowed' : 'pointer', background: loading ? '#bdc3c7' : 'linear-gradient(135deg, #E4405F, #C13584)', color: 'white', boxShadow: '0 6px 20px rgba(228, 64, 95, 0.4)', transition: 'all 0.3s ease' }}>
                      {loading ? 'Connecting...' : '🔗 Connect Instagram Account'}
                    </button>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'create' && (
              <div>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '40px', textAlign: 'center' }}>Instagram Content Creator</h2>
                
                {!instagramConnected ? (
                  <div style={{ textAlign: 'center', padding: '40px' }}>
                    <p style={{ fontSize: '18px', color: '#666', marginBottom: '24px' }}>Please connect your Instagram account first to create content.</p>
                    <button onClick={() => setActiveTab('connect')} style={{ padding: '16px 32px', background: '#E4405F', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '600', cursor: 'pointer' }}>
                      Go to Connection
                    </button>
                  </div>
                ) : !userProfile.isConfigured ? (
                  <div style={{ textAlign: 'center', padding: '40px' }}>
                    <p style={{ fontSize: '18px', color: '#666', marginBottom: '24px' }}>Please configure your profile first to generate content.</p>
                    <button onClick={() => setActiveTab('setup')} style={{ padding: '16px 32px', background: '#E4405F', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '600', cursor: 'pointer' }}>
                      Go to Profile Setup
                    </button>
                  </div>
                ) : (
                  <div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr auto', gap: '24px', marginBottom: '32px', alignItems: 'end' }}>
                      <div>
                        <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151', display: 'block', marginBottom: '10px' }}>Content Type</label>
                        <select value={postCreator.contentType} onChange={(e) => setPostCreator(prev => ({ ...prev, contentType: e.target.value }))} style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', fontWeight: '500', width: '100%' }}>
                          {Object.entries(CONTENT_TYPES).map(([key, desc]) => (
                            <option key={key} value={key}>{desc}</option>
                          ))}
                        </select>
                      </div>
                      <button onClick={generateInstagramContent} disabled={postCreator.isGeneratingContent} style={{ padding: '20px 32px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: postCreator.isGeneratingContent ? 'not-allowed' : 'pointer', background: postCreator.isGeneratingContent ? '#bdc3c7' : 'linear-gradient(135deg, #667eea, #764ba2)', color: 'white', boxShadow: '0 6px 20px rgba(102, 126, 234, 0.4)', transition: 'all 0.3s ease' }}>
                        {postCreator.isGeneratingContent ? 'Generating...' : '🤖 Generate Content'}
                      </button>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                      <div>
                        <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151', display: 'block', marginBottom: '10px' }}>Instagram Caption</label>
                        <textarea value={postCreator.caption} onChange={(e) => setPostCreator(prev => ({ ...prev, caption: e.target.value }))} placeholder="Write your Instagram caption here or generate with AI..." rows="8" style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', resize: 'vertical', fontWeight: '500', lineHeight: 1.6, width: '100%' }} />
                        
                        <div style={{ marginTop: '20px' }}>
                          <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151', display: 'block', marginBottom: '10px' }}>Hashtags ({postCreator.hashtags.length}/30)</label>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '12px', minHeight: '40px', padding: '12px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', background: 'white' }}>
                            {postCreator.hashtags.map(hashtag => (
                              <span key={hashtag} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 8px', background: '#E4405F', color: 'white', borderRadius: '12px', fontSize: '12px', fontWeight: '600' }}>
                                {hashtag}
                                <button onClick={() => removeHashtag(hashtag)} style={{ background: 'none', border: 'none', color: 'white', fontSize: '14px', cursor: 'pointer', padding: '0' }}>×</button>
                              </span>
                            ))}
                          </div>
                          
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {Object.entries(POPULAR_HASHTAGS).map(([category, tags]) => (
                              <div key={category} style={{ marginBottom: '8px' }}>
                                <div style={{ fontSize: '12px', color: '#666', marginBottom: '4px', fontWeight: '600', textTransform: 'capitalize' }}>{category}:</div>
                                <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                                  {tags.map(tag => (
                                    <button key={tag} onClick={() => addHashtag(tag)} disabled={postCreator.hashtags.includes(tag) || postCreator.hashtags.length >= 30} style={{ padding: '2px 6px', fontSize: '11px', background: postCreator.hashtags.includes(tag) ? '#d1d5db' : '#f3f4f6', color: postCreator.hashtags.includes(tag) ? '#666' : '#374151', border: '1px solid #e5e7eb', borderRadius: '8px', cursor: postCreator.hashtags.includes(tag) || postCreator.hashtags.length >= 30 ? 'not-allowed' : 'pointer', fontWeight: '500' }}>
                                      {tag}
                                    </button>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>

                      <div>
                        <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151', display: 'block', marginBottom: '10px' }}>Image Description</label>
                        <textarea value={postCreator.imagePrompt} onChange={(e) => setPostCreator(prev => ({ ...prev, imagePrompt: e.target.value }))} placeholder="Describe the image you want to generate..." rows="4" style={{ padding: '16px 20px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '12px', fontSize: '16px', background: 'white', resize: 'vertical', fontWeight: '500', lineHeight: 1.6, width: '100%', marginBottom: '16px' }} />
                        
                        <button onClick={generateInstagramImage} disabled={postCreator.isGeneratingImage || !postCreator.imagePrompt} style={{ width: '100%', padding: '16px 20px', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: (postCreator.isGeneratingImage || !postCreator.imagePrompt) ? 'not-allowed' : 'pointer', background: (postCreator.isGeneratingImage || !postCreator.imagePrompt) ? '#bdc3c7' : 'linear-gradient(135deg, #10b981, #059669)', color: 'white', boxShadow: '0 6px 20px rgba(16, 185, 129, 0.4)', transition: 'all 0.3s ease', marginBottom: '20px' }}>
                          {postCreator.isGeneratingImage ? 'Generating Image...' : '🎨 Generate Image'}
                        </button>

                        {postCreator.generatedImage && (
                          <div style={{ marginBottom: '20px' }}>
                            <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151', display: 'block', marginBottom: '10px' }}>Generated Image</label>
                            <img src={postCreator.generatedImage} alt="Generated" style={{ width: '100%', borderRadius: '12px', border: '2px solid rgba(0, 0, 0, 0.1)' }} />
                          </div>
                        )}

                        <button onClick={publishInstagramPost} disabled={loading || !postCreator.caption} style={{ width: '100%', padding: '20px 20px', border: 'none', borderRadius: '16px', fontSize: '18px', fontWeight: '700', cursor: (loading || !postCreator.caption) ? 'not-allowed' : 'pointer', background: (loading || !postCreator.caption) ? '#bdc3c7' : 'linear-gradient(135deg, #E4405F, #C13584)', color: 'white', boxShadow: '0 6px 20px rgba(228, 64, 95, 0.4)', transition: 'all 0.3s ease' }}>
                          {loading ? 'Publishing...' : '🚀 Publish to Instagram'}
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'automate' && (
              <div>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '40px', textAlign: 'center' }}>Instagram Automation Settings</h2>
                
                {!userProfile.isConfigured ? (
                  <div style={{ textAlign: 'center', padding: '40px' }}>
                    <p style={{ fontSize: '18px', color: '#666', marginBottom: '24px' }}>Please configure your profile first to set up automation.</p>
                    <button onClick={() => setActiveTab('setup')} style={{ padding: '16px 32px', background: '#E4405F', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '600', cursor: 'pointer' }}>
                      Go to Profile Setup
                    </button>
                  </div>
                ) : !instagramConnected ? (
                  <div style={{ textAlign: 'center', padding: '40px' }}>
                    <p style={{ fontSize: '18px', color: '#666', marginBottom: '24px' }}>Please connect your Instagram account first to set up automation.</p>
                    <button onClick={() => setActiveTab('connect')} style={{ padding: '16px 32px', background: '#E4405F', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '600', cursor: 'pointer' }}>
                      Go to Connection
                    </button>
                  </div>
                ) : (
                  <div style={{ padding: '32px', background: 'rgba(255,255,255,0.7)', borderRadius: '20px', border: '3px solid #E4405F' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '24px' }}>
                      <span style={{ fontSize: '40px' }}>📸</span>
                      <h3 style={{ margin: 0, color: '#E4405F', fontSize: '24px', fontWeight: '700' }}>Instagram Auto-Posting</h3>
                    </div>
                    
                    <div style={{ marginBottom: '20px' }}>
                      <label style={{ display: 'block', fontSize: '16px', fontWeight: '700', marginBottom: '12px', color: '#374151' }}>Posts Per Day</label>
                      <input type="number" min="1" max="3" value={automationConfig.postsPerDay} onChange={(e) => setAutomationConfig(prev => ({ ...prev, postsPerDay: parseInt(e.target.value) || 1 }))} style={{ padding: '12px 16px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '10px', width: '100px', fontSize: '16px', fontWeight: '600' }} />
                      <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '6px' }}>Recommended: 1-2 posts per day</div>
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                        <label style={{ fontSize: '16px', fontWeight: '700', color: '#374151' }}>Posting Times</label>
                        <button type="button" onClick={addTime} style={{ padding: '8px 16px', fontSize: '12px', background: '#E4405F', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>Add +5min</button>
                      </div>
                      
                      <input type="time" onChange={(e) => { if (e.target.value && !automationConfig.postingTimes.includes(e.target.value)) { setAutomationConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, e.target.value].sort() })); e.target.value = ''; } }} style={{ padding: '10px 12px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '8px', fontSize: '14px', marginBottom: '12px', width: '100%' }} />

                      {automationConfig.postingTimes.length > 0 && (
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                          {automationConfig.postingTimes.map(time => (
                            <span key={time} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 12px', background: 'white', border: '2px solid #E4405F40', borderRadius: '16px', color: '#E4405F', fontSize: '13px', fontWeight: '600' }}>
                              {time}
                              <button onClick={() => removeTime(time)} style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '16px', cursor: 'pointer', padding: '0', lineHeight: '1' }}>×</button>
                            </span>
                          ))}
                        </div>
                      )}
                    </div>

                    <div style={{ padding: '16px', backgroundColor: '#E4405F15', borderRadius: '12px', marginTop: '20px' }}>
                      <h4 style={{ margin: '0 0 8px 0', color: '#E4405F', fontSize: '16px', fontWeight: '700' }}>Automation Status:</h4>
                      <div style={{ fontSize: '14px', color: '#374151', fontWeight: '500' }}>
                        {automationConfig.enabled ? (
                          <span style={{ color: '#22c55e' }}>✅ Active - {automationConfig.postsPerDay} posts/day</span>
                        ) : (
                          <span style={{ color: '#ef4444' }}>⏸️ Inactive - Configure and start automation</span>
                        )}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'analytics' && (
              <div>
                <h2 style={{ fontSize: '32px', fontWeight: '700', color: '#333', marginBottom: '40px', textAlign: 'center' }}>Instagram Analytics & Performance</h2>
                
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px', marginBottom: '40px' }}>
                  <div style={{ background: 'white', borderRadius: '16px', padding: '28px', boxShadow: '0 6px 20px rgba(0, 0, 0, 0.08)', border: '2px solid #E4405F30' }}>
                    <h3 style={{ marginTop: 0, fontSize: '20px', fontWeight: '700', color: '#E4405F' }}>📸 Instagram Connection</h3>
                    <div style={{ padding: '8px 16px', borderRadius: '20px', fontSize: '14px', fontWeight: '700', backgroundColor: instagramConnected ? '#d4edda' : '#f8d7da', color: instagramConnected ? '#155724' : '#721c24', display: 'inline-block', marginBottom: '12px' }}>
                      {instagramConnected ? 'Connected' : 'Disconnected'}
                    </div>
                    {instagramUsername && <p style={{ margin: '12px 0 0 0', color: '#666', fontSize: '16px' }}>Connected as: <strong>@{instagramUsername}</strong></p>}
                    <p style={{ margin: '8px 0 0 0', color: '#666', fontSize: '14px' }}>Account Type: {accountType}</p>
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

                  <div style={{ background: 'white', borderRadius: '16px', padding: '28px', boxShadow: '0 6px 20px rgba(0, 0, 0, 0.08)', border: '2px solid #10b98130' }}>
                    <h3 style={{ marginTop: 0, fontSize: '20px', fontWeight: '700', color: '#10b981' }}>⚡ Automation Status</h3>
                    <div style={{ padding: '8px 16px', borderRadius: '20px', fontSize: '14px', fontWeight: '700', backgroundColor: automationConfig.enabled ? '#d4edda' : '#f8d7da', color: automationConfig.enabled ? '#155724' : '#721c24', display: 'inline-block', marginBottom: '12px' }}>
                      {automationConfig.enabled ? 'Active' : 'Inactive'}
                    </div>
                    {automationConfig.enabled && (
                      <p style={{ margin: '12px 0 0 0', color: '#666', fontSize: '16px' }}>Posts per day: <strong>{automationConfig.postsPerDay}</strong></p>
                    )}
                  </div>
                </div>

                <div style={{ padding: '32px', backgroundColor: '#f8f9fa', borderRadius: '20px', border: '2px solid rgba(228, 64, 95, 0.2)' }}>
                  <h3 style={{ marginTop: 0, fontSize: '24px', fontWeight: '700', color: '#E4405F', textAlign: 'center', marginBottom: '32px' }}>📊 Performance Metrics</h3>
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

export defastagramAutomation;