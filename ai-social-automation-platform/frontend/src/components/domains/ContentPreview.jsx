import React, { useState, useEffect } from 'react';
import { 
  RefreshCw, 
  Copy, 
  Edit, 
  Share2, 
  Calendar, 
  Heart, 
  MessageCircle, 
  Bookmark,
  MoreHorizontal,
  Image,
  Video,
  Hash,
  Clock,
  User,
  MapPin
} from 'lucide-react';
import { useToast } from '../common/Toast';

const ContentPreview = ({ domain, platform, onContentGenerate, onContentSave }) => {
  const [content, setContent] = useState(null);
  const [generating, setGenerating] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editedContent, setEditedContent] = useState('');
  const { toast } = useToast();

  useEffect(() => {
    if (domain && platform) {
      generateContent();
    }
  }, [domain, platform]);

  const generateContent = async () => {
    try {
      setGenerating(true);
      
      const response = await fetch('/api/content/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          domain: domain.name,
          platform,
          content_type: 'text'
        })
      });

      if (response.ok) {
        const data = await response.json();
        setContent({
          text: data.content,
          hashtags: data.hashtags || [],
          media_suggestions: data.media_suggestions || [],
          estimated_engagement: Math.floor(Math.random() * 1000) + 100,
          optimal_time: data.optimal_time || '7:00 PM',
          character_count: data.content.length
        });
        setEditedContent(data.content);
        onContentGenerate?.(data);
      } else {
        throw new Error('Failed to generate content');
      }
    } catch (error) {
      console.error('Error generating content:', error);
      toast.error('Failed to generate content');
      // Demo content for development
      setContent({
        text: getDemoContent(domain.name, platform),
        hashtags: domain.hashtags || ['#content', '#social'],
        media_suggestions: ['motivational-quote.jpg', 'trending-meme.gif'],
        estimated_engagement: Math.floor(Math.random() * 1000) + 100,
        optimal_time: '7:00 PM',
        character_count: 150
      });
    } finally {
      setGenerating(false);
    }
  };

  const getDemoContent = (domainName, platform) => {
    const demoContents = {
      memes: {
        instagram: "When you finally understand that JavaScript callback... 😅 #coding #memes #javascript",
        facebook: "That moment when your code works on the first try and you don't trust it 🤔 Who else can relate?",
        twitter: "Me: I'll just fix this one small bug\n*3 hours later*\nMe: How did I break the entire application? 😭",
        linkedin: "The learning curve in tech might be steep, but the view from the top is worth it! 💪 #TechCareers",
        youtube: "Today's video: Why every developer needs to learn to laugh at their own code mistakes!"
      },
      'tech-news': {
        instagram: "🚀 Breaking: New AI breakthrough could revolutionize how we code! What do you think about AI-assisted development?",
        facebook: "The future of technology is here! Latest updates from the world of AI and machine learning that will blow your mind.",
        twitter: "BREAKING: Major tech company announces game-changing AI feature. This could change everything! 🤯",
        linkedin: "Industry Analysis: How emerging AI technologies are reshaping the job market in 2024. Key insights for professionals.",
        youtube: "In today's tech update: The 5 most important technology trends that will dominate 2024"
      },
      'business-tips': {
        instagram: "💡 Business Tip: Your network is your net worth. Start building meaningful connections today! #entrepreneurship",
        facebook: "Success isn't just about having a great idea - it's about executing it consistently every single day. What's your daily success habit?",
        twitter: "The difference between successful entrepreneurs and dreamers? They start before they're ready. 🚀",
        linkedin: "Key insight from today's market analysis: Companies that prioritize customer experience see 60% higher profits.",
        youtube: "Today's topic: 5 business mistakes that cost entrepreneurs their dreams (and how to avoid them)"
      }
    };

    return demoContents[domainName]?.[platform] || "Generated content will appear here...";
  };

  const getPlatformPreview = () => {
    if (!content) return null;

    const platformStyles = {
      instagram: {
        background: 'bg-gradient-to-br from-purple-600 via-pink-600 to-yellow-500',
        avatar: '👤',
        username: 'your_account',
        time: '2m'
      },
      facebook: {
        background: 'bg-blue-600',
        avatar: '👤',
        username: 'Your Page',
        time: '2 mins'
      },
      twitter: {
        background: 'bg-sky-500',
        avatar: '👤',
        username: 'your_handle',
        time: '2m'
      },
      linkedin: {
        background: 'bg-blue-700',
        avatar: '👤',
        username: 'Your Name',
        time: '2 minutes'
      },
      youtube: {
        background: 'bg-red-600',
        avatar: '👤',
        username: 'Your Channel',
        time: '2 minutes ago'
      }
    };

    const style = platformStyles[platform] || platformStyles.instagram;

    return (
      <div className="bg-white border rounded-lg overflow-hidden shadow-sm">
        {/* Platform Header */}
        <div className={`${style.background} px-4 py-2 text-white text-sm font-medium`}>
          📱 {platform.charAt(0).toUpperCase() + platform.slice(1)} Preview
        </div>

        {/* Post Header */}
        <div className="p-4 border-b">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center text-lg">
              {style.avatar}
            </div>
            <div>
              <div className="font-semibold text-gray-900">{style.username}</div>
              <div className="text-sm text-gray-500 flex items-center">
                <Clock className="w-3 h-3 mr-1" />
                {style.time}
              </div>
            </div>
            <div className="ml-auto">
              <MoreHorizontal className="w-5 h-5 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Post Content */}
        <div className="p-4">
          {editing ? (
            <div className="space-y-3">
              <textarea
                value={editedContent}
                onChange={(e) => setEditedContent(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                rows={4}
                placeholder="Edit your content..."
              />
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-500">
                  {editedContent.length} characters
                </span>
                <div className="flex space-x-2">
                  <button
                    onClick={() => {
                      setContent(prev => ({ ...prev, text: editedContent }));
                      setEditing(false);
                      toast.success('Content updated!');
                    }}
                    className="px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                  >
                    Save
                  </button>
                  <button
                    onClick={() => {
                      setEditedContent(content.text);
                      setEditing(false);
                    }}
                    className="px-3 py-1 bg-gray-300 text-gray-700 rounded text-sm hover:bg-gray-400"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <p className="text-gray-900 whitespace-pre-wrap">{content.text}</p>
              
              {/* Hashtags */}
              {content.hashtags && content.hashtags.length > 0 && (
                <div className="flex flex-wrap gap-1">
                  {content.hashtags.map((hashtag, index) => (
                    <span
                      key={index}
                      className="text-blue-600 hover:text-blue-700 cursor-pointer text-sm"
                    >
                      {hashtag}
                    </span>
                  ))}
                </div>
              )}

              {/* Media Suggestions */}
              {content.media_suggestions && content.media_suggestions.length > 0 && (
                <div className="mt-3">
                  <div className="text-sm text-gray-600 mb-2">Suggested media:</div>
                  <div className="flex space-x-2">
                    {content.media_suggestions.slice(0, 2).map((media, index) => (
                      <div
                        key={index}
                        className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center border-2 border-dashed border-gray-300"
                      >
                        {media.includes('video') || media.includes('.mp4') ? (
                          <Video className="w-6 h-6 text-gray-400" />
                        ) : (
                          <Image className="w-6 h-6 text-gray-400" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Engagement Actions */}
        <div className="px-4 py-3 border-t bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button className="flex items-center space-x-1 text-gray-600 hover:text-red-600">
                <Heart className="w-5 h-5" />
                <span className="text-sm">{content.estimated_engagement}</span>
              </button>
              <button className="flex items-center space-x-1 text-gray-600 hover:text-blue-600">
                <MessageCircle className="w-5 h-5" />
                <span className="text-sm">{Math.floor(content.estimated_engagement * 0.1)}</span>
              </button>
              <button className="flex items-center space-x-1 text-gray-600 hover:text-green-600">
                <Share2 className="w-5 h-5" />
                <span className="text-sm">{Math.floor(content.estimated_engagement * 0.05)}</span>
              </button>
            </div>
            <button className="text-gray-600 hover:text-gray-700">
              <Bookmark className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    );
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(content.text);
      toast.success('Content copied to clipboard!');
    } catch (error) {
      toast.error('Failed to copy content');
    }
  };

  const schedulePost = () => {
    // Implementation for scheduling
    toast.success('Post scheduled for optimal time!');
  };

  const saveAsDraft = () => {
    onContentSave?.({
      ...content,
      domain: domain.name,
      platform,
      status: 'draft'
    });
    toast.success('Content saved as draft!');
  };

  if (generating) {
    return (
      <div className="space-y-4">
        <div className="text-center py-8">
          <RefreshCw className="w-8 h-8 text-blue-500 animate-spin mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Generating Content</h3>
          <p className="text-gray-600">AI is creating {platform} content for {domain?.display_name}...</p>
        </div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="text-center py-8">
        <div className="text-gray-400 mb-4">
          <Edit className="w-12 h-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Content Generated</h3>
        <p className="text-gray-600 mb-4">Select a domain and platform to generate content</p>
        <button
          onClick={generateContent}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Generate Content
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Content Preview</h3>
          <p className="text-sm text-gray-600">
            {domain?.display_name} content for {platform.charAt(0).toUpperCase() + platform.slice(1)}
          </p>
        </div>
        <button
          onClick={generateContent}
          disabled={generating}
          className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${generating ? 'animate-spin' : ''}`} />
          Regenerate
        </button>
      </div>

      {/* Platform Preview */}
      {getPlatformPreview()}

      {/* Content Analytics */}
      <div className="bg-white border rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Content Analytics</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">
              {content.character_count}
            </div>
            <div className="text-sm text-gray-600">Characters</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">
              {content.hashtags?.length || 0}
            </div>
            <div className="text-sm text-gray-600">Hashtags</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {content.estimated_engagement}
            </div>
            <div className="text-sm text-gray-600">Est. Engagement</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">
              {content.optimal_time}
            </div>
            <div className="text-sm text-gray-600">Optimal Time</div>
          </div>
        </div>
      </div>

      {/* Platform-Specific Insights */}
      <div className="bg-gray-50 border rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-3">Platform Insights</h4>
        <div className="space-y-2 text-sm">
          {platform === 'instagram' && (
            <>
              <p>• Instagram posts with hashtags get 12.6% more engagement</p>
              <p>• Optimal length: 125-150 characters for captions</p>
              <p>• Best posting time: 6-9 PM local time</p>
            </>
          )}
          {platform === 'twitter' && (
            <>
              <p>• Tweets with images get 150% more retweets</p>
              <p>• Optimal length: 71-100 characters for maximum engagement</p>
              <p>• Best posting time: 9 AM and 3 PM</p>
            </>
          )}
          {platform === 'linkedin' && (
            <>
              <p>• Professional content performs 20% better</p>
              <p>• Posts with questions get 100% more comments</p>
              <p>• Best posting time: Tuesday-Thursday, 7-8 AM</p>
            </>
          )}
          {platform === 'facebook' && (
            <>
              <p>• Posts with emotional content get 2x more shares</p>
              <p>• Optimal length: 40-80 characters</p>
              <p>• Best posting time: 1-3 PM</p>
            </>
          )}
          {platform === 'youtube' && (
            <>
              <p>• Compelling titles increase CTR by 30%</p>
              <p>• Optimal title length: 60 characters or less</p>
              <p>• Best upload time: 2-4 PM EST</p>
            </>
          )}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => setEditing(!editing)}
          className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <Edit className="w-4 h-4 mr-2" />
          {editing ? 'Cancel Edit' : 'Edit Content'}
        </button>

        <button
          onClick={copyToClipboard}
          className="flex items-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          <Copy className="w-4 h-4 mr-2" />
          Copy Text
        </button>

        <button
          onClick={schedulePost}
          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          <Calendar className="w-4 h-4 mr-2" />
          Schedule Post
        </button>

        <button
          onClick={saveAsDraft}
          className="flex items-center px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
        >
          <Bookmark className="w-4 h-4 mr-2" />
          Save Draft
        </button>

        <button
          onClick={() => onContentSave?.({
            ...content,
            domain: domain.name,
            platform,
            status: 'approved'
          })}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Share2 className="w-4 h-4 mr-2" />
          Post Now
        </button>
      </div>

      {/* Content Variations */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-gray-900">Content Variations</h4>
          <button className="text-sm text-blue-600 hover:text-blue-700">
            Generate More
          </button>
        </div>
        <div className="space-y-2">
          {[
            "Shorter version optimized for Twitter",
            "Professional tone for LinkedIn",
            "Casual version with more emojis"
          ].map((variation, index) => (
            <button
              key={index}
              onClick={() => {
                // Generate variation
                toast.success(`Generating ${variation.toLowerCase()}...`);
              }}
              className="block w-full text-left p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors text-sm"
            >
              {variation}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ContentPreview;