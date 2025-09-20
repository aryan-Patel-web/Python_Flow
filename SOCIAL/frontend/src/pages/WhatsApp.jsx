import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../quickpage/AuthContext';

const WhatsAppAutomation = () => {
  const { user, makeAuthenticatedRequest } = useAuth();
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [notifications, setNotifications] = useState([]);
  
  // Multi-user credential system with testing defaults
  const [whatsappCredentials, setWhatsappCredentials] = useState({
    phone_number_id: '842943155558927', // Your testing default
    access_token: 'EAALNGPo4t80BPVCNDAKG9VCphy4OmQxVkZCsZCPAvYZCrHgRfSCmZAcLnRNiOM8MD97IjQNl0p7z2A5WDt3IxjmDRzdJOr1AZCwOr7kVZAZAe81MGsVMbRQks2cSv2jq49LlSa4HFlSLZAbhM8uYezRUNukGcm9oZALUj1u0ACxzZCZCZB9voYbCApSaoZCjA4egSjv45YwZDZD', // Your testing default
    business_name: 'VelocityAgent', // Your testing default
    webhook_verify_token: 'whatsapp_webhook_verify_2024_secure_velocity'
  });

  const [isConnected, setIsConnected] = useState(false);
  const [automationConfig, setAutomationConfig] = useState({
    auto_reply_enabled: true,
    campaign_enabled: true,
    business_hours: { start: '09:00', end: '18:00' },
    timezone: 'Asia/Calcutta'
  });

  const [messageData, setMessageData] = useState({
    to: '',
    message: '',
    message_type: 'text',
    business_type: 'general'
  });

  const [broadcastData, setBroadcastData] = useState({
    recipients: '',
    message: '',
    media_url: '',
    media_type: ''
  });

  const showNotification = useCallback((message, type = 'success') => {
    const notification = { id: Date.now(), message, type };
    setNotifications(prev => [...prev, notification]);
    setTimeout(() => setNotifications(prev => prev.filter(n => n.id !== notification.id)), 5000);
  }, []);

  useEffect(() => {
    if (user?.email) {
      fetchAutomationStatus();
      loadUserCredentials();
    }
  }, [user]);

  const loadUserCredentials = () => {
    try {
      const savedCredentials = localStorage.getItem(`whatsapp_credentials_${user.email}`);
      if (savedCredentials) {
        const parsed = JSON.parse(savedCredentials);
        setWhatsappCredentials(prev => ({ ...prev, ...parsed }));
        setIsConnected(!!parsed.access_token);
      }
    } catch (error) {
      console.error('Error loading user credentials:', error);
    }
  };

  const saveUserCredentials = (credentials) => {
    try {
      // Save credentials per user email
      localStorage.setItem(`whatsapp_credentials_${user.email}`, JSON.stringify(credentials));
    } catch (error) {
      console.error('Error saving user credentials:', error);
    }
  };

  const fetchAutomationStatus = async () => {
    try {
      const response = await makeAuthenticatedRequest('/api/automation/status');
      const data = await response.json();
      if (data.success) {
        setStatus(data);
        if (data.whatsapp_connected) {
          setIsConnected(true);
        }
        if (data.whatsapp_automation?.config) {
          setAutomationConfig(prev => ({ ...prev, ...data.whatsapp_automation.config }));
        }
      }
    } catch (error) {
      console.error('Status fetch failed:', error);
    }
  };

  const setupWhatsAppAutomation = async () => {
    if (!whatsappCredentials.phone_number_id || !whatsappCredentials.access_token) {
      showNotification('Please enter your WhatsApp credentials', 'error');
      return;
    }

    setLoading(true);
    try {
      showNotification('Setting up WhatsApp automation...', 'info');
      
      const requestBody = {
        phone_number_id: whatsappCredentials.phone_number_id,
        access_token: whatsappCredentials.access_token,
        business_name: whatsappCredentials.business_name || `${user.name}'s Business`,
        auto_reply_enabled: automationConfig.auto_reply_enabled,
        campaign_enabled: automationConfig.campaign_enabled,
        business_hours: automationConfig.business_hours,
        timezone: automationConfig.timezone
      };

      const response = await makeAuthenticatedRequest('/api/whatsapp/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(requestBody)
      });
      
      const result = await response.json();
      
      if (result.success) {
        setIsConnected(true);
        showNotification('WhatsApp automation setup successful!', 'success');
        
        // Save user credentials for future use
        saveUserCredentials({
          phone_number_id: whatsappCredentials.phone_number_id,
          business_name: whatsappCredentials.business_name,
          // Don't save access token in localStorage for security
        });
        
        fetchAutomationStatus();
        setActiveTab('dashboard');
      } else {
        showNotification(`Setup failed: ${result.error}`, 'error');
      }
    } catch (error) {
      showNotification(`Setup failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!messageData.to || !messageData.message) {
      showNotification('Please fill in recipient and message', 'error');
      return;
    }

    if (!isConnected) {
      showNotification('Please setup WhatsApp automation first', 'error');
      return;
    }

    setLoading(true);
    try {
      showNotification('Sending message...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/whatsapp/send-message', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          to: messageData.to,
          message: messageData.message,
          message_type: messageData.message_type
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        showNotification('Message sent successfully!', 'success');
        setMessageData(prev => ({ ...prev, to: '', message: '' }));
        fetchAutomationStatus();
      } else {
        showNotification(`Send failed: ${result.error}`, 'error');
      }
    } catch (error) {
      showNotification(`Send failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const generateAIMessage = async () => {
    setLoading(true);
    try {
      showNotification('Generating AI content...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/automation/test-auto-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: 'whatsapp',
          domain: 'business',
          business_type: messageData.business_type,
          target_audience: 'customers',
          content_style: 'helpful'
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        setMessageData(prev => ({
          ...prev,
          message: result.content_preview || result.message || 'AI generated message'
        }));
        showNotification('AI content generated successfully!', 'success');
      } else {
        showNotification(`AI generation failed: ${result.error}`, 'error');
      }
    } catch (error) {
      showNotification(`AI generation failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const sendBroadcast = async () => {
    const recipients = broadcastData.recipients.split(',').map(r => r.trim()).filter(r => r);
    if (recipients.length === 0 || !broadcastData.message) {
      showNotification('Please provide recipients and message', 'error');
      return;
    }

    if (!isConnected) {
      showNotification('Please setup WhatsApp automation first', 'error');
      return;
    }

    setLoading(true);
    try {
      showNotification('Sending broadcast...', 'info');
      
      const response = await makeAuthenticatedRequest('/api/whatsapp/broadcast', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipient_list: recipients,
          message: broadcastData.message,
          media_url: broadcastData.media_url || '',
          media_type: broadcastData.media_type || ''
        })
      });
      
      const result = await response.json();
      
      if (result.success) {
        const stats = result.broadcast_results || { successful: recipients.length, failed: 0 };
        showNotification(`Broadcast sent! Success: ${stats.successful}, Failed: ${stats.failed}`, 'success');
        setBroadcastData({ recipients: '', message: '', media_url: '', media_type: '' });
        fetchAutomationStatus();
      } else {
        showNotification(`Broadcast failed: ${result.error}`, 'error');
      }
    } catch (error) {
      showNotification(`Broadcast failed: ${error.message}`, 'error');
    } finally {
      setLoading(false);
    }
  };

  const disconnectWhatsApp = async () => {
    try {
      setLoading(true);
      const response = await makeAuthenticatedRequest('/api/whatsapp/disconnect', {
        method: 'POST'
      });
      
      if (response.ok) {
        setIsConnected(false);
        setWhatsappCredentials({
          phone_number_id: '',
          access_token: '',
          business_name: '',
          webhook_verify_token: ''
        });
        localStorage.removeItem(`whatsapp_credentials_${user.email}`);
        showNotification('WhatsApp disconnected successfully', 'success');
      }
    } catch (error) {
      showNotification('Disconnect failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  const TabButton = ({ id, label, emoji, active, onClick }) => (
    <button
      onClick={onClick}
      style={{
        padding: '12px 24px',
        background: active ? '#25D366' : 'transparent',
        color: active ? 'white' : '#25D366',
        border: '2px solid #25D366',
        borderRadius: '12px',
        cursor: 'pointer',
        fontWeight: '600',
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '14px'
      }}
    >
      <span>{emoji}</span>{label}
    </button>
  );

  const StatusCard = ({ title, value, color = '#25D366' }) => (
    <div style={{
      background: 'white',
      borderRadius: '12px',
      padding: '20px',
      textAlign: 'center',
      boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
      border: `2px solid ${color}`
    }}>
      <div style={{ fontSize: '24px', fontWeight: 'bold', color, marginBottom: '8px' }}>
        {value}
      </div>
      <div style={{ fontSize: '14px', color: '#666' }}>
        {title}
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #25D366 0%, #128C7E 100%)', padding: '20px' }}>
      {/* Notifications */}
      <div style={{ position: 'fixed', top: '20px', right: '20px', zIndex: 10000, display: 'flex', flexDirection: 'column', gap: '10px', maxWidth: '400px' }}>
        {notifications.map(notification => (
          <div key={notification.id} style={{
            padding: '16px 20px',
            borderRadius: '12px',
            backdropFilter: 'blur(15px)',
            color: 'white',
            fontWeight: '600',
            boxShadow: '0 8px 25px rgba(0, 0, 0, 0.3)',
            background: notification.type === 'success' ? 'rgba(34, 197, 94, 0.9)' :
                       notification.type === 'error' ? 'rgba(239, 68, 68, 0.9)' : 'rgba(59, 130, 246, 0.9)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: '12px',
            fontSize: '14px',
            border: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <span>{notification.message}</span>
            <button 
              onClick={() => setNotifications(prev => prev.filter(n => n.id !== notification.id))}
              style={{ background: 'none', border: 'none', color: 'white', fontSize: '18px', cursor: 'pointer', padding: '4px', opacity: 0.8 }}
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px', color: 'white' }}>
          <h1 style={{
            fontSize: '48px',
            fontWeight: '700',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '16px'
          }}>
            <span style={{ fontSize: '56px' }}>💬</span>
            WhatsApp Business Automation
          </h1>
          <p style={{
            fontSize: '20px',
            opacity: 0.9,
            maxWidth: '800px',
            margin: '0 auto'
          }}>
            Multi-user WhatsApp automation for {user?.name} - AI-powered messaging, broadcasts, and customer engagement
          </p>
        </div>

        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: '16px',
          marginBottom: '40px',
          flexWrap: 'wrap'
        }}>
          <TabButton id="setup" label="Setup & Config" emoji="⚙️" active={activeTab === 'setup'} onClick={() => setActiveTab('setup')} />
          <TabButton id="dashboard" label="Dashboard" emoji="📊" active={activeTab === 'dashboard'} onClick={() => setActiveTab('dashboard')} />
          <TabButton id="send" label="Send Messages" emoji="📤" active={activeTab === 'send'} onClick={() => setActiveTab('send')} />
          <TabButton id="broadcast" label="Broadcast" emoji="📢" active={activeTab === 'broadcast'} onClick={() => setActiveTab('broadcast')} />
          <TabButton id="analytics" label="Analytics" emoji="📈" active={activeTab === 'analytics'} onClick={() => setActiveTab('analytics')} />
        </div>

        {activeTab === 'setup' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#25D366',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              WhatsApp Business Setup for {user?.name}
            </h2>

            {!isConnected && (
              <div style={{
                background: '#fff3cd',
                border: '1px solid #ffeeba',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '30px'
              }}>
                <h4 style={{ color: '#856404', margin: '0 0 8px 0' }}>
                  📝 For Testing - Your Credentials Are Pre-filled
                </h4>
                <p style={{ color: '#856404', margin: 0, fontSize: '14px' }}>
                  Default testing credentials are loaded. For production, replace with your own WhatsApp Business API credentials.
                  Each user can have their own separate WhatsApp automation.
                </p>
              </div>
            )}
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '30px'
            }}>
              <div>
                <h3 style={{ color: '#128C7E', marginBottom: '20px' }}>
                  Your WhatsApp API Configuration
                </h3>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333'
                  }}>
                    Business Name
                  </label>
                  <input
                    type="text"
                    value={whatsappCredentials.business_name}
                    onChange={(e) => setWhatsappCredentials(prev => ({
                      ...prev,
                      business_name: e.target.value
                    }))}
                    placeholder={`${user?.name}'s Business`}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '16px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333'
                  }}>
                    Phone Number ID
                  </label>
                  <input
                    type="text"
                    value={whatsappCredentials.phone_number_id}
                    onChange={(e) => setWhatsappCredentials(prev => ({
                      ...prev,
                      phone_number_id: e.target.value
                    }))}
                    placeholder="Get from Meta Developer Console"
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '16px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333'
                  }}>
                    Access Token
                  </label>
                  <input
                    type="password"
                    value={whatsappCredentials.access_token}
                    onChange={(e) => setWhatsappCredentials(prev => ({
                      ...prev,
                      access_token: e.target.value
                    }))}
                    placeholder="Your permanent WhatsApp Access Token"
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '16px',
                      boxSizing: 'border-box'
                    }}
                  />
                </div>
              </div>

              <div>
                <h3 style={{ color: '#128C7E', marginBottom: '20px' }}>
                  Automation Settings
                </h3>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    cursor: 'pointer'
                  }}>
                    <input
                      type="checkbox"
                      checked={automationConfig.auto_reply_enabled}
                      onChange={(e) => setAutomationConfig(prev => ({
                        ...prev,
                        auto_reply_enabled: e.target.checked
                      }))}
                      style={{ width: '20px', height: '20px' }}
                    />
                    <span style={{ fontWeight: '600', color: '#333' }}>
                      Enable Auto-Reply
                    </span>
                  </label>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    cursor: 'pointer'
                  }}>
                    <input
                      type="checkbox"
                      checked={automationConfig.campaign_enabled}
                      onChange={(e) => setAutomationConfig(prev => ({
                        ...prev,
                        campaign_enabled: e.target.checked
                      }))}
                      style={{ width: '20px', height: '20px' }}
                    />
                    <span style={{ fontWeight: '600', color: '#333' }}>
                      Enable Campaigns
                    </span>
                  </label>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333'
                  }}>
                    Business Hours
                  </label>
                  <div style={{
                    display: 'flex',
                    gap: '12px',
                    alignItems: 'center'
                  }}>
                    <input
                      type="time"
                      value={automationConfig.business_hours.start}
                      onChange={(e) => setAutomationConfig(prev => ({
                        ...prev,
                        business_hours: {
                          ...prev.business_hours,
                          start: e.target.value
                        }
                      }))}
                      style={{
                        padding: '8px 12px',
                        border: '2px solid #ddd',
                        borderRadius: '8px',
                        fontSize: '14px'
                      }}
                    />
                    <span style={{ color: '#666' }}>to</span>
                    <input
                      type="time"
                      value={automationConfig.business_hours.end}
                      onChange={(e) => setAutomationConfig(prev => ({
                        ...prev,
                        business_hours: {
                          ...prev.business_hours,
                          end: e.target.value
                        }
                      }))}
                      style={{
                        padding: '8px 12px',
                        border: '2px solid #ddd',
                        borderRadius: '8px',
                        fontSize: '14px'
                      }}
                    />
                  </div>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333'
                  }}>
                    Timezone
                  </label>
                  <select
                    value={automationConfig.timezone}
                    onChange={(e) => setAutomationConfig(prev => ({
                      ...prev,
                      timezone: e.target.value
                    }))}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '16px',
                      boxSizing: 'border-box'
                    }}
                  >
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="Asia/Kolkata">India Standard Time</option>
                    <option value="Europe/London">London Time</option>
                    <option value="Asia/Singapore">Singapore Time</option>
                  </select>
                </div>
              </div>
            </div>

            <div style={{ textAlign: 'center', marginTop: '30px', display: 'flex', gap: '16px', justifyContent: 'center' }}>
              {!isConnected ? (
                <button
                  onClick={setupWhatsAppAutomation}
                  disabled={loading || !whatsappCredentials.phone_number_id || !whatsappCredentials.access_token}
                  style={{
                    padding: '16px 32px',
                    background: loading || !whatsappCredentials.phone_number_id || !whatsappCredentials.access_token ? '#ccc' : '#25D366',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '700',
                    cursor: loading || !whatsappCredentials.phone_number_id || !whatsappCredentials.access_token ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                >
                  {loading ? '⏳ Setting up...' : '🚀 Setup WhatsApp Automation'}
                </button>
              ) : (
                <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                  <div style={{
                    padding: '16px 24px',
                    background: '#00C851',
                    color: 'white',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '600'
                  }}>
                    ✅ WhatsApp Connected Successfully!
                  </div>
                  <button
                    onClick={disconnectWhatsApp}
                    disabled={loading}
                    style={{
                      padding: '12px 20px',
                      background: '#ff4444',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      fontSize: '14px',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                  >
                    Disconnect
                  </button>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Rest of the tabs remain the same but with isConnected checks */}
        {activeTab === 'dashboard' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#25D366',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Automation Dashboard - {user?.name}
            </h2>
            
            {!isConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px'
              }}>
                <p style={{ color: '#721c24', margin: 0, fontSize: '16px' }}>
                  ❌ WhatsApp not connected. Please go to Setup tab to connect your WhatsApp Business account.
                </p>
              </div>
            )}

            {status && isConnected && (
              <>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                  gap: '20px',
                  marginBottom: '30px'
                }}>
                  <StatusCard 
                    title="Total Messages" 
                    value={status.whatsapp_automation?.stats?.total_messages || 0} 
                    color="#25D366" 
                  />
                  <StatusCard 
                    title="Successful" 
                    value={status.whatsapp_automation?.stats?.successful_messages || 0} 
                    color="#00C851" 
                  />
                  <StatusCard 
                    title="Failed" 
                    value={status.whatsapp_automation?.stats?.failed_messages || 0} 
                    color="#ff4444" 
                  />
                  <StatusCard 
                    title="Connection" 
                    value={status.whatsapp_connected ? "Connected" : "Disconnected"} 
                    color={status.whatsapp_connected ? "#00C851" : "#ff4444"} 
                  />
                </div>

                <div style={{
                  background: '#f8f9fa',
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '20px'
                }}>
                  <h3 style={{ color: '#128C7E', marginBottom: '16px' }}>
                    Configuration Status
                  </h3>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                    gap: '16px'
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span>{status.whatsapp_automation?.enabled ? '✅' : '❌'}</span>
                      <span style={{
                        fontWeight: '600',
                        color: status.whatsapp_automation?.enabled ? '#00C851' : '#ff4444'
                      }}>
                        Automation {status.whatsapp_automation?.enabled ? 'Enabled' : 'Disabled'}
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span>{status.whatsapp_automation?.config?.auto_reply_enabled ? '✅' : '❌'}</span>
                      <span style={{
                        fontWeight: '600',
                        color: status.whatsapp_automation?.config?.auto_reply_enabled ? '#00C851' : '#666'
                      }}>
                        Auto-Reply {status.whatsapp_automation?.config?.auto_reply_enabled ? 'On' : 'Off'}
                      </span>
                    </div>
                  </div>
                </div>
              </>
            )}

            <div style={{ textAlign: 'center', marginTop: '20px' }}>
              <button
                onClick={fetchAutomationStatus}
                style={{
                  padding: '12px 24px',
                  background: '#25D366',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                🔄 Refresh Status
              </button>
            </div>
          </div>
        )}

        {activeTab === 'send' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#25D366',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Send WhatsApp Messages
            </h2>

            {!isConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px'
              }}>
                <p style={{ color: '#721c24', margin: 0, fontSize: '16px' }}>
                  ❌ WhatsApp not connected. Please setup WhatsApp automation first.
                </p>
              </div>
            )}
            
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: '30px'
            }}>
              <div>
                <h3 style={{ color: '#128C7E', marginBottom: '20px' }}>
                  Message Details
                </h3>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333'
                  }}>
                    Recipient Phone Number (with country code)
                  </label>
                  <input
                    type="text"
                    value={messageData.to}
                    onChange={(e) => setMessageData(prev => ({
                      ...prev,
                      to: e.target.value
                    }))}
                    placeholder="919876543210"
                    disabled={!isConnected}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '16px',
                      boxSizing: 'border-box',
                      opacity: !isConnected ? 0.6 : 1
                    }}
                  />
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333'
                  }}>
                    Message Content
                  </label>
                  <textarea
                    value={messageData.message}
                    onChange={(e) => setMessageData(prev => ({
                      ...prev,
                      message: e.target.value
                    }))}
                    placeholder="Enter your message here..."
                    rows="6"
                    disabled={!isConnected}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '16px',
                      resize: 'vertical',
                      boxSizing: 'border-box',
                      opacity: !isConnected ? 0.6 : 1
                    }}
                  />
                  <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                    Character count: {messageData.message.length}
                  </div>
                </div>

                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  <button
                    onClick={sendMessage}
                    disabled={loading || !messageData.to || !messageData.message || !isConnected}
                    style={{
                      padding: '12px 24px',
                      background: loading || !messageData.to || !messageData.message || !isConnected ? '#ccc' : '#25D366',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: loading || !messageData.to || !messageData.message || !isConnected ? 'not-allowed' : 'pointer',
                      fontWeight: '600',
                      flex: '1'
                    }}
                  >
                    {loading ? '⏳ Sending...' : '📤 Send Message'}
                  </button>
                </div>
              </div>

              <div>
                <h3 style={{ color: '#128C7E', marginBottom: '20px' }}>
                  AI Content Generation
                </h3>
                
                <div style={{ marginBottom: '20px' }}>
                  <label style={{
                    display: 'block',
                    marginBottom: '8px',
                    fontWeight: '600',
                    color: '#333'
                  }}>
                    Business Type
                  </label>
                  <select
                    value={messageData.business_type}
                    onChange={(e) => setMessageData(prev => ({
                      ...prev,
                      business_type: e.target.value
                    }))}
                    disabled={!isConnected}
                    style={{
                      width: '100%',
                      padding: '12px 16px',
                      border: '2px solid #ddd',
                      borderRadius: '8px',
                      fontSize: '16px',
                      boxSizing: 'border-box',
                      opacity: !isConnected ? 0.6 : 1
                    }}
                  >
                    <option value="general">General Business</option>
                    <option value="restaurant">Restaurant</option>
                    <option value="retail">Retail Store</option>
                    <option value="service">Service Provider</option>
                    <option value="technology">Technology</option>
                    <option value="education">Education</option>
                    <option value="healthcare">Healthcare</option>
                  </select>
                </div>

                <div style={{ marginBottom: '20px' }}>
                  <button
                    onClick={generateAIMessage}
                    disabled={loading || !isConnected}
                    style={{
                      width: '100%',
                      padding: '12px 24px',
                      background: loading || !isConnected ? '#ccc' : '#128C7E',
                      color: 'white',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: loading || !isConnected ? 'not-allowed' : 'pointer',
                      fontWeight: '600'
                    }}
                  >
                    {loading ? '⏳ Generating...' : '🤖 Generate AI Message'}
                  </button>
                </div>

                <div style={{
                  background: '#f8f9fa',
                  borderRadius: '8px',
                  padding: '16px'
                }}>
                  <h4 style={{ color: '#128C7E', marginBottom: '12px' }}>
                    Quick Templates
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <button
                      onClick={() => setMessageData(prev => ({
                        ...prev,
                        message: 'Hi! Thank you for your interest in our services. How can we help you today?'
                      }))}
                      disabled={!isConnected}
                      style={{
                        padding: '8px 12px',
                        background: 'white',
                        border: '1px solid #ddd',
                        borderRadius: '6px',
                        cursor: !isConnected ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        textAlign: 'left',
                        opacity: !isConnected ? 0.6 : 1
                      }}
                    >
                      Welcome Message
                    </button>
                    <button
                      onClick={() => setMessageData(prev => ({
                        ...prev,
                        message: 'Thank you for your order! We will process it shortly and keep you updated.'
                      }))}
                      disabled={!isConnected}
                      style={{
                        padding: '8px 12px',
                        background: 'white',
                        border: '1px solid #ddd',
                        borderRadius: '6px',
                        cursor: !isConnected ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        textAlign: 'left',
                        opacity: !isConnected ? 0.6 : 1
                      }}
                    >
                      Order Confirmation
                    </button>
                    <button
                      onClick={() => setMessageData(prev => ({
                        ...prev,
                        message: `Hello! This is ${user?.name} from ${whatsappCredentials.business_name}. We hope you're having a great day!`
                      }))}
                      disabled={!isConnected}
                      style={{
                        padding: '8px 12px',
                        background: 'white',
                        border: '1px solid #ddd',
                        borderRadius: '6px',
                        cursor: !isConnected ? 'not-allowed' : 'pointer',
                        fontSize: '14px',
                        textAlign: 'left',
                        opacity: !isConnected ? 0.6 : 1
                      }}
                    >
                      Personal Greeting
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'broadcast' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#25D366',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Broadcast Messages
            </h2>

            {!isConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px'
              }}>
                <p style={{ color: '#721c24', margin: 0, fontSize: '16px' }}>
                  ❌ WhatsApp not connected. Please setup WhatsApp automation first.
                </p>
              </div>
            )}
            
            <div style={{ marginBottom: '30px' }}>
              <div style={{
                background: '#fff3cd',
                border: '1px solid #ffeeba',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px'
              }}>
                <h4 style={{ color: '#856404', margin: '0 0 8px 0' }}>
                  ⚠️ Important Note
                </h4>
                <p style={{ color: '#856404', margin: 0, fontSize: '14px' }}>
                  WhatsApp broadcast messages can only be sent to users who have messaged your business first. 
                  Make sure your recipients have opted in to receive messages from you.
                </p>
              </div>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
                gap: '30px'
              }}>
                <div>
                  <div style={{ marginBottom: '20px' }}>
                    <label style={{
                      display: 'block',
                      marginBottom: '8px',
                      fontWeight: '600',
                      color: '#333'
                    }}>
                      Recipients (comma-separated phone numbers)
                    </label>
                    <textarea
                      value={broadcastData.recipients}
                      onChange={(e) => setBroadcastData(prev => ({
                        ...prev,
                        recipients: e.target.value
                      }))}
                      placeholder="919876543210, 919876543211, 919876543212"
                      rows="4"
                      disabled={!isConnected}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #ddd',
                        borderRadius: '8px',
                        fontSize: '16px',
                        resize: 'vertical',
                        boxSizing: 'border-box',
                        opacity: !isConnected ? 0.6 : 1
                      }}
                    />
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                      Recipients count: {broadcastData.recipients ? broadcastData.recipients.split(',').filter(r => r.trim()).length : 0}
                    </div>
                  </div>

                  <div style={{ marginBottom: '20px' }}>
                    <label style={{
                      display: 'block',
                      marginBottom: '8px',
                      fontWeight: '600',
                      color: '#333'
                    }}>
                      Broadcast Message
                    </label>
                    <textarea
                      value={broadcastData.message}
                      onChange={(e) => setBroadcastData(prev => ({
                        ...prev,
                        message: e.target.value
                      }))}
                      placeholder="Enter your broadcast message here..."
                      rows="6"
                      disabled={!isConnected}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #ddd',
                        borderRadius: '8px',
                        fontSize: '16px',
                        resize: 'vertical',
                        boxSizing: 'border-box',
                        opacity: !isConnected ? 0.6 : 1
                      }}
                    />
                    <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
                      Character count: {broadcastData.message.length}
                    </div>
                  </div>
                </div>

                <div>
                  <div style={{ marginBottom: '20px' }}>
                    <label style={{
                      display: 'block',
                      marginBottom: '8px',
                      fontWeight: '600',
                      color: '#333'
                    }}>
                      Media URL (Optional)
                    </label>
                    <input
                      type="url"
                      value={broadcastData.media_url}
                      onChange={(e) => setBroadcastData(prev => ({
                        ...prev,
                        media_url: e.target.value
                      }))}
                      placeholder="https://example.com/image.jpg"
                      disabled={!isConnected}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #ddd',
                        borderRadius: '8px',
                        fontSize: '16px',
                        boxSizing: 'border-box',
                        opacity: !isConnected ? 0.6 : 1
                      }}
                    />
                  </div>

                  <div style={{ marginBottom: '20px' }}>
                    <label style={{
                      display: 'block',
                      marginBottom: '8px',
                      fontWeight: '600',
                      color: '#333'
                    }}>
                      Media Type
                    </label>
                    <select
                      value={broadcastData.media_type}
                      onChange={(e) => setBroadcastData(prev => ({
                        ...prev,
                        media_type: e.target.value
                      }))}
                      disabled={!broadcastData.media_url || !isConnected}
                      style={{
                        width: '100%',
                        padding: '12px 16px',
                        border: '2px solid #ddd',
                        borderRadius: '8px',
                        fontSize: '16px',
                        boxSizing: 'border-box',
                        opacity: (!broadcastData.media_url || !isConnected) ? 0.5 : 1
                      }}
                    >
                      <option value="">Select media type</option>
                      <option value="image">Image</option>
                      <option value="video">Video</option>
                      <option value="document">Document</option>
                    </select>
                  </div>

                  <div style={{
                    background: '#f8f9fa',
                    borderRadius: '8px',
                    padding: '16px'
                  }}>
                    <h4 style={{ color: '#128C7E', marginBottom: '12px' }}>
                      Broadcast Templates
                    </h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      <button
                        onClick={() => setBroadcastData(prev => ({
                          ...prev,
                          message: `Exciting news from ${whatsappCredentials.business_name}! We have a special promotion running this week. Don't miss out!`
                        }))}
                        disabled={!isConnected}
                        style={{
                          padding: '8px 12px',
                          background: 'white',
                          border: '1px solid #ddd',
                          borderRadius: '6px',
                          cursor: !isConnected ? 'not-allowed' : 'pointer',
                          fontSize: '14px',
                          textAlign: 'left',
                          opacity: !isConnected ? 0.6 : 1
                        }}
                      >
                        Promotion Announcement
                      </button>
                      <button
                        onClick={() => setBroadcastData(prev => ({
                          ...prev,
                          message: `Thank you for being our valued customer at ${whatsappCredentials.business_name}! We have some exciting updates to share with you.`
                        }))}
                        disabled={!isConnected}
                        style={{
                          padding: '8px 12px',
                          background: 'white',
                          border: '1px solid #ddd',
                          borderRadius: '6px',
                          cursor: !isConnected ? 'not-allowed' : 'pointer',
                          fontSize: '14px',
                          textAlign: 'left',
                          opacity: !isConnected ? 0.6 : 1
                        }}
                      >
                        Customer Appreciation
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div style={{ textAlign: 'center', marginTop: '30px' }}>
                <button
                  onClick={sendBroadcast}
                  disabled={loading || !broadcastData.recipients || !broadcastData.message || !isConnected}
                  style={{
                    padding: '16px 32px',
                    background: loading || !broadcastData.recipients || !broadcastData.message || !isConnected ? '#ccc' : '#25D366',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '700',
                    cursor: loading || !broadcastData.recipients || !broadcastData.message || !isConnected ? 'not-allowed' : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    margin: '0 auto'
                  }}
                >
                  {loading ? '⏳ Sending Broadcast...' : '📢 Send Broadcast'}
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div style={{
            background: 'rgba(255, 255, 255, 0.95)',
            borderRadius: '20px',
            padding: '40px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}>
            <h2 style={{
              color: '#25D366',
              marginBottom: '30px',
              fontSize: '28px',
              fontWeight: '700'
            }}>
              Analytics & Performance - {user?.name}
            </h2>

            {!isConnected && (
              <div style={{
                background: '#f8d7da',
                border: '1px solid #f5c6cb',
                borderRadius: '8px',
                padding: '16px',
                marginBottom: '20px'
              }}>
                <p style={{ color: '#721c24', margin: 0, fontSize: '16px' }}>
                  ❌ WhatsApp not connected. Analytics will be available after connecting your WhatsApp Business account.
                </p>
              </div>
            )}
            
            {status && isConnected && (
              <div>
                <div style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                  gap: '20px',
                  marginBottom: '30px'
                }}>
                  <div style={{
                    background: 'linear-gradient(135deg, #25D366, #128C7E)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    color: 'white'
                  }}>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
                      {status.whatsapp_automation?.stats?.total_messages || 0}
                    </div>
                    <div style={{ fontSize: '14px', opacity: 0.9 }}>
                      Total Messages Sent
                    </div>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #00C851, #00A047)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    color: 'white'
                  }}>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
                      {status.whatsapp_automation?.stats?.successful_messages || 0}
                    </div>
                    <div style={{ fontSize: '14px', opacity: 0.9 }}>
                      Successful Deliveries
                    </div>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #ff4444, #cc0000)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    color: 'white'
                  }}>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
                      {status.whatsapp_automation?.stats?.failed_messages || 0}
                    </div>
                    <div style={{ fontSize: '14px', opacity: 0.9 }}>
                      Failed Messages
                    </div>
                  </div>

                  <div style={{
                    background: 'linear-gradient(135deg, #667eea, #764ba2)',
                    borderRadius: '12px',
                    padding: '20px',
                    textAlign: 'center',
                    color: 'white'
                  }}>
                    <div style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '8px' }}>
                      {status.whatsapp_automation?.stats?.total_messages > 0 
                        ? Math.round((status.whatsapp_automation.stats.successful_messages / status.whatsapp_automation.stats.total_messages) * 100) 
                        : 0}%
                    </div>
                    <div style={{ fontSize: '14px', opacity: 0.9 }}>
                      Success Rate
                    </div>
                  </div>
                </div>

                <div style={{
                  background: '#f8f9fa',
                  borderRadius: '12px',
                  padding: '20px',
                  marginBottom: '20px'
                }}>
                  <h3 style={{ color: '#128C7E', marginBottom: '16px' }}>
                    Activity Summary
                  </h3>
                  <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                    gap: '16px'
                  }}>
                    <div>
                      <strong>Business Name:</strong> {whatsappCredentials.business_name || 'Not configured'}
                    </div>
                    <div>
                      <strong>Auto-Reply Status:</strong>
                      <span style={{
                        color: status.whatsapp_automation?.config?.auto_reply_enabled ? '#00C851' : '#666',
                        marginLeft: '8px',
                        fontWeight: '600'
                      }}>
                        {status.whatsapp_automation?.config?.auto_reply_enabled ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div>
                      <strong>Campaign Status:</strong>
                      <span style={{
                        color: status.whatsapp_automation?.config?.campaign_enabled ? '#00C851' : '#666',
                        marginLeft: '8px',
                        fontWeight: '600'
                      }}>
                        {status.whatsapp_automation?.config?.campaign_enabled ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    <div>
                      <strong>Last Activity:</strong> {status.whatsapp_automation?.stats?.last_activity 
                        ? new Date(status.whatsapp_automation.stats.last_activity).toLocaleString() 
                        : 'No recent activity'}
                    </div>
                  </div>
                </div>

                <div style={{
                  background: '#e8f5e8',
                  borderRadius: '12px',
                  padding: '20px'
                }}>
                  <h3 style={{ color: '#128C7E', marginBottom: '16px' }}>
                    Performance Tips for {user?.name}
                  </h3>
                  <ul style={{ margin: 0, paddingLeft: '20px', color: '#333' }}>
                    <li style={{ marginBottom: '8px' }}>
                      Personalize your messages to improve engagement rates
                    </li>
                    <li style={{ marginBottom: '8px' }}>
                      Send messages during business hours for better response rates
                    </li>
                    <li style={{ marginBottom: '8px' }}>
                      Use templates for consistent messaging
                    </li>
                    <li style={{ marginBottom: '8px' }}>
                      Monitor failed messages and update contact information
                    </li>
                    <li>
                      Keep messages concise and include clear calls-to-action
                    </li>
                  </ul>
                </div>
              </div>
            )}

            {!status && isConnected && (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <p style={{ color: '#666', fontSize: '18px' }}>
                  Loading analytics data...
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default WhatsAppAutomation;