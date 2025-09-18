import React, { useState, useEffect } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const YouTubeAutomation = () => {
  const { user, token } = useAuth(); // Get both user and token from auth context
  const [activeTab, setActiveTab] = useState('connect');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState('');
  
  const [config, setConfig] = useState({
    content_type: 'shorts',
    upload_schedule: ['09:00', '15:00', '21:00'],
    content_categories: ['Technology', 'Business', 'Education'],
    auto_generate_titles: true,
    auto_generate_descriptions: true,
    auto_add_tags: true,
    privacy_status: 'public',
    shorts_per_day: 3,
    videos_per_week: 2
  });
  
  const [contentData, setContentData] = useState({
    content_type: 'shorts',
    topic: '',
    target_audience: 'general',
    duration_seconds: 30,
    style: 'engaging',
    title: '',
    description: '',
    video_url: ''
  });

  const [generatedContent, setGeneratedContent] = useState(null);
  const [analytics, setAnalytics] = useState(null);

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (user && token) {
      fetchAutomationStatus();
    }
    
    // Handle OAuth redirect callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    const error_param = urlParams.get('error');
    
    if (error_param) {
      setError(`OAuth error: ${error_param}`);
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    } else if (code && state === 'youtube_oauth') {
      handleOAuthCallback(code);
    }
  }, [user, token]);







const fetchAutomationStatus = async () => {
  if (!token) return;
  
  try {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    const userObj = userData ? JSON.parse(userData) : null;
    
    if (!userObj || !userObj.user_id) {
      console.error('No user_id found');
      return;
    }
    
    const response = await fetch(`${API_BASE}/api/youtube/status/${userObj.user_id}`, {
      method: 'GET',
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (response.ok) {
      const data = await response.json();
      if (data.success) {
        setStatus(data);
        if (data.youtube_automation?.config) {
          setConfig(prev => ({ ...prev, ...data.youtube_automation.config }));
        }
      }
    } else if (response.status === 404) {
      setStatus({ youtube_connected: false });
    }
  } catch (error) {
    console.error('Status fetch failed:', error);
    setStatus({ youtube_connected: false });
  }
};






// Replace your generateOAuthUrl function in YouTube component with this:
const generateOAuthUrl = async () => {
  if (!token) {
    setError('Please login first');
    return;
  }

  setLoading(true);
  setError('');
  
  try {
    // Get user data from localStorage (this matches your AuthContext)
    const userData = localStorage.getItem('user');
    const userObj = userData ? JSON.parse(userData) : null;
    
    if (!userObj || !userObj.user_id) {
      setError('User ID not found. Please log in again.');
      console.error('User object:', userObj);
      return;
    }

    console.log('Generating OAuth URL for user_id:', userObj.user_id);
    
    const requestPayload = {
      user_id: userObj.user_id, // ✅ Use user_id, not id
      state: 'youtube_oauth'
      // Let backend use default redirect_uri
    };
    
    console.log('Request payload:', requestPayload);
    
    const response = await fetch(`${API_BASE}/api/youtube/oauth-url`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(requestPayload)
    });
    
    console.log('Response status:', response.status);
    console.log('Response ok:', response.ok);
    
    const result = await response.json();
    console.log('Response data:', result);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${JSON.stringify(result)}`);
    }
    
    if (result.success && result.authorization_url) {
      // Redirect to OAuth URL
      window.location.href = result.authorization_url;
    } else {
      setError(result.error || result.message || 'Failed to generate OAuth URL');
    }
  } catch (error) {
    console.error('OAuth URL generation failed:', error);
    setError('Network error: ' + error.message);
  } finally {
    setLoading(false);
  }
};

// Also update your handleOAuthCallback function:
const handleOAuthCallback = async (code) => {
  if (!token) {
    setError('Authentication required');
    return;
  }

  setLoading(true);
  setError('');
  
  try {
    // Get user data from localStorage
    const userData = localStorage.getItem('user');
    const userObj = userData ? JSON.parse(userData) : null;
    
    if (!userObj || !userObj.user_id) {
      setError('User ID not found. Please log in again.');
      return;
    }
    
    const response = await fetch(`${API_BASE}/api/youtube/oauth-callback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        user_id: userObj.user_id, // ✅ Use user_id, not id
        code: code,
        redirect_uri: window.location.origin + '/youtube'
      })
    });
    
    const result = await response.json();
    
    if (result.success) {
      setError('');
      alert('YouTube connected successfully!');
      await fetchAutomationStatus();
      setActiveTab('setup');
      // Clear URL parameters
      window.history.replaceState({}, document.title, window.location.pathname);
    } else {
      setError(result.error || result.message || 'YouTube connection failed');
    }
  } catch (error) {
    setError('Connection failed: ' + error.message);
    console.error('OAuth callback failed:', error);
  } finally {
    setLoading(false);
  }
};









  const setupYouTubeAutomation = async () => {
    if (!token) {
      setError('Authentication required');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE}/api/youtube/setup-automation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: user?.id,
          config: {
            ...config,
            user_id: user?.id
          }
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert('YouTube automation setup successful!');
        await fetchAutomationStatus();
        setActiveTab('content');
      } else {
        setError(result.error || result.message || 'Setup failed');
      }
    } catch (error) {
      setError('Setup failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const generateContent = async () => {
    if (!token) {
      setError('Authentication required');
      return;
    }

    if (!contentData.topic) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE}/api/ai/generate-youtube-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          content_type: contentData.content_type,
          topic: contentData.topic,
          target_audience: contentData.target_audience,
          duration_seconds: contentData.duration_seconds,
          style: contentData.style
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setGeneratedContent(result);
        setContentData(prev => ({
          ...prev,
          title: result.title || '',
          description: result.description || ''
        }));
        setError('');
      } else {
        setError(result.error || result.message || 'Content generation failed');
      }
    } catch (error) {
      setError('Content generation failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const uploadVideo = async () => {
    if (!token) {
      setError('Authentication required');
      return;
    }

    if (!contentData.video_url || !contentData.title) {
      setError('Please provide video URL and title');
      return;
    }

    setLoading(true);
    setError('');
    
    try {
      const response = await fetch(`${API_BASE}/api/youtube/upload`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          user_id: user?.id,
          content_type: contentData.content_type,
          title: contentData.title,
          description: contentData.description,
          video_url: contentData.video_url
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        alert(`Video uploaded successfully! URL: ${result.video_url}`);
        setContentData(prev => ({ ...prev, title: '', description: '', video_url: '' }));
        await fetchAutomationStatus();
        if (analytics) fetchAnalytics();
        setError('');
      } else {
        setError(result.error || result.message || 'Upload failed');
      }
    } catch (error) {
      setError('Upload failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchAnalytics = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(`${API_BASE}/api/youtube/analytics?days=30`, {
        headers: { 
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setAnalytics(data);
        }
      }
    } catch (error) {
      console.error('Analytics fetch failed:', error);
    }
  };

  const TabButton = ({ id, label, emoji, active, onClick }) => (
    <button onClick={onClick} style={{ padding: '12px 24px', background: active ? '#FF0000' : 'transparent', color: active ? 'white' : '#FF0000', border: '2px solid #FF0000', borderRadius: '12px', cursor: 'pointer', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
      <span>{emoji}</span>{label}
    </button>
  );

  const StatusCard = ({ title, value, color = '#FF0000' }) => (
    <div style={{ background: 'white', borderRadius: '12px', padding: '20px', textAlign: 'center', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)', border: `2px solid ${color}` }}>
      <div style={{ fontSize: '24px', fontWeight: 'bold', color, marginBottom: '8px' }}>{value}</div>
      <div style={{ fontSize: '14px', color: '#666' }}>{title}</div>
    </div>
  );

  // Show login required message if no authentication
  if (!user || !token) {
    return (
      <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
        <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', textAlign: 'center', maxWidth: '500px' }}>
          <h2 style={{ color: '#FF0000', marginBottom: '16px' }}>Authentication Required</h2>
          <p style={{ color: '#666', marginBottom: '20px' }}>Please log in to access YouTube automation features.</p>
          <a href="/login" style={{ padding: '12px 24px', background: '#FF0000', color: 'white', textDecoration: 'none', borderRadius: '8px', fontWeight: '600' }}>
            Go to Login
          </a>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px', color: 'white' }}>
          <h1 style={{ fontSize: '48px', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
            <span style={{ fontSize: '56px' }}>📺</span>YouTube Automation Studio
          </h1>
          <p style={{ fontSize: '20px', opacity: 0.9, maxWidth: '800px', margin: '0 auto' }}>
            Automate your YouTube channel with AI-generated content, smart scheduling, and analytics tracking
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <div style={{ background: '#fee', border: '1px solid #fcc', borderRadius: '12px', padding: '16px', marginBottom: '20px', color: '#c33', textAlign: 'center' }}>
            <strong>Error:</strong> {error}
            <button onClick={() => setError('')} style={{ marginLeft: '10px', background: 'none', border: 'none', color: '#c33', cursor: 'pointer', fontSize: '16px' }}>✕</button>
          </div>
        )}

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginBottom: '40px', flexWrap: 'wrap' }}>
          <TabButton id="connect" label="Connect YouTube" emoji="🔗" active={activeTab === 'connect'} onClick={() => setActiveTab('connect')} />
          <TabButton id="setup" label="Setup Automation" emoji="⚙️" active={activeTab === 'setup'} onClick={() => setActiveTab('setup')} />
          <TabButton id="content" label="Create Content" emoji="🎬" active={activeTab === 'content'} onClick={() => setActiveTab('content')} />
          <TabButton id="dashboard" label="Dashboard" emoji="📊" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <TabButton id="analytics" label="Analytics" emoji="📈" active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')} />
        </div>

        {/* Connect YouTube Tab */}
        {activeTab === 'connect' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#FF0000', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>Connect Your YouTube Channel</h2>
            
            <div style={{ textAlign: 'center', maxWidth: '600px', margin: '0 auto' }}>
              <div style={{ marginBottom: '30px' }}>
                <div style={{ fontSize: '64px', marginBottom: '20px' }}>📺</div>
                <h3 style={{ color: '#333', marginBottom: '16px' }}>
                  {status?.youtube_connected ? 'YouTube Connected!' : 'Connect to Get Started'}
                </h3>
                <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '30px' }}>
                  {status?.youtube_connected 
                    ? 'Your YouTube channel is connected and ready for automation.' 
                    : 'Connect your YouTube channel to start automating content creation and uploads.'}
                </p>
              </div>

              {status?.youtube_connected ? (
                <div style={{ background: '#d4edda', border: '1px solid #c3e6cb', borderRadius: '8px', padding: '16px', marginBottom: '20px', color: '#155724' }}>
                  <h4 style={{ margin: '0 0 8px 0' }}>✅ Connected Successfully</h4>
                  <p style={{ margin: 0, fontSize: '14px' }}>Channel: {status.channel_info?.channel_name || 'YouTube Channel'}</p>
                  <button onClick={() => setActiveTab('setup')} style={{ marginTop: '12px', padding: '8px 16px', background: '#155724', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '600' }}>
                    Continue to Setup →
                  </button>
                </div>
              ) : (
                <button
                  onClick={generateOAuthUrl}
                  disabled={loading}
                  style={{
                    padding: '16px 32px',
                    background: loading ? '#ccc' : '#FF0000',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '700',
                    cursor: loading ? 'not-allowed' : 'pointer'
                  }}
                >
                  {loading ? '⏳ Connecting...' : '🔗 Connect YouTube Channel'}
                </button>
              )}

              <div style={{ marginTop: '30px', padding: '20px', background: '#f8f9fa', borderRadius: '12px', fontSize: '14px', color: '#666' }}>
                <h4 style={{ color: '#333', marginBottom: '12px' }}>📋 What happens next:</h4>
                <ol style={{ textAlign: 'left', paddingLeft: '20px' }}>
                  <li>You'll be redirected to Google's secure authentication page</li>
                  <li>Sign in to your Google account that owns the YouTube channel</li>
                  <li>Grant permissions for YouTube channel management</li>
                  <li>You'll be redirected back here with confirmation</li>
                </ol>
              </div>
            </div>
          </div>
        )}

        {/* Rest of the tabs remain the same as your original code... */}
        {activeTab !== 'connect' && !status?.youtube_connected && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)', textAlign: 'center' }}>
            <h3 style={{ color: '#FF0000', marginBottom: '20px' }}>YouTube Not Connected</h3>
            <p style={{ color: '#666', marginBottom: '20px' }}>Please connect your YouTube channel first to access this feature.</p>
            <button onClick={() => setActiveTab('connect')} style={{ padding: '12px 24px', background: '#FF0000', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>
              Connect YouTube Channel
            </button>
          </div>
        )}

        {/* Include all your other existing tabs (setup, content, dashboard, analytics) here with the same structure as your original code */}
      </div>
    </div>
  );
};

export default YouTubeAutomation;