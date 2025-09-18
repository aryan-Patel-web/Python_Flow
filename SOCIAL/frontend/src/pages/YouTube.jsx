import React, { useState, useEffect } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const YouTubeAutomation = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('connect');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [oauthUrl, setOauthUrl] = useState('');
  
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
    fetchAutomationStatus();
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');
    if (code && state === 'youtube_oauth') { handleOAuthCallback(code); }
  }, []);

  const fetchAutomationStatus = async () => {
    try {
      const response = await fetch(`${API_BASE}/youtube/status`, { headers: { 'Authorization': `Bearer ${user?.token}` } });
      const data = await response.json();
      if (data.success) { setStatus(data); if (data.youtube_automation?.config) { setConfig(prev => ({ ...prev, ...data.youtube_automation.config })); } }
    } catch (error) { console.error('Status fetch failed:', error); }
  };

  const generateOAuthUrl = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/youtube/oauth-url`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${user?.token}` }, body: JSON.stringify({ user_id: user?.id || 'test_user', state: 'youtube_oauth' }) });
      const result = await response.json();
      if (result.success) { setOauthUrl(result.authorization_url); window.open(result.authorization_url, '_blank'); } else { alert(`OAuth URL generation failed: ${result.error}`); }
    } catch (error) { alert(`OAuth failed: ${error.message}`); } finally { setLoading(false); }
  };

  const handleOAuthCallback = async (code) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/youtube/oauth-callback`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${user?.token}` }, body: JSON.stringify({ user_id: user?.id || 'test_user', code: code }) });
      const result = await response.json();
      if (result.success) { alert('YouTube connected successfully!'); fetchAutomationStatus(); setActiveTab('setup'); window.history.replaceState({}, document.title, window.location.pathname); } else { alert(`YouTube connection failed: ${result.error}`); }
    } catch (error) { alert(`Connection failed: ${error.message}`); } finally { setLoading(false); }
  };

  const setupYouTubeAutomation = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/youtube/setup-automation`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${user?.token}` }, body: JSON.stringify({ user_id: user?.id || 'test_user', config: { ...config, user_id: user?.id || 'test_user' } }) });
      const result = await response.json();
      if (result.success) { alert('YouTube automation setup successful!'); fetchAutomationStatus(); setActiveTab('content'); } else { alert(`Setup failed: ${result.error}`); }
    } catch (error) { alert(`Setup failed: ${error.message}`); } finally { setLoading(false); }
  };

  const generateContent = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/ai/generate-youtube-content`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${user?.token}` }, body: JSON.stringify({ content_type: contentData.content_type, topic: contentData.topic, target_audience: contentData.target_audience, duration_seconds: contentData.duration_seconds, style: contentData.style }) });
      const result = await response.json();
      if (result.success) { setGeneratedContent(result); setContentData(prev => ({ ...prev, title: result.title || '', description: result.description || '' })); } else { alert(`Content generation failed: ${result.error}`); }
    } catch (error) { alert(`Content generation failed: ${error.message}`); } finally { setLoading(false); }
  };

  const uploadVideo = async () => {
    if (!contentData.video_url || !contentData.title) { alert('Please provide video URL and title'); return; }
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/youtube/upload`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${user?.token}` }, body: JSON.stringify({ user_id: user?.id || 'test_user', content_type: contentData.content_type, title: contentData.title, description: contentData.description, video_url: contentData.video_url }) });
      const result = await response.json();
      if (result.success) { alert(`Video uploaded successfully! URL: ${result.video_url}`); setContentData(prev => ({ ...prev, title: '', description: '', video_url: '' })); fetchAutomationStatus(); fetchAnalytics(); } else { alert(`Upload failed: ${result.error}`); }
    } catch (error) { alert(`Upload failed: ${error.message}`); } finally { setLoading(false); }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await fetch(`${API_BASE}/youtube/analytics?days=30`, { headers: { 'Authorization': `Bearer ${user?.token}` } });
      const data = await response.json();
      if (data.success) { setAnalytics(data); }
    } catch (error) { console.error('Analytics fetch failed:', error); }
  };

  const TabButton = ({ id, label, emoji, active, onClick }) => (
    <button onClick={onClick} style={{ padding: '12px 24px', background: active ? '#FF0000' : 'transparent', color: active ? 'white' : '#FF0000', border: `2px solid #FF0000`, borderRadius: '12px', cursor: 'pointer', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}>
      <span>{emoji}</span>{label}
    </button>
  );

  const StatusCard = ({ title, value, color = '#FF0000' }) => (
    <div style={{ background: 'white', borderRadius: '12px', padding: '20px', textAlign: 'center', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)', border: `2px solid ${color}` }}>
      <div style={{ fontSize: '24px', fontWeight: 'bold', color, marginBottom: '8px' }}>{value}</div>
      <div style={{ fontSize: '14px', color: '#666' }}>{title}</div>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #FF0000 0%, #CC0000 100%)', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '40px', color: 'white' }}>
          <h1 style={{ fontSize: '48px', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px' }}>
            <span style={{ fontSize: '56px' }}>📺</span>YouTube Automation Studio
          </h1>
          <p style={{ fontSize: '20px', opacity: 0.9, maxWidth: '800px', margin: '0 auto' }}>Automate your YouTube channel with AI-generated content, smart scheduling, and analytics tracking</p>
        </div>

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
                <h3 style={{ color: '#333', marginBottom: '16px' }}>{status?.youtube_connected ? 'YouTube Connected!' : 'Connect to Get Started'}</h3>
                <p style={{ color: '#666', lineHeight: 1.6, marginBottom: '30px' }}>{status?.youtube_connected ? 'Your YouTube channel is connected and ready for automation.' : 'Connect your YouTube channel to start automating content.'}</p>
              </div>
              {status?.youtube_connected ? (
                <div style={{ background: '#d4edda', border: '1px solid #c3e6cb', borderRadius: '8px', padding: '16px', marginBottom: '20px', color: '#155724' }}>
                  <h4 style={{ margin: '0 0 8px 0' }}>✅ Connected Successfully</h4>
                  <p style={{ margin: 0, fontSize: '14px' }}>Channel: {status.channel_info?.channel_name || 'YouTube Channel'}</p>
                </div>
              ) : (
                <button onClick={generateOAuthUrl} disabled={loading} style={{ padding: '16px 32px', background: loading ? '#ccc' : '#FF0000', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: loading ? 'not-allowed' : 'pointer' }}>
                  {loading ? '⏳ Generating...' : '🔗 Connect YouTube Channel'}
                </button>
              )}
              {oauthUrl && !status?.youtube_connected && (
                <div style={{ marginTop: '20px', padding: '16px', background: '#fff3cd', border: '1px solid #ffeeba', borderRadius: '8px', color: '#856404' }}>
                  <p style={{ margin: 0, fontSize: '14px' }}>A new window should have opened. Please complete the authorization and return here.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Setup Tab */}
        {activeTab === 'setup' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#FF0000', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>YouTube Automation Setup</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '30px' }}>
              <div>
                <h3 style={{ color: '#CC0000', marginBottom: '20px' }}>Content Settings</h3>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Content Type</label>
                  <select value={config.content_type} onChange={(e) => setConfig(prev => ({ ...prev, content_type: e.target.value }))} style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }}>
                    <option value="shorts">YouTube Shorts</option>
                    <option value="videos">Regular Videos</option>
                    <option value="both">Both</option>
                  </select>
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Content Categories</label>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {['Technology', 'Business', 'Education', 'Entertainment', 'Gaming', 'Sports'].map(category => (
                      <button key={category} onClick={() => setConfig(prev => ({ ...prev, content_categories: prev.content_categories.includes(category) ? prev.content_categories.filter(c => c !== category) : [...prev.content_categories, category] }))} style={{ padding: '8px 16px', background: config.content_categories.includes(category) ? '#FF0000' : 'white', color: config.content_categories.includes(category) ? 'white' : '#FF0000', border: '2px solid #FF0000', borderRadius: '20px', cursor: 'pointer', fontSize: '12px', fontWeight: '600' }}>
                        {category}
                      </button>
                    ))}
                  </div>
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Privacy Status</label>
                  <select value={config.privacy_status} onChange={(e) => setConfig(prev => ({ ...prev, privacy_status: e.target.value }))} style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }}>
                    <option value="public">Public</option>
                    <option value="unlisted">Unlisted</option>
                    <option value="private">Private</option>
                  </select>
                </div>
              </div>
              <div>
                <h3 style={{ color: '#CC0000', marginBottom: '20px' }}>Automation Options</h3>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', marginBottom: '10px' }}>
                    <input type="checkbox" checked={config.auto_generate_titles} onChange={(e) => setConfig(prev => ({ ...prev, auto_generate_titles: e.target.checked }))} style={{ width: '20px', height: '20px' }} />
                    <span style={{ fontWeight: '600', color: '#333' }}>Auto-generate Titles</span>
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer', marginBottom: '10px' }}>
                    <input type="checkbox" checked={config.auto_generate_descriptions} onChange={(e) => setConfig(prev => ({ ...prev, auto_generate_descriptions: e.target.checked }))} style={{ width: '20px', height: '20px' }} />
                    <span style={{ fontWeight: '600', color: '#333' }}>Auto-generate Descriptions</span>
                  </label>
                  <label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}>
                    <input type="checkbox" checked={config.auto_add_tags} onChange={(e) => setConfig(prev => ({ ...prev, auto_add_tags: e.target.checked }))} style={{ width: '20px', height: '20px' }} />
                    <span style={{ fontWeight: '600', color: '#333' }}>Auto-add Tags</span>
                  </label>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Shorts per Day</label>
                    <input type="number" value={config.shorts_per_day} onChange={(e) => setConfig(prev => ({ ...prev, shorts_per_day: parseInt(e.target.value) }))} min="1" max="10" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} />
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Videos per Week</label>
                    <input type="number" value={config.videos_per_week} onChange={(e) => setConfig(prev => ({ ...prev, videos_per_week: parseInt(e.target.value) }))} min="1" max="21" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} />
                  </div>
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Upload Schedule</label>
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                    {['09:00', '12:00', '15:00', '18:00', '21:00'].map(time => (
                      <button key={time} onClick={() => setConfig(prev => ({ ...prev, upload_schedule: prev.upload_schedule.includes(time) ? prev.upload_schedule.filter(t => t !== time) : [...prev.upload_schedule, time] }))} style={{ padding: '8px 16px', background: config.upload_schedule.includes(time) ? '#FF0000' : 'white', color: config.upload_schedule.includes(time) ? 'white' : '#FF0000', border: '2px solid #FF0000', borderRadius: '8px', cursor: 'pointer', fontSize: '14px', fontWeight: '600' }}>
                        {time}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
            <div style={{ textAlign: 'center', marginTop: '30px' }}>
              <button onClick={setupYouTubeAutomation} disabled={loading || !status?.youtube_connected} style={{ padding: '16px 32px', background: loading || !status?.youtube_connected ? '#ccc' : '#FF0000', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: loading || !status?.youtube_connected ? 'not-allowed' : 'pointer' }}>
                {loading ? '⏳ Setting up...' : '🚀 Setup Automation'}
              </button>
            </div>
          </div>
        )}

        {/* Content Tab */}
        {activeTab === 'content' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#FF0000', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>Create & Upload Content</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '30px' }}>
              <div>
                <h3 style={{ color: '#CC0000', marginBottom: '20px' }}>Content Generation</h3>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Topic</label>
                  <input type="text" value={contentData.topic} onChange={(e) => setContentData(prev => ({ ...prev, topic: e.target.value }))} placeholder="Enter video topic" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} />
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Content Type</label>
                    <select value={contentData.content_type} onChange={(e) => setContentData(prev => ({ ...prev, content_type: e.target.value }))} style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }}>
                      <option value="shorts">YouTube Shorts</option>
                      <option value="video">Regular Video</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Style</label>
                    <select value={contentData.style} onChange={(e) => setContentData(prev => ({ ...prev, style: e.target.value }))} style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }}>
                      <option value="engaging">Engaging</option>
                      <option value="educational">Educational</option>
                      <option value="entertaining">Entertaining</option>
                      <option value="professional">Professional</option>
                    </select>
                  </div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px' }}>
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Target Audience</label>
                    <select value={contentData.target_audience} onChange={(e) => setContentData(prev => ({ ...prev, target_audience: e.target.value }))} style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }}>
                      <option value="general">General</option>
                      <option value="teens">Teens</option>
                      <option value="adults">Adults</option>
                      <option value="professionals">Professionals</option>
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Duration (seconds)</label>
                    <input type="number" value={contentData.duration_seconds} onChange={(e) => setContentData(prev => ({ ...prev, duration_seconds: parseInt(e.target.value) }))} min="15" max="3600" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} />
                  </div>
                </div>
                <button onClick={generateContent} disabled={loading || !contentData.topic} style={{ width: '100%', padding: '12px 24px', background: loading || !contentData.topic ? '#ccc' : '#FF0000', color: 'white', border: 'none', borderRadius: '8px', cursor: loading || !contentData.topic ? 'not-allowed' : 'pointer', fontWeight: '600', marginBottom: '20px' }}>
                  {loading ? '⏳ Generating...' : '🤖 Generate AI Content'}
                </button>
                {generatedContent && (
                  <div style={{ background: '#f8f9fa', borderRadius: '8px', padding: '16px', marginBottom: '20px' }}>
                    <h4 style={{ color: '#CC0000', marginBottom: '12px' }}>Generated Content</h4>
                    <div style={{ fontSize: '14px', color: '#333' }}>
                      <strong>Title:</strong> {generatedContent.title}<br />
                      <strong>Tags:</strong> {generatedContent.tags?.join(', ')}<br />
                      <strong>Script:</strong> {generatedContent.script?.substring(0, 100)}...
                    </div>
                  </div>
                )}
              </div>
              <div>
                <h3 style={{ color: '#CC0000', marginBottom: '20px' }}>Upload Video</h3>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Video URL</label>
                  <input type="url" value={contentData.video_url} onChange={(e) => setContentData(prev => ({ ...prev, video_url: e.target.value }))} placeholder="https://example.com/video.mp4" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} />
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Title</label>
                  <input type="text" value={contentData.title} onChange={(e) => setContentData(prev => ({ ...prev, title: e.target.value }))} placeholder="Video title" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} />
                </div>
                <div style={{ marginBottom: '20px' }}>
                  <label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Description</label>
                  <textarea value={contentData.description} onChange={(e) => setContentData(prev => ({ ...prev, description: e.target.value }))} placeholder="Video description" rows="6" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', resize: 'vertical', boxSizing: 'border-box' }} />
                </div>
                <button onClick={uploadVideo} disabled={loading || !contentData.video_url || !contentData.title} style={{ width: '100%', padding: '12px 24px', background: loading || !contentData.video_url || !contentData.title ? '#ccc' : '#FF0000', color: 'white', border: 'none', borderRadius: '8px', cursor: loading || !contentData.video_url || !contentData.title ? 'not-allowed' : 'pointer', fontWeight: '600' }}>
                  {loading ? '⏳ Uploading...' : '📤 Upload to YouTube'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Dashboard Tab */}
        {activeTab === 'dashboard' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#FF0000', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>YouTube Dashboard</h2>
            {status && (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  <StatusCard title="Total Uploads" value={status.youtube_automation?.stats?.total_uploads || 0} />
                  <StatusCard title="Successful" value={status.youtube_automation?.stats?.successful_uploads || 0} color="#00C851" />
                  <StatusCard title="Failed" value={status.youtube_automation?.stats?.failed_uploads || 0} color="#ff4444" />
                  <StatusCard title="Connection" value={status.youtube_connected ? "Connected" : "Disconnected"} color={status.youtube_connected ? "#00C851" : "#ff4444"} />
                </div>
                {status.channel_info && (
                  <div style={{ background: '#f8f9fa', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
                    <h3 style={{ color: '#CC0000', marginBottom: '16px' }}>Channel Information</h3>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                      <div><strong>Channel:</strong> {status.channel_info.channel_name}</div>
                      <div><strong>Subscribers:</strong> {status.channel_info.subscriber_count}</div>
                      <div><strong>Videos:</strong> {status.channel_info.video_count}</div>
                      <div><strong>Views:</strong> {status.channel_info.view_count}</div>
                    </div>
                  </div>
                )}
                <div style={{ background: '#f8f9fa', borderRadius: '12px', padding: '20px' }}>
                  <h3 style={{ color: '#CC0000', marginBottom: '16px' }}>Automation Status</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span>{status.youtube_automation?.enabled ? '✅' : '❌'}</span>
                      <span style={{ fontWeight: '600', color: status.youtube_automation?.enabled ? '#00C851' : '#666' }}>
                        Automation {status.youtube_automation?.enabled ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div><strong>Content Type:</strong> {status.youtube_automation?.config?.content_type || 'Not set'}</div>
                    <div><strong>Privacy:</strong> {status.youtube_automation?.config?.privacy_status || 'Not set'}</div>
                    <div><strong>Schedule:</strong> {status.youtube_automation?.config?.upload_schedule?.join(', ') || 'Not set'}</div>
                  </div>
                </div>
              </>
            )}
            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button onClick={fetchAutomationStatus} style={{ padding: '12px 24px', background: '#FF0000', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600', marginRight: '12px' }}>🔄 Refresh Status</button>
              <button onClick={() => { fetchAnalytics(); setActiveTab('analytics'); }} style={{ padding: '12px 24px', background: '#CC0000', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>📈 View Analytics</button>
            </div>
          </div>
        )}

        {/* Analytics Tab */}
        {activeTab === 'analytics' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#FF0000', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>YouTube Analytics</h2>
            <div style={{ textAlign: 'center', marginBottom: '30px' }}>
              <button onClick={fetchAnalytics} disabled={loading} style={{ padding: '12px 24px', background: loading ? '#ccc' : '#FF0000', color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: '600' }}>
                {loading ? '⏳ Loading...' : '📊 Load Analytics'}
              </button>
            </div>
            {analytics && (
              <div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  {analytics.channel_statistics && (
                    <>
                      <div style={{ background: 'linear-gradient(135deg, #FF0000, #CC0000)', borderRadius: '12px', padding: '20px', textAlign: 'center', color: 'white' }}>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>{analytics.channel_statistics.subscriberCount || 0}</div>
                        <div style={{ fontSize: '14px', opacity: 0.9 }}>Subscribers</div>
                      </div>
                      <div style={{ background: 'linear-gradient(135deg, #00C851, #00A047)', borderRadius: '12px', padding: '20px', textAlign: 'center', color: 'white' }}>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>{analytics.channel_statistics.viewCount || 0}</div>
                        <div style={{ fontSize: '14px', opacity: 0.9 }}>Total Views</div>
                      </div>
                      <div style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)', borderRadius: '12px', padding: '20px', textAlign: 'center', color: 'white' }}>
                        <div style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '8px' }}>{analytics.channel_statistics.videoCount || 0}</div>
                        <div style={{ fontSize: '14px', opacity: 0.9 }}>Total Videos</div>
                      </div>
                    </>
                  )}
                </div>
                {analytics.recent_videos && analytics.recent_videos.length > 0 && (
                  <div style={{ background: '#f8f9fa', borderRadius: '12px', padding: '20px' }}>
                    <h3 style={{ color: '#CC0000', marginBottom: '16px' }}>Recent Videos</h3>
                    <div style={{ display: 'grid', gap: '16px' }}>
                      {analytics.recent_videos.slice(0, 5).map((video, index) => (
                        <div key={index} style={{ background: 'white', borderRadius: '8px', padding: '16px', display: 'grid', gridTemplateColumns: '1fr auto auto auto', gap: '16px', alignItems: 'center', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
                          <div><strong>{video.title}</strong><br /><small style={{ color: '#666' }}>{new Date(video.published_at).toLocaleDateString()}</small></div>
                          <div style={{ textAlign: 'center' }}><strong>{video.view_count || 0}</strong><br /><small>Views</small></div>
                          <div style={{ textAlign: 'center' }}><strong>{video.like_count || 0}</strong><br /><small>Likes</small></div>
                          <div style={{ textAlign: 'center' }}><strong>{video.comment_count || 0}</strong><br /><small>Comments</small></div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default YouTubeAutomation;