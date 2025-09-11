import React, { useState, useEffect } from 'react';
import './RedditAUTO.css';

const RedditAUTO = () => {
  const [activeTab, setActiveTab] = useState('setup');
  const [loading, setLoading] = useState(false);
  const [automationStatus, setAutomationStatus] = useState(null);
  const [redditConnected, setRedditConnected] = useState(false);
  
  // Auto-posting configuration
  const [autoPostConfig, setAutoPostConfig] = useState({
    domain: 'education',
    businessType: '',
    targetAudience: 'indian_users',
    language: 'en',
    subreddits: [],
    postsPerDay: 3,
    postingTimes: ['09:00', '14:00', '19:00'],
    contentStyle: 'engaging',
    enabled: false
  });

  // Auto-reply configuration
  const [autoReplyConfig, setAutoReplyConfig] = useState({
    domain: 'education',
    expertiseLevel: 'intermediate',
    subreddits: [],
    keywords: '',
    maxRepliesPerHour: 2,
    responseDelayMinutes: 15,
    enabled: false
  });

  // Performance metrics
  const [performanceData, setPerformanceData] = useState(null);

  // Domain-specific subreddit suggestions
  const domainSubreddits = {
    education: ['JEE', 'NEET', 'IndianStudents', 'india', 'AskReddit', 'studytips'],
    restaurant: ['IndianFood', 'food', 'bangalore', 'mumbai', 'delhi', 'FoodPorn'],
    tech: ['developersIndia', 'programming', 'india', 'bangalore', 'cscareerquestions'],
    health: ['fitness', 'HealthyFood', 'india', 'mentalhealth', 'nutrition'],
    business: ['entrepreneur', 'IndiaInvestments', 'business', 'india', 'startup']
  };

  // Available posting times
  const availablePostingTimes = [
    '06:00', '08:00', '09:00', '11:00', '12:00', 
    '14:00', '16:00', '18:00', '19:00', '20:00', '22:00'
  ];

  useEffect(() => {
    checkRedditConnection();
    loadAutomationStatus();
  }, []);

  const makeAPIRequest = async (endpoint, method = 'GET', data = null) => {
    try {
      const config = {
        method,
        headers: {
          'Content-Type': 'application/json'
        }
      };
      
      if (data && method !== 'GET') {
        config.body = JSON.stringify(data);
      }
      
      const response = await fetch(`http://localhost:8000${endpoint}`, config);
      return await response.json();
    } catch (error) {
      console.error('API Request failed:', error);
      return { success: false, error: error.message };
    }
  };

  const checkRedditConnection = async () => {
    const response = await makeAPIRequest('/api/reddit/connection-status');
    setRedditConnected(response.connected || false);
  };

  const loadAutomationStatus = async () => {
    setLoading(true);
    const response = await makeAPIRequest('/api/automation/status');
    if (response.success) {
      setAutomationStatus(response);
      
      // Update local state with server configuration
      if (response.auto_posting?.config) {
        setAutoPostConfig(prev => ({
          ...prev,
          ...response.auto_posting.config,
          enabled: response.auto_posting.enabled
        }));
      }
      
      if (response.auto_replies?.config) {
        setAutoReplyConfig(prev => ({
          ...prev,
          ...response.auto_replies.config,
          enabled: response.auto_replies.enabled
        }));
      }
    }
    setLoading(false);
  };

  const loadPerformanceAnalytics = async () => {
    const response = await makeAPIRequest('/api/automation/performance-analytics');
    if (response.success) {
      setPerformanceData(response.performance);
    }
  };

  const handleRedditConnect = async () => {
    const response = await makeAPIRequest('/api/oauth/reddit/authorize');
    if (response.success && response.redirect_url) {
      window.open(response.redirect_url, '_blank');
    }
  };

  const setupAutoPosting = async () => {
    if (!autoPostConfig.businessType || autoPostConfig.subreddits.length === 0) {
      alert('Please fill in business description and select at least one subreddit');
      return;
    }

    setLoading(true);
    const response = await makeAPIRequest('/api/automation/setup-auto-posting', 'POST', {
      domain: autoPostConfig.domain,
      business_type: autoPostConfig.businessType,
      target_audience: autoPostConfig.targetAudience,
      language: autoPostConfig.language,
      subreddits: autoPostConfig.subreddits,
      posts_per_day: autoPostConfig.postsPerDay,
      posting_times: autoPostConfig.postingTimes,
      content_style: autoPostConfig.contentStyle
    });

    if (response.success) {
      setAutoPostConfig(prev => ({ ...prev, enabled: true }));
      alert('Auto-posting enabled successfully!');
      loadAutomationStatus();
    } else {
      alert(`Setup failed: ${response.error}`);
    }
    setLoading(false);
  };

  const setupAutoReplies = async () => {
    if (!autoReplyConfig.keywords || autoReplyConfig.subreddits.length === 0) {
      alert('Please enter keywords and select subreddits to monitor');
      return;
    }

    setLoading(true);
    const keywordList = autoReplyConfig.keywords.split(',').map(k => k.trim());
    
    const response = await makeAPIRequest('/api/automation/setup-auto-replies', 'POST', {
      domain: autoReplyConfig.domain,
      expertise_level: autoReplyConfig.expertiseLevel,
      subreddits: autoReplyConfig.subreddits,
      keywords: keywordList,
      max_replies_per_hour: autoReplyConfig.maxRepliesPerHour,
      response_delay_minutes: autoReplyConfig.responseDelayMinutes
    });

    if (response.success) {
      setAutoReplyConfig(prev => ({ ...prev, enabled: true }));
      alert('Auto-replies enabled successfully!');
      loadAutomationStatus();
    } else {
      alert(`Setup failed: ${response.error}`);
    }
    setLoading(false);
  };

  const updateSchedule = async (type, scheduleData) => {
    const response = await makeAPIRequest('/api/automation/update-schedule', 'POST', {
      type,
      ...scheduleData
    });

    if (response.success) {
      alert(`${type} schedule updated successfully!`);
      loadAutomationStatus();
    } else {
      alert(`Update failed: ${response.error}`);
    }
  };

  const toggleAutomation = async (type, enabled) => {
    if (type === 'auto_posting') {
      await updateSchedule('auto_posting', { enabled });
      setAutoPostConfig(prev => ({ ...prev, enabled }));
    } else if (type === 'auto_replies') {
      await updateSchedule('auto_replies', { enabled });
      setAutoReplyConfig(prev => ({ ...prev, enabled }));
    }
  };

  return (
    <div className="reddit-auto-container">
      <div className="header">
        <h1>Reddit Automation Dashboard</h1>
        <div className="connection-status">
          {redditConnected ? (
            <span className="status-connected">✅ Reddit Connected</span>
          ) : (
            <button onClick={handleRedditConnect} className="connect-button">
              Connect Reddit Account
            </button>
          )}
        </div>
      </div>

      <div className="tabs">
        <button 
          className={`tab ${activeTab === 'setup' ? 'active' : ''}`}
          onClick={() => setActiveTab('setup')}
        >
          Automation Setup
        </button>
        <button 
          className={`tab ${activeTab === 'schedule' ? 'active' : ''}`}
          onClick={() => setActiveTab('schedule')}
        >
          Schedule Management
        </button>
        <button 
          className={`tab ${activeTab === 'analytics' ? 'active' : ''}`}
          onClick={() => setActiveTab('analytics')}
        >
          Performance Analytics
        </button>
        <button 
          className={`tab ${activeTab === 'status' ? 'active' : ''}`}
          onClick={() => setActiveTab('status')}
        >
          Current Status
        </button>
      </div>

      {/* Automation Setup Tab */}
      {activeTab === 'setup' && (
        <div className="tab-content">
          <div className="setup-sections">
            
            {/* Auto-Posting Setup */}
            <div className="setup-section">
              <h2>🚀 Auto-Posting Configuration</h2>
              <div className="config-grid">
                <div className="config-column">
                  <div className="form-group">
                    <label>Business Domain</label>
                    <select 
                      value={autoPostConfig.domain}
                      onChange={(e) => {
                        const newDomain = e.target.value;
                        setAutoPostConfig(prev => ({
                          ...prev,
                          domain: newDomain,
                          subreddits: domainSubreddits[newDomain]?.slice(0, 3) || []
                        }));
                      }}
                    >
                      <option value="education">Education</option>
                      <option value="restaurant">Restaurant</option>
                      <option value="tech">Technology</option>
                      <option value="health">Health</option>
                      <option value="business">Business</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Business Description</label>
                    <input
                      type="text"
                      placeholder="e.g., JEE coaching institute in Delhi..."
                      value={autoPostConfig.businessType}
                      onChange={(e) => setAutoPostConfig(prev => ({
                        ...prev,
                        businessType: e.target.value
                      }))}
                    />
                  </div>

                  <div className="form-group">
                    <label>Target Audience</label>
                    <select 
                      value={autoPostConfig.targetAudience}
                      onChange={(e) => setAutoPostConfig(prev => ({
                        ...prev,
                        targetAudience: e.target.value
                      }))}
                    >
                      <option value="indian_students">Indian Students</option>
                      <option value="food_lovers">Food Lovers</option>
                      <option value="tech_professionals">Tech Professionals</option>
                      <option value="health_conscious">Health Conscious</option>
                      <option value="entrepreneurs">Entrepreneurs</option>
                    </select>
                  </div>
                </div>

                <div className="config-column">
                  <div className="form-group">
                    <label>Posts Per Day: {autoPostConfig.postsPerDay}</label>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={autoPostConfig.postsPerDay}
                      onChange={(e) => setAutoPostConfig(prev => ({
                        ...prev,
                        postsPerDay: parseInt(e.target.value)
                      }))}
                    />
                  </div>

                  <div className="form-group">
                    <label>Content Style</label>
                    <select 
                      value={autoPostConfig.contentStyle}
                      onChange={(e) => setAutoPostConfig(prev => ({
                        ...prev,
                        contentStyle: e.target.value
                      }))}
                    >
                      <option value="engaging">Engaging</option>
                      <option value="informative">Informative</option>
                      <option value="promotional">Promotional</option>
                      <option value="helpful">Helpful</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Language</label>
                    <select 
                      value={autoPostConfig.language}
                      onChange={(e) => setAutoPostConfig(prev => ({
                        ...prev,
                        language: e.target.value
                      }))}
                    >
                      <option value="en">English</option>
                      <option value="hi">Hindi</option>
                    </select>
                  </div>
                </div>
              </div>

              {/* Posting Times */}
              <div className="form-group">
                <label>Posting Times (Select {autoPostConfig.postsPerDay} times)</label>
                <div className="time-grid">
                  {availablePostingTimes.map(time => (
                    <label key={time} className="time-checkbox">
                      <input
                        type="checkbox"
                        checked={autoPostConfig.postingTimes.includes(time)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            if (autoPostConfig.postingTimes.length < autoPostConfig.postsPerDay) {
                              setAutoPostConfig(prev => ({
                                ...prev,
                                postingTimes: [...prev.postingTimes, time]
                              }));
                            }
                          } else {
                            setAutoPostConfig(prev => ({
                              ...prev,
                              postingTimes: prev.postingTimes.filter(t => t !== time)
                            }));
                          }
                        }}
                      />
                      {time}
                    </label>
                  ))}
                </div>
              </div>

              {/* Target Subreddits */}
              <div className="form-group">
                <label>Target Subreddits (Recommended for {autoPostConfig.domain})</label>
                <div className="subreddit-grid">
                  {(domainSubreddits[autoPostConfig.domain] || []).map(subreddit => (
                    <label key={subreddit} className="subreddit-checkbox">
                      <input
                        type="checkbox"
                        checked={autoPostConfig.subreddits.includes(subreddit)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setAutoPostConfig(prev => ({
                              ...prev,
                              subreddits: [...prev.subreddits, subreddit]
                            }));
                          } else {
                            setAutoPostConfig(prev => ({
                              ...prev,
                              subreddits: prev.subreddits.filter(s => s !== subreddit)
                            }));
                          }
                        }}
                      />
                      r/{subreddit}
                    </label>
                  ))}
                </div>
              </div>

              <button 
                onClick={setupAutoPosting}
                disabled={loading || !redditConnected}
                className="setup-button primary"
              >
                {loading ? 'Setting up...' : 'Enable Auto-Posting'}
              </button>
            </div>

            {/* Auto-Reply Setup */}
            <div className="setup-section">
              <h2>💬 Auto-Reply Configuration</h2>
              <div className="config-grid">
                <div className="config-column">
                  <div className="form-group">
                    <label>Expertise Domain</label>
                    <select 
                      value={autoReplyConfig.domain}
                      onChange={(e) => {
                        const newDomain = e.target.value;
                        setAutoReplyConfig(prev => ({
                          ...prev,
                          domain: newDomain,
                          subreddits: domainSubreddits[newDomain]?.slice(0, 2) || []
                        }));
                      }}
                    >
                      <option value="education">Education</option>
                      <option value="tech">Technology</option>
                      <option value="health">Health</option>
                      <option value="business">Business</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Expertise Level</label>
                    <select 
                      value={autoReplyConfig.expertiseLevel}
                      onChange={(e) => setAutoReplyConfig(prev => ({
                        ...prev,
                        expertiseLevel: e.target.value
                      }))}
                    >
                      <option value="beginner">Beginner</option>
                      <option value="intermediate">Intermediate</option>
                      <option value="expert">Expert</option>
                    </select>
                  </div>

                  <div className="form-group">
                    <label>Keywords to Monitor</label>
                    <textarea
                      placeholder="help, advice, tips, guidance, how to, best way, struggling with"
                      value={autoReplyConfig.keywords}
                      onChange={(e) => setAutoReplyConfig(prev => ({
                        ...prev,
                        keywords: e.target.value
                      }))}
                      rows="3"
                    />
                  </div>
                </div>

                <div className="config-column">
                  <div className="form-group">
                    <label>Max Replies Per Hour: {autoReplyConfig.maxRepliesPerHour}</label>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={autoReplyConfig.maxRepliesPerHour}
                      onChange={(e) => setAutoReplyConfig(prev => ({
                        ...prev,
                        maxRepliesPerHour: parseInt(e.target.value)
                      }))}
                    />
                  </div>

                  <div className="form-group">
                    <label>Response Delay (minutes): {autoReplyConfig.responseDelayMinutes}</label>
                    <input
                      type="range"
                      min="5"
                      max="60"
                      value={autoReplyConfig.responseDelayMinutes}
                      onChange={(e) => setAutoReplyConfig(prev => ({
                        ...prev,
                        responseDelayMinutes: parseInt(e.target.value)
                      }))}
                    />
                  </div>

                  <div className="form-group">
                    <label>Monitor Subreddits</label>
                    <div className="subreddit-grid">
                      {(domainSubreddits[autoReplyConfig.domain] || []).map(subreddit => (
                        <label key={subreddit} className="subreddit-checkbox">
                          <input
                            type="checkbox"
                            checked={autoReplyConfig.subreddits.includes(subreddit)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setAutoReplyConfig(prev => ({
                                  ...prev,
                                  subreddits: [...prev.subreddits, subreddit]
                                }));
                              } else {
                                setAutoReplyConfig(prev => ({
                                  ...prev,
                                  subreddits: prev.subreddits.filter(s => s !== subreddit)
                                }));
                              }
                            }}
                          />
                          r/{subreddit}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              </div>

              <button 
                onClick={setupAutoReplies}
                disabled={loading || !redditConnected}
                className="setup-button primary"
              >
                {loading ? 'Setting up...' : 'Enable Auto-Replies'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Schedule Management Tab */}
      {activeTab === 'schedule' && (
        <div className="tab-content">
          <div className="schedule-management">
            <h2>Schedule Management & Control</h2>
            
            {/* Auto-Posting Schedule */}
            <div className="schedule-section">
              <div className="schedule-header">
                <h3>Auto-Posting Schedule</h3>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={autoPostConfig.enabled}
                    onChange={(e) => toggleAutomation('auto_posting', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              {autoPostConfig.enabled && (
                <div className="schedule-controls">
                  <div className="control-group">
                    <label>Posts Per Day: {autoPostConfig.postsPerDay}</label>
                    <input
                      type="range"
                      min="1"
                      max="5"
                      value={autoPostConfig.postsPerDay}
                      onChange={(e) => {
                        const newValue = parseInt(e.target.value);
                        setAutoPostConfig(prev => ({ ...prev, postsPerDay: newValue }));
                        updateSchedule('auto_posting', { posts_per_day: newValue });
                      }}
                    />
                  </div>
                  
                  <div className="control-group">
                    <label>Posting Times</label>
                    <div className="time-grid">
                      {availablePostingTimes.map(time => (
                        <label key={time} className="time-checkbox">
                          <input
                            type="checkbox"
                            checked={autoPostConfig.postingTimes.includes(time)}
                            onChange={(e) => {
                              let newTimes;
                              if (e.target.checked) {
                                if (autoPostConfig.postingTimes.length < autoPostConfig.postsPerDay) {
                                  newTimes = [...autoPostConfig.postingTimes, time];
                                } else {
                                  return;
                                }
                              } else {
                                newTimes = autoPostConfig.postingTimes.filter(t => t !== time);
                              }
                              setAutoPostConfig(prev => ({ ...prev, postingTimes: newTimes }));
                              updateSchedule('auto_posting', { posting_times: newTimes });
                            }}
                          />
                          {time}
                        </label>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Auto-Reply Schedule */}
            <div className="schedule-section">
              <div className="schedule-header">
                <h3>Auto-Reply Schedule</h3>
                <label className="toggle-switch">
                  <input
                    type="checkbox"
                    checked={autoReplyConfig.enabled}
                    onChange={(e) => toggleAutomation('auto_replies', e.target.checked)}
                  />
                  <span className="slider"></span>
                </label>
              </div>
              
              {autoReplyConfig.enabled && (
                <div className="schedule-controls">
                  <div className="control-group">
                    <label>Max Replies Per Hour: {autoReplyConfig.maxRepliesPerHour}</label>
                    <input
                      type="range"
                      min="1"
                      max="10"
                      value={autoReplyConfig.maxRepliesPerHour}
                      onChange={(e) => {
                        const newValue = parseInt(e.target.value);
                        setAutoReplyConfig(prev => ({ ...prev, maxRepliesPerHour: newValue }));
                        updateSchedule('auto_replies', { max_replies_per_hour: newValue });
                      }}
                    />
                  </div>
                  
                  <div className="control-group">
                    <label>Response Delay (minutes): {autoReplyConfig.responseDelayMinutes}</label>
                    <input
                      type="range"
                      min="5"
                      max="60"
                      value={autoReplyConfig.responseDelayMinutes}
                      onChange={(e) => {
                        const newValue = parseInt(e.target.value);
                        setAutoReplyConfig(prev => ({ ...prev, responseDelayMinutes: newValue }));
                        updateSchedule('auto_replies', { response_delay_minutes: newValue });
                      }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Performance Analytics Tab */}
      {activeTab === 'analytics' && (
        <div className="tab-content">
          <div className="analytics-section">
            <div className="analytics-header">
              <h2>Performance Analytics</h2>
              <button 
                onClick={loadPerformanceAnalytics}
                className="refresh-button"
              >
                Refresh Analytics
              </button>
            </div>
            
            {performanceData ? (
              <div className="analytics-grid">
                <div className="metric-card">
                  <h3>Auto Posts</h3>
                  <div className="metric-value">{performanceData.auto_posts?.total_this_month || 0}</div>
                  <div className="metric-subtitle">
                    {performanceData.auto_posts?.success_rate || 0}% success rate
                  </div>
                </div>
                
                <div className="metric-card">
                  <h3>Auto Replies</h3>
                  <div className="metric-value">{performanceData.auto_replies?.total_this_month || 0}</div>
                  <div className="metric-subtitle">
                    {performanceData.auto_replies?.success_rate || 0}% success rate
                  </div>
                </div>
                
                <div className="metric-card">
                  <h3>Karma Gained</h3>
                  <div className="metric-value">{performanceData.engagement_metrics?.karma_gained || 0}</div>
                  <div className="metric-subtitle">
                    +{performanceData.engagement_metrics?.followers_gained || 0} followers
                  </div>
                </div>
                
                <div className="metric-card">
                  <h3>Questions Answered</h3>
                  <div className="metric-value">{performanceData.auto_replies?.questions_answered || 0}</div>
                  <div className="metric-subtitle">
                    {performanceData.auto_replies?.helpful_votes || 0} helpful votes
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-data">
                <p>Click "Refresh Analytics" to load performance data</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Current Status Tab */}
      {activeTab === 'status' && (
        <div className="tab-content">
          <div className="status-section">
            <div className="status-header">
              <h2>Current Automation Status</h2>
              <button 
                onClick={loadAutomationStatus}
                className="refresh-button"
              >
                Refresh Status
              </button>
            </div>
            
            {automationStatus ? (
              <div className="status-grid">
                <div className="status-card">
                  <h3>Auto-Posting</h3>
                  <div className={`status-indicator ${automationStatus.auto_posting?.enabled ? 'active' : 'inactive'}`}>
                    {automationStatus.auto_posting?.enabled ? 'Active' : 'Inactive'}
                  </div>
                  {automationStatus.auto_posting?.config && (
                    <div className="status-details">
                      <p>Domain: {automationStatus.auto_posting.config.domain}</p>
                      <p>Posts/Day: {automationStatus.auto_posting.config.posts_per_day}</p>
                      <p>Subreddits: {automationStatus.auto_posting.config.subreddits?.length || 0}</p>
                    </div>
                  )}
                </div>
                
                <div className="status-card">
                  <h3>Auto-Replies</h3>
                  <div className={`status-indicator ${automationStatus.auto_replies?.enabled ? 'active' : 'inactive'}`}>
                    {automationStatus.auto_replies?.enabled ? 'Active' : 'Inactive'}
                  </div>
                  {automationStatus.auto_replies?.config && (
                    <div className="status-details">
                      <p>Domain: {automationStatus.auto_replies.config.domain}</p>
                      <p>Max Replies/Hour: {automationStatus.auto_replies.config.max_replies_per_hour}</p>
                      <p>Monitoring: {automationStatus.auto_replies.config.subreddits?.length || 0} subreddits</p>
                    </div>
                  )}
                </div>
                
                <div className="status-card">
                  <h3>Today's Activity</h3>
                  <div className="activity-stats">
                    <div className="stat">
                      <span className="stat-label">Posts Today</span>
                      <span className="stat-value">{automationStatus.daily_stats?.posts_today || 0}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Replies (24h)</span>
                      <span className="stat-value">{automationStatus.daily_stats?.recent_replies || 0}</span>
                    </div>
                    <div className="stat">
                      <span className="stat-label">Karma Gained</span>
                      <span className="stat-value">{automationStatus.daily_stats?.total_karma || 0}</span>
                    </div>
                  </div>
                </div>
                
                <div className="status-card">
                  <h3>System Health</h3>
                  <div className={`status-indicator ${automationStatus.scheduler_running ? 'active' : 'inactive'}`}>
                    Scheduler: {automationStatus.scheduler_running ? 'Running' : 'Stopped'}
                  </div>
                  <div className="status-details">
                    <p>Last Updated: {automationStatus.last_updated ? new Date(automationStatus.last_updated).toLocaleString() : 'Unknown'}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="no-data">
                <p>Loading automation status...</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RedditAUTO;