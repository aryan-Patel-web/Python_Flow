import React, { useState, useEffect } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const WhatsAppAutomation = () => {
  const { user, makeAuthenticatedRequest } = useAuth();
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [config, setConfig] = useState({ business_name: '', phone_number_id: '842943155558927', access_token: 'EAALNGPo4t80BPVCNDAKG9VCphy4OmQxVkZCsZCPAvYZCrHgRfSCmZAcLnRNiOM8MD97IjQNl0p7z2A5WDt3IxjmDRzdJOr1AZCwOr7kVZAZAe81MGsVMbRQks2cSv2jq49LlSa4HFlSLZAbhM8uYezRUNukGcm9oZALUj1u0ACxzZCZCZB9voYbCApSaoZCjA4egSjv45YwZDZD', webhook_verify_token: 'whatsapp_webhook_verify_2024_secure_velocity', auto_reply_enabled: false, campaign_enabled: false, business_hours: { start: '09:00', end: '18:00' }, timezone: 'Asia/Calcutta' });
  const [messageData, setMessageData] = useState({ to: '', message: '', message_type: 'text', business_type: 'general' });
  const [broadcastData, setBroadcastData] = useState({ recipients: '', message: '', media_url: '', media_type: '' });

  useEffect(() => { fetchAutomationStatus(); }, []);

  const fetchAutomationStatus = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/automation/status');
      const data = await response.json();
      if (data.success) { setStatus(data); if (data.whatsapp_automation?.config) { setConfig(prev => ({ ...prev, ...data.whatsapp_automation.config })); }}
    } catch (error) { console.error('Status fetch failed:', error); }
  };

  const setupWhatsAppAutomation = async () => {
    setLoading(true);
    try {
      const response = await makeAuthenticatedRequest(`/api/whatsapp/setup?phone_number_id=${config.phone_number_id}&access_token=${config.access_token}&business_name=${config.business_name}`, { method: 'POST' });
      const result = await response.json();
      if (result.success) { alert('WhatsApp automation setup successful!'); fetchAutomationStatus(); setActiveTab('dashboard'); } else { alert(`Setup failed: ${result.error}`); }
    } catch (error) { alert(`Setup failed: ${error.message}`); } finally { setLoading(false); }
  };

  const sendMessage = async () => {
    if (!messageData.to || !messageData.message) { alert('Please fill in recipient and message'); return; }
    setLoading(true);
    try {
      const response = await makeAuthenticatedRequest('/api/whatsapp/send-message', { method: 'POST', body: JSON.stringify({ to: messageData.to, message: messageData.message, message_type: messageData.message_type }) });
      const result = await response.json();
      if (result.success) { alert('Message sent successfully!'); setMessageData(prev => ({ ...prev, to: '', message: '' })); fetchAutomationStatus(); } else { alert(`Send failed: ${result.error}`); }
    } catch (error) { alert(`Send failed: ${error.message}`); } finally { setLoading(false); }
  };

  const generateAIMessage = async () => {
    setLoading(true);
    try {
      const response = await makeAuthenticatedRequest('/api/automation/test-auto-post', { method: 'POST', body: JSON.stringify({ platform: 'whatsapp', domain: 'business', business_type: messageData.business_type, target_audience: 'customers', content_style: 'helpful' }) });
      const result = await response.json();
      if (result.success) { setMessageData(prev => ({ ...prev, message: result.content_preview || result.message || 'AI generated message' })); } else { alert(`AI generation failed: ${result.error}`); }
    } catch (error) { alert(`AI generation failed: ${error.message}`); } finally { setLoading(false); }
  };

  const sendBroadcast = async () => {
    const recipients = broadcastData.recipients.split(',').map(r => r.trim()).filter(r => r);
    if (recipients.length === 0 || !broadcastData.message) { alert('Please provide recipients and message'); return; }
    setLoading(true);
    try {
      const response = await makeAuthenticatedRequest('/api/whatsapp/broadcast', { method: 'POST', body: JSON.stringify({ recipient_list: recipients, message: broadcastData.message, media_url: broadcastData.media_url || '', media_type: broadcastData.media_type || '' }) });
      const result = await response.json();
      if (result.success) { const stats = result.broadcast_results; alert(`Broadcast sent! Success: ${stats.successful}, Failed: ${stats.failed}`); setBroadcastData({ recipients: '', message: '', media_url: '', media_type: '' }); fetchAutomationStatus(); } else { alert(`Broadcast failed: ${result.error}`); }
    } catch (error) { alert(`Broadcast failed: ${error.message}`); } finally { setLoading(false); }
  };

  const TabButton = ({ id, label, emoji, active, onClick }) => ( <button onClick={onClick} style={{ padding: '12px 24px', background: active ? '#25D366' : 'transparent', color: active ? 'white' : '#25D366', border: '2px solid #25D366', borderRadius: '12px', cursor: 'pointer', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '14px' }}><span>{emoji}</span>{label}</button>);

  const StatusCard = ({ title, value, color = '#25D366' }) => ( <div style={{ background: 'white', borderRadius: '12px', padding: '20px', textAlign: 'center', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)', border: `2px solid ${color}` }}><div style={{ fontSize: '24px', fontWeight: 'bold', color, marginBottom: '8px' }}>{value}</div><div style={{ fontSize: '14px', color: '#666' }}>{title}</div></div>);

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #25D366 0%, #128C7E 100%)', padding: '20px' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px', color: 'white' }}>
          <h1 style={{ fontSize: '48px', fontWeight: '700', marginBottom: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '16px' }}><span style={{ fontSize: '56px' }}>💬</span>WhatsApp Business Automation</h1>
          <p style={{ fontSize: '20px', opacity: 0.9, maxWidth: '800px', margin: '0 auto' }}>Automate your WhatsApp Business messaging with AI-powered responses, broadcasts, and customer engagement</p>
        </div>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginBottom: '40px', flexWrap: 'wrap' }}>
          <TabButton id="setup" label="Setup & Config" emoji="⚙️" active={activeTab === 'setup'} onClick={() => setActiveTab('setup')} />
          <TabButton id="dashboard" label="Dashboard" emoji="📊" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <TabButton id="send" label="Send Messages" emoji="📤" active={activeTab === 'send'} onClick={() => setActiveTab('send')} />
          <TabButton id="broadcast" label="Broadcast" emoji="📢" active={activeTab === 'broadcast'} onClick={() => setActiveTab('broadcast')} />
          <TabButton id="analytics" label="Analytics" emoji="📈" active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')} />
        </div>

        {activeTab === 'setup' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#25D366', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>WhatsApp Business Setup</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' }}>
              <div>
                <h3 style={{ color: '#128C7E', marginBottom: '20px' }}>API Configuration</h3>
                
                <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Business Name</label><input type="text" value={config.business_name} onChange={(e) => setConfig(prev => ({ ...prev, business_name: e.target.value }))} placeholder="VelocityAgent" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} /></div>

                <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Phone Number ID</label><input type="text" value={config.phone_number_id} onChange={(e) => setConfig(prev => ({ ...prev, phone_number_id: e.target.value }))} placeholder="842943155558927" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} /></div>

                <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Access Token</label><input type="password" value={config.access_token} onChange={(e) => setConfig(prev => ({ ...prev, access_token: e.target.value }))} placeholder="Permanent WhatsApp Access Token" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} /></div>
              </div>

              <div>
                <h3 style={{ color: '#128C7E', marginBottom: '20px' }}>Automation Settings</h3>
                
                <div style={{ marginBottom: '20px' }}><label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}><input type="checkbox" checked={config.auto_reply_enabled} onChange={(e) => setConfig(prev => ({ ...prev, auto_reply_enabled: e.target.checked }))} style={{ width: '20px', height: '20px' }} /><span style={{ fontWeight: '600', color: '#333' }}>Enable Auto-Reply</span></label></div>

                <div style={{ marginBottom: '20px' }}><label style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }}><input type="checkbox" checked={config.campaign_enabled} onChange={(e) => setConfig(prev => ({ ...prev, campaign_enabled: e.target.checked }))} style={{ width: '20px', height: '20px' }} /><span style={{ fontWeight: '600', color: '#333' }}>Enable Campaigns</span></label></div>

                <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Business Hours</label><div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}><input type="time" value={config.business_hours.start} onChange={(e) => setConfig(prev => ({ ...prev, business_hours: { ...prev.business_hours, start: e.target.value } }))} style={{ padding: '8px 12px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '14px' }} /><span style={{ color: '#666' }}>to</span><input type="time" value={config.business_hours.end} onChange={(e) => setConfig(prev => ({ ...prev, business_hours: { ...prev.business_hours, end: e.target.value } }))} style={{ padding: '8px 12px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '14px' }} /></div></div>

                <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Timezone</label><select value={config.timezone} onChange={(e) => setConfig(prev => ({ ...prev, timezone: e.target.value }))} style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }}><option value="UTC">UTC</option><option value="America/New_York">Eastern Time</option><option value="Asia/Kolkata">India Standard Time</option></select></div>
              </div>
            </div>

            <div style={{ textAlign: 'center', marginTop: '30px' }}><button onClick={setupWhatsAppAutomation} disabled={loading || !config.phone_number_id || !config.access_token} style={{ padding: '16px 32px', background: loading || !config.phone_number_id || !config.access_token ? '#ccc' : '#25D366', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: loading || !config.phone_number_id || !config.access_token ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '8px', margin: '0 auto' }}>{loading ? '⏳ Setting up...' : '🚀 Setup WhatsApp Automation'}</button></div>
          </div>
        )}

        {activeTab === 'dashboard' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#25D366', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>Automation Dashboard</h2>
            
            {status && (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  <StatusCard title="Total Messages" value={status.whatsapp_automation?.stats?.total_messages || 0} color="#25D366" />
                  <StatusCard title="Successful" value={status.whatsapp_automation?.stats?.successful_messages || 0} color="#00C851" />
                  <StatusCard title="Failed" value={status.whatsapp_automation?.stats?.failed_messages || 0} color="#ff4444" />
                  <StatusCard title="Connection" value={status.whatsapp_connected ? "Connected" : "Disconnected"} color={status.whatsapp_connected ? "#00C851" : "#ff4444"} />
                </div>

                <div style={{ background: '#f8f9fa', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}>
                  <h3 style={{ color: '#128C7E', marginBottom: '16px' }}>Configuration Status</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><span>{status.whatsapp_automation?.enabled ? '✅' : '❌'}</span><span style={{ fontWeight: '600', color: status.whatsapp_automation?.enabled ? '#00C851' : '#ff4444' }}>Automation {status.whatsapp_automation?.enabled ? 'Enabled' : 'Disabled'}</span></div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><span>{status.whatsapp_automation?.config?.auto_reply_enabled ? '✅' : '❌'}</span><span style={{ fontWeight: '600', color: status.whatsapp_automation?.config?.auto_reply_enabled ? '#00C851' : '#666' }}>Auto-Reply {status.whatsapp_automation?.config?.auto_reply_enabled ? 'On' : 'Off'}</span></div>
                  </div>
                </div>
              </>
            )}

            <div style={{ textAlign: 'center', marginTop: '20px' }}><button onClick={fetchAutomationStatus} style={{ padding: '12px 24px', background: '#25D366', color: 'white', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600' }}>🔄 Refresh Status</button></div>
          </div>
        )}

        {activeTab === 'send' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#25D366', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>Send WhatsApp Messages</h2>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '30px' }}>
              <div>
                <h3 style={{ color: '#128C7E', marginBottom: '20px' }}>Message Details</h3>
                
                <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Recipient Phone Number (with country code)</label><input type="text" value={messageData.to} onChange={(e) => setMessageData(prev => ({ ...prev, to: e.target.value }))} placeholder="919876543210" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} /></div>

                <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Message Content</label><textarea value={messageData.message} onChange={(e) => setMessageData(prev => ({ ...prev, message: e.target.value }))} placeholder="Enter your message here..." rows="6" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', resize: 'vertical', boxSizing: 'border-box' }} /><div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>Character count: {messageData.message.length}</div></div>

                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}><button onClick={sendMessage} disabled={loading || !messageData.to || !messageData.message} style={{ padding: '12px 24px', background: loading || !messageData.to || !messageData.message ? '#ccc' : '#25D366', color: 'white', border: 'none', borderRadius: '8px', cursor: loading || !messageData.to || !messageData.message ? 'not-allowed' : 'pointer', fontWeight: '600', flex: '1' }}>{loading ? '⏳ Sending...' : '📤 Send Message'}</button></div>
              </div>

              <div>
                <h3 style={{ color: '#128C7E', marginBottom: '20px' }}>AI Content Generation</h3>
                
                <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Business Type</label><select value={messageData.business_type} onChange={(e) => setMessageData(prev => ({ ...prev, business_type: e.target.value }))} style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }}><option value="general">General Business</option><option value="restaurant">Restaurant</option><option value="retail">Retail Store</option><option value="service">Service Provider</option><option value="technology">Technology</option></select></div>

                <div style={{ marginBottom: '20px' }}><button onClick={generateAIMessage} disabled={loading} style={{ width: '100%', padding: '12px 24px', background: loading ? '#ccc' : '#128C7E', color: 'white', border: 'none', borderRadius: '8px', cursor: loading ? 'not-allowed' : 'pointer', fontWeight: '600' }}>{loading ? '⏳ Generating...' : '🤖 Generate AI Message'}</button></div>

                <div style={{ background: '#f8f9fa', borderRadius: '8px', padding: '16px' }}>
                  <h4 style={{ color: '#128C7E', marginBottom: '12px' }}>Quick Templates</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <button onClick={() => setMessageData(prev => ({ ...prev, message: 'Hi! Thank you for your interest in our services. How can we help you today?' }))} style={{ padding: '8px 12px', background: 'white', border: '1px solid #ddd', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', textAlign: 'left' }}>Welcome Message</button>
                    <button onClick={() => setMessageData(prev => ({ ...prev, message: 'Thank you for your order! We will process it shortly and keep you updated.' }))} style={{ padding: '8px 12px', background: 'white', border: '1px solid #ddd', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', textAlign: 'left' }}>Order Confirmation</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'broadcast' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#25D366', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>Broadcast Messages</h2>
            
            <div style={{ marginBottom: '30px' }}>
              <div style={{ background: '#fff3cd', border: '1px solid #ffeeba', borderRadius: '8px', padding: '16px', marginBottom: '20px' }}><h4 style={{ color: '#856404', margin: '0 0 8px 0' }}>⚠️ Important Note</h4><p style={{ color: '#856404', margin: 0, fontSize: '14px' }}>WhatsApp broadcast messages can only be sent to users who have messaged your business first. Make sure your recipients have opted in to receive messages from you.</p></div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '30px' }}>
                <div>
                  <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Recipients (comma-separated phone numbers)</label><textarea value={broadcastData.recipients} onChange={(e) => setBroadcastData(prev => ({ ...prev, recipients: e.target.value }))} placeholder="919876543210, 919876543211, 919876543212" rows="4" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', resize: 'vertical', boxSizing: 'border-box' }} /><div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>Recipients count: {broadcastData.recipients ? broadcastData.recipients.split(',').filter(r => r.trim()).length : 0}</div></div>

                  <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Broadcast Message</label><textarea value={broadcastData.message} onChange={(e) => setBroadcastData(prev => ({ ...prev, message: e.target.value }))} placeholder="Enter your broadcast message here..." rows="6" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', resize: 'vertical', boxSizing: 'border-box' }} /><div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>Character count: {broadcastData.message.length}</div></div>
                </div>

                <div>
                  <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Media URL (Optional)</label><input type="url" value={broadcastData.media_url} onChange={(e) => setBroadcastData(prev => ({ ...prev, media_url: e.target.value }))} placeholder="https://example.com/image.jpg" style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box' }} /></div>

                  <div style={{ marginBottom: '20px' }}><label style={{ display: 'block', marginBottom: '8px', fontWeight: '600', color: '#333' }}>Media Type</label><select value={broadcastData.media_type} onChange={(e) => setBroadcastData(prev => ({ ...prev, media_type: e.target.value }))} disabled={!broadcastData.media_url} style={{ width: '100%', padding: '12px 16px', border: '2px solid #ddd', borderRadius: '8px', fontSize: '16px', boxSizing: 'border-box', opacity: !broadcastData.media_url ? 0.5 : 1 }}><option value="">Select media type</option><option value="image">Image</option><option value="video">Video</option><option value="document">Document</option></select></div>

                  <div style={{ background: '#f8f9fa', borderRadius: '8px', padding: '16px' }}><h4 style={{ color: '#128C7E', marginBottom: '12px' }}>Broadcast Templates</h4><div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}><button onClick={() => setBroadcastData(prev => ({ ...prev, message: 'Exciting news! We have a special promotion running this week. Don\'t miss out!' }))} style={{ padding: '8px 12px', background: 'white', border: '1px solid #ddd', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', textAlign: 'left' }}>Promotion Announcement</button><button onClick={() => setBroadcastData(prev => ({ ...prev, message: 'Thank you for being our valued customer! We have some exciting updates to share with you.' }))} style={{ padding: '8px 12px', background: 'white', border: '1px solid #ddd', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', textAlign: 'left' }}>Customer Appreciation</button></div></div>
                </div>
              </div>

              <div style={{ textAlign: 'center', marginTop: '30px' }}><button onClick={sendBroadcast} disabled={loading || !broadcastData.recipients || !broadcastData.message} style={{ padding: '16px 32px', background: loading || !broadcastData.recipients || !broadcastData.message ? '#ccc' : '#25D366', color: 'white', border: 'none', borderRadius: '12px', fontSize: '16px', fontWeight: '700', cursor: loading || !broadcastData.recipients || !broadcastData.message ? 'not-allowed' : 'pointer', display: 'flex', alignItems: 'center', gap: '8px', margin: '0 auto' }}>{loading ? '⏳ Sending Broadcast...' : '📢 Send Broadcast'}</button></div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div style={{ background: 'rgba(255, 255, 255, 0.95)', borderRadius: '20px', padding: '40px', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)' }}>
            <h2 style={{ color: '#25D366', marginBottom: '30px', fontSize: '28px', fontWeight: '700' }}>Analytics & Performance</h2>
            
            {status && (
              <div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '30px' }}>
                  <div style={{ background: 'linear-gradient(135deg, #25D366, #128C7E)', borderRadius: '12px', padding: '20px', textAlign: 'center', color: 'white' }}><div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>{status.whatsapp_automation?.stats?.total_messages || 0}</div><div style={{ fontSize: '14px', opacity: 0.9 }}>Total Messages Sent</div></div>

                  <div style={{ background: 'linear-gradient(135deg, #00C851, #00A047)', borderRadius: '12px', padding: '20px', textAlign: 'center', color: 'white' }}><div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>{status.whatsapp_automation?.stats?.successful_messages || 0}</div><div style={{ fontSize: '14px', opacity: 0.9 }}>Successful Deliveries</div></div>

                  <div style={{ background: 'linear-gradient(135deg, #ff4444, #cc0000)', borderRadius: '12px', padding: '20px', textAlign: 'center', color: 'white' }}><div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>{status.whatsapp_automation?.stats?.failed_messages || 0}</div><div style={{ fontSize: '14px', opacity: 0.9 }}>Failed Messages</div></div>

                  <div style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)', borderRadius: '12px', padding: '20px', textAlign: 'center', color: 'white' }}><div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>{status.whatsapp_automation?.stats?.total_messages > 0 ? Math.round((status.whatsapp_automation.stats.successful_messages / status.whatsapp_automation.stats.total_messages) * 100) : 0}%</div><div style={{ fontSize: '14px', opacity: 0.9 }}>Success Rate</div></div>
                </div>

                <div style={{ background: '#f8f9fa', borderRadius: '12px', padding: '20px', marginBottom: '20px' }}><h3 style={{ color: '#128C7E', marginBottom: '16px' }}>Activity Summary</h3><div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px' }}><div><strong>Business Name:</strong> {status.whatsapp_automation?.config?.business_name || 'Not configured'}</div><div><strong>Auto-Reply Status:</strong> <span style={{ color: status.whatsapp_automation?.config?.auto_reply_enabled ? '#00C851' : '#666', marginLeft: '8px', fontWeight: '600' }}>{status.whatsapp_automation?.config?.auto_reply_enabled ? 'Active' : 'Inactive'}</span></div><div><strong>Campaign Status:</strong> <span style={{ color: status.whatsapp_automation?.config?.campaign_enabled ? '#00C851' : '#666', marginLeft: '8px', fontWeight: '600' }}>{status.whatsapp_automation?.config?.campaign_enabled ? 'Active' : 'Inactive'}</span></div><div><strong>Last Activity:</strong> {status.whatsapp_automation?.stats?.last_activity ? new Date(status.whatsapp_automation.stats.last_activity).toLocaleString() : 'No recent activity'}</div></div></div>

                <div style={{ background: '#e8f5e8', borderRadius: '12px', padding: '20px' }}><h3 style={{ color: '#128C7E', marginBottom: '16px' }}>Performance Tips</h3><ul style={{ margin: 0, paddingLeft: '20px', color: '#333' }}><li style={{ marginBottom: '8px' }}>Personalize your messages to improve engagement rates</li><li style={{ marginBottom: '8px' }}>Send messages during business hours for better response rates</li><li style={{ marginBottom: '8px' }}>Use templates for consistent messaging</li><li style={{ marginBottom: '8px' }}>Monitor failed messages and update contact information</li><li>Keep messages concise and include clear calls-to-action</li></ul></div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WhatsAppAutomation;