import React, { useState, useEffect } from 'react';

const InstagramComponent = ({ platform, userProfile }) => {
  const [config, setConfig] = useState({
    postsPerDay: platform === 'instagram' ? 2 : 3,
    postingTimes: [],
    hashtags: platform === 'instagram' ? ['#business', '#entrepreneur', '#growth'] : [],
    pages: platform === 'facebook' ? [] : undefined
  });

  const platformConfig = {
    facebook: { color: '#4267B2', icon: '📘', name: 'Facebook', maxPosts: 5 },
    instagram: { color: '#E4405F', icon: '📸', name: 'Instagram', maxPosts: 3 }
  };

  const currentPlatform = platformConfig[platform];

  const addTime = () => {
    const now = new Date();
    now.setMinutes(now.getMinutes() + 5);
    const testTime = now.toTimeString().slice(0, 5);
    if (!config.postingTimes.includes(testTime)) {
      setConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, testTime].sort() }));
    }
  };

  const removeTime = (timeToRemove) => {
    setConfig(prev => ({ ...prev, postingTimes: prev.postingTimes.filter(t => t !== timeToRemove) }));
  };

  const addHashtag = (hashtag) => {
    if (hashtag && !config.hashtags.includes(hashtag)) {
      setConfig(prev => ({ ...prev, hashtags: [...prev.hashtags, hashtag] }));
    }
  };

  const removeHashtag = (hashtagToRemove) => {
    setConfig(prev => ({ ...prev, hashtags: prev.hashtags.filter(h => h !== hashtagToRemove) }));
  };

  return (
    <div style={{ padding: '24px', background: 'rgba(255,255,255,0.05)', borderRadius: '16px', border: `2px solid ${currentPlatform.color}20` }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
        <span style={{ fontSize: '32px' }}>{currentPlatform.icon}</span>
        <h3 style={{ margin: 0, color: currentPlatform.color, fontSize: '24px' }}>{currentPlatform.name} Automation Settings</h3>
      </div>

      {/* Posts Per Day */}
      <div style={{ marginBottom: '24px' }}>
        <label style={{ display: 'block', fontSize: '14px', fontWeight: '600', color: '#374151', marginBottom: '8px' }}>Posts Per Day</label>
        <input type="number" min="1" max={currentPlatform.maxPosts} value={config.postsPerDay} onChange={(e) => setConfig(prev => ({ ...prev, postsPerDay: parseInt(e.target.value) || 1 }))} style={{ padding: '10px 14px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '8px', fontSize: '14px', background: 'white', width: '120px' }} />
        <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px' }}>Recommended: {platform === 'instagram' ? '1-2' : '2-3'} posts per day</div>
      </div>

      {/* Posting Times */}
      <div style={{ marginBottom: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
          <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Posting Schedule</label>
          <button onClick={addTime} type="button" style={{ padding: '6px 12px', background: currentPlatform.color, color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', cursor: 'pointer' }}>Add Time (+5min)</button>
        </div>
        
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center', marginBottom: '12px' }}>
          <input type="time" onChange={(e) => { if (e.target.value && !config.postingTimes.includes(e.target.value)) { setConfig(prev => ({ ...prev, postingTimes: [...prev.postingTimes, e.target.value].sort() })); e.target.value = ''; } }} style={{ padding: '8px 10px', border: '2px solid rgba(0, 0, 0, 0.1)', borderRadius: '6px', fontSize: '13px' }} />
          <span style={{ fontSize: '12px', color: '#6b7280' }}>Add custom time</span>
        </div>

        {config.postingTimes.length > 0 && (
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {config.postingTimes.map(time => (
              <span key={time} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 8px', background: 'white', border: `1px solid ${currentPlatform.color}40`, borderRadius: '12px', color: currentPlatform.color, fontSize: '12px', fontWeight: '500' }}>
                {time}
                <button onClick={() => removeTime(time)} style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '14px', cursor: 'pointer', padding: '0', lineHeight: '1' }}>×</button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Platform Specific Settings */}
      {platform === 'instagram' && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <label style={{ fontSize: '14px', fontWeight: '600', color: '#374151' }}>Hashtags</label>
            <button onClick={() => { const hashtag = prompt('Enter hashtag (without #):'); if (hashtag) addHashtag(`#${hashtag.replace('#', '')}`); }} type="button" style={{ padding: '6px 12px', background: currentPlatform.color, color: 'white', border: 'none', borderRadius: '6px', fontSize: '12px', cursor: 'pointer' }}>Add Hashtag</button>
          </div>
          
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {config.hashtags.map(hashtag => (
              <span key={hashtag} style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '4px 8px', background: 'white', border: `1px solid ${currentPlatform.color}40`, borderRadius: '12px', color: currentPlatform.color, fontSize: '12px', fontWeight: '500' }}>
                {hashtag}
                <button onClick={() => removeHashtag(hashtag)} style={{ background: 'none', border: 'none', color: '#ef4444', fontSize: '14px', cursor: 'pointer', padding: '0', lineHeight: '1' }}>×</button>
              </span>
            ))}
          </div>
          <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '8px' }}>Recommended: 5-10 relevant hashtags for better reach</div>
        </div>
      )}

      {/* Best Practices */}
      <div style={{ padding: '16px', background: `${currentPlatform.color}10`, borderRadius: '8px', border: `1px solid ${currentPlatform.color}30` }}>
        <h4 style={{ margin: '0 0 8px 0', color: currentPlatform.color, fontSize: '14px' }}>{currentPlatform.name} Best Practices:</h4>
        <ul style={{ margin: 0, paddingLeft: '16px', fontSize: '12px', color: '#374151' }}>
          {platform === 'facebook' ? (
            <>
              <li>Post when your audience is most active (typically 9AM-10AM, 3PM-4PM)</li>
              <li>Use engaging questions to encourage comments</li>
              <li>Share behind-the-scenes content and customer stories</li>
              <li>Keep posts concise but informative</li>
            </>
          ) : (
            <>
              <li>Post high-quality, visually appealing images</li>
              <li>Use relevant hashtags (5-10 per post)</li>
              <li>Post consistently during peak hours (11AM-1PM, 7PM-9PM)</li>
              <li>Engage with your audience through Stories and Reels</li>
            </>
          )}
        </ul>
      </div>

      {/* Quick Stats Preview */}
      <div style={{ marginTop: '20px', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px', textAlign: 'center' }}>
        <div style={{ padding: '12px', background: 'white', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: currentPlatform.color }}>{config.postsPerDay}</div>
          <div style={{ fontSize: '11px', color: '#6b7280' }}>Posts/Day</div>
        </div>
        <div style={{ padding: '12px', background: 'white', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: currentPlatform.color }}>{config.postingTimes.length}</div>
          <div style={{ fontSize: '11px', color: '#6b7280' }}>Time Slots</div>
        </div>
        <div style={{ padding: '12px', background: 'white', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
          <div style={{ fontSize: '18px', fontWeight: 'bold', color: currentPlatform.color }}>{platform === 'instagram' ? config.hashtags.length : '∞'}</div>
          <div style={{ fontSize: '11px', color: '#6b7280' }}>{platform === 'instagram' ? 'Hashtags' : 'Pages'}</div>
        </div>
      </div>
    </div>
  );
};

export default InstagramComponent;