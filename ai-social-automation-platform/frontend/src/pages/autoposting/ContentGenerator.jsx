import React, { useState, useEffect } from 'react';
import { toast } from 'react-hot-toast';
import { 
  Bot, Sparkles, RefreshCw, Copy, Edit3, Send, Save,
  Target, Zap, Brain, Wand2, TrendingUp, Hash, Image,
  MessageCircle, Heart, Share2, Calendar
} from 'lucide-react';

const ContentGenerator = () => {
  const [selectedDomain, setSelectedDomain] = useState('tech');
  const [selectedPlatforms, setSelectedPlatforms] = useState(['instagram']);
  const [generatedContent, setGeneratedContent] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [editingContent, setEditingContent] = useState(null);
  const [customPrompt, setCustomPrompt] = useState('');
  const [generationSettings, setGenerationSettings] = useState({
    tone: 'professional',
    length: 'medium',
    includeHashtags: true,
    includeEmojis: true,
    followTrends: true,
    creativityLevel: 75,
    generateImage: false
  });

  const domains = [
    { id: 'tech', name: 'Tech & Innovation', icon: '💻', color: 'bg-blue-500' },
    { id: 'memes', name: 'Memes & Humor', icon: '😂', color: 'bg-yellow-500' },
    { id: 'business', name: 'Business Tips', icon: '💼', color: 'bg-green-500' },
    { id: 'lifestyle', name: 'Lifestyle', icon: '🌟', color: 'bg-purple-500' },
    { id: 'fitness', name: 'Health & Fitness', icon: '💪', color: 'bg-red-500' },
    { id: 'finance', name: 'Finance & Crypto', icon: '💰', color: 'bg-emerald-500' },
    { id: 'travel', name: 'Travel & Adventure', icon: '✈️', color: 'bg-cyan-500' },
    { id: 'food', name: 'Food & Recipes', icon: '🍕', color: 'bg-orange-500' }
  ];

  const platforms = [
    { id: 'instagram', name: 'Instagram', icon: '📸', limit: 280 },
    { id: 'facebook', name: 'Facebook', icon: '📘', limit: 500 },
    { id: 'twitter', name: 'Twitter/X', icon: '🐦', limit: 280 },
    { id: 'linkedin', name: 'LinkedIn', icon: '💼', limit: 700 },
    { id: 'youtube', name: 'YouTube', icon: '📺', limit: 1000 }
  ];

  const tones = [
    { id: 'professional', name: 'Professional', desc: 'Business-focused, authoritative' },
    { id: 'casual', name: 'Casual', desc: 'Friendly, conversational' },
    { id: 'humorous', name: 'Humorous', desc: 'Funny, entertaining' },
    { id: 'inspirational', name: 'Inspirational', desc: 'Motivating, uplifting' },
    { id: 'educational', name: 'Educational', desc: 'Informative, teaching' }
  ];

  const handleGenerate = async () => {
    if (selectedPlatforms.length === 0) {
      toast.error('Please select at least one platform');
      return;
    }

    try {
      setIsGenerating(true);
      
      // Mock generated content - replace with actual API call
      const mockContent = [
        {
          id: Date.now(),
          text: `🚀 Exciting developments in ${selectedDomain === 'tech' ? 'AI technology' : selectedDomain} today! The future is looking bright with innovative solutions that will transform how we work and live. What are your thoughts on these emerging trends? \n\n#Innovation #Technology #Future`,
          domain: selectedDomain,
          platforms: selectedPlatforms,
          createdAt: new Date().toISOString(),
          performancePrediction: {
            score: Math.floor(Math.random() * 40) + 60,
            description: 'High engagement potential with trending hashtags'
          },
          tags: ['innovation', 'technology', 'future'],
          engagementPreview: {
            likes: Math.floor(Math.random() * 500) + 100,
            comments: Math.floor(Math.random() * 50) + 10,
            shares: Math.floor(Math.random() * 100) + 20
          }
        }
      ];
      
      setGeneratedContent(prev => [...mockContent, ...prev]);
      toast.success(`🎉 Generated ${mockContent.length} pieces of content!`);
      setCustomPrompt('');
      
    } catch (error) {
      console.error('Content generation failed:', error);
      toast.error('Failed to generate content: ' + error.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleCopy = async (content) => {
    try {
      await navigator.clipboard.writeText(content.text);
      toast.success('Content copied to clipboard!');
    } catch (error) {
      console.error('Failed to copy content:', error);
      toast.error('Failed to copy content');
    }
  };

  const handleEdit = (content) => {
    setEditingContent({ ...content });
  };

  const handleSaveEdit = async () => {
    try {
      setGeneratedContent(prev => 
        prev.map(item => item.id === editingContent.id ? editingContent : item)
      );
      setEditingContent(null);
      toast.success('Content updated successfully!');
    } catch (error) {
      console.error('Failed to update content:', error);
      toast.error('Failed to update content');
    }
  };

  const handleSchedulePost = async (content) => {
    try {
      toast.success('Content scheduled for posting!');
    } catch (error) {
      console.error('Failed to schedule post:', error);
      toast.error('Failed to schedule post');
    }
  };

  const handlePostNow = async (content) => {
    if (!window.confirm('Post this content immediately to selected platforms?')) {
      return;
    }

    try {
      toast.success('Content posted successfully!');
    } catch (error) {
      console.error('Failed to post content:', error);
      toast.error('Failed to post content');
    }
  };

  const getCharacterCount = (text, platform) => {
    const limit = platforms.find(p => p.id === platform)?.limit || 280;
    return { current: text.length, limit, remaining: limit - text.length };
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-6 text-white">
        <div className="flex items-center space-x-4 mb-4">
          <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
            <Bot className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">AI Content Generator</h1>
            <p className="text-purple-100">Create engaging posts with artificial intelligence</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4" />
              <span className="font-medium text-sm">AI-Powered</span>
            </div>
            <p className="text-xs text-purple-100 mt-1">Advanced language models</p>
          </div>
          <div className="bg-white/10 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4" />
              <span className="font-medium text-sm">Platform-Optimized</span>
            </div>
            <p className="text-xs text-purple-100 mt-1">Tailored for each platform</p>
          </div>
          <div className="bg-white/10 rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <TrendingUp className="w-4 h-4" />
              <span className="font-medium text-sm">Trend-Aware</span>
            </div>
            <p className="text-xs text-purple-100 mt-1">Incorporates trending topics</p>
          </div>
        </div>
      </div>

      {/* Generation Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">Generate New Content</h2>

        {/* Domain Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">Content Domain</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {domains.map((domain) => (
              <button
                key={domain.id}
                onClick={() => setSelectedDomain(domain.id)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  selectedDomain === domain.id
                    ? 'border-purple-500 bg-purple-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="text-2xl mb-2">{domain.icon}</div>
                <div className="text-sm font-medium text-gray-900">{domain.name}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Platform Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-3">Target Platforms</label>
          <div className="flex flex-wrap gap-3">
            {platforms.map((platform) => (
              <button
                key={platform.id}
                onClick={() => {
                  setSelectedPlatforms(prev =>
                    prev.includes(platform.id)
                      ? prev.filter(p => p !== platform.id)
                      : [...prev, platform.id]
                  );
                }}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg border-2 transition-all ${
                  selectedPlatforms.includes(platform.id)
                    ? 'border-purple-500 bg-purple-50 text-purple-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <span>{platform.icon}</span>
                <span className="font-medium">{platform.name}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Custom Prompt */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Custom Prompt (Optional)
            <span className="text-gray-500 font-normal"> - Guide the AI with specific instructions</span>
          </label>
          <textarea
            value={customPrompt}
            onChange={(e) => setCustomPrompt(e.target.value)}
            placeholder="e.g., 'Create a post about the latest iPhone features focusing on camera improvements' or 'Write a motivational Monday post for entrepreneurs'"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
            rows="3"
          />
        </div>

        {/* Generation Settings */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Tone</label>
            <select
              value={generationSettings.tone}
              onChange={(e) => setGenerationSettings(prev => ({ ...prev, tone: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              {tones.map((tone) => (
                <option key={tone.id} value={tone.id}>
                  {tone.name} - {tone.desc}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Content Length</label>
            <select
              value={generationSettings.length}
              onChange={(e) => setGenerationSettings(prev => ({ ...prev, length: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
            >
              <option value="short">Short - Concise and punchy</option>
              <option value="medium">Medium - Balanced detail</option>
              <option value="long">Long - Detailed and comprehensive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Creativity: {generationSettings.creativityLevel}%
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={generationSettings.creativityLevel}
              onChange={(e) => setGenerationSettings(prev => ({ ...prev, creativityLevel: parseInt(e.target.value) }))}
              className="w-full"
            />
            <div className="text-xs text-gray-500 mt-1">Higher = more creative and unique</div>
          </div>
        </div>

        {/* Additional Options */}
        <div className="mb-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={generationSettings.includeHashtags}
                onChange={(e) => setGenerationSettings(prev => ({ ...prev, includeHashtags: e.target.checked }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Include Hashtags</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={generationSettings.includeEmojis}
                onChange={(e) => setGenerationSettings(prev => ({ ...prev, includeEmojis: e.target.checked }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Include Emojis</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={generationSettings.followTrends}
                onChange={(e) => setGenerationSettings(prev => ({ ...prev, followTrends: e.target.checked }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Follow Trends</span>
            </label>

            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={generationSettings.generateImage}
                onChange={(e) => setGenerationSettings(prev => ({ ...prev, generateImage: e.target.checked }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Generate Image</span>
            </label>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={isGenerating || selectedPlatforms.length === 0}
          className={`w-full flex items-center justify-center space-x-3 py-4 px-6 rounded-lg font-medium transition-colors ${
            isGenerating || selectedPlatforms.length === 0
              ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white'
          }`}
        >
          {isGenerating ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>AI is creating your content...</span>
            </>
          ) : (
            <>
              <Wand2 className="w-5 h-5" />
              <span>Generate Content with AI</span>
              <Sparkles className="w-5 h-5" />
            </>
          )}
        </button>
      </div>

      {/* Generated Content */}
      {generatedContent.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Generated Content</h2>
            <button
              onClick={() => setGeneratedContent([])}
              className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
            >
              <RefreshCw className="w-4 h-4" />
              <span className="text-sm">Clear All</span>
            </button>
          </div>

          <div className="space-y-6">
            {generatedContent.map((content) => (
              <div key={content.id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                {/* Content Header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="flex space-x-1">
                      {content.platforms.map((platform) => (
                        <span
                          key={platform}
                          className="text-xs px-2 py-1 bg-gray-100 rounded-full"
                        >
                          {platforms.find(p => p.id === platform)?.icon} {platforms.find(p => p.id === platform)?.name}
                        </span>
                      ))}
                    </div>
                    <div className="flex items-center space-x-2">
                      <Bot className="w-4 h-4 text-purple-600" />
                      <span className="text-sm text-purple-600 font-medium">
                        {domains.find(d => d.id === content.domain)?.name}
                      </span>
                    </div>
                  </div>
                  
                  <div className="text-sm text-gray-500">
                    {new Date(content.createdAt).toLocaleString()}
                  </div>
                </div>

                {/* Content Text */}
                <div className="mb-4">
                  {editingContent && editingContent.id === content.id ? (
                    <div className="space-y-3">
                      <textarea
                        value={editingContent.text}
                        onChange={(e) => setEditingContent(prev => ({ ...prev, text: e.target.value }))}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                        rows="4"
                      />
                      <div className="flex items-center justify-between">
                        <div className="text-sm text-gray-600">
                          Characters: {editingContent.text.length}
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={() => setEditingContent(null)}
                            className="px-3 py-1 text-gray-600 hover:text-gray-800"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={handleSaveEdit}
                            className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700"
                          >
                            Save
                          </button>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="bg-gray-50 rounded-lg p-4">
                      <p className="text-gray-900 whitespace-pre-wrap">{content.text}</p>
                    </div>
                  )}
                </div>

                {/* Performance Prediction */}
                {content.performancePrediction && (
                  <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Brain className="w-4 h-4 text-blue-600" />
                        <span className="text-sm font-medium text-blue-800">AI Performance Prediction</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 h-2 bg-blue-200 rounded-full">
                          <div 
                            className="h-2 bg-blue-500 rounded-full"
                            style={{ width: `${content.performancePrediction.score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-semibold text-blue-800">
                          {content.performancePrediction.score}/100
                        </span>
                      </div>
                    </div>
                    <p className="text-xs text-blue-700 mt-1">
                      {content.performancePrediction.description}
                    </p>
                  </div>
                )}

                {/* Action Buttons */}
                <div className="flex items-center justify-between">
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleCopy(content)}
                      className="flex items-center space-x-1 px-3 py-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <Copy className="w-4 h-4" />
                      <span className="text-sm">Copy</span>
                    </button>

                    <button
                      onClick={() => handleEdit(content)}
                      className="flex items-center space-x-1 px-3 py-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                    >
                      <Edit3 className="w-4 h-4" />
                      <span className="text-sm">Edit</span>
                    </button>
                  </div>

                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleSchedulePost(content)}
                      className="flex items-center space-x-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      <Calendar className="w-4 h-4" />
                      <span className="text-sm">Schedule</span>
                    </button>

                    <button
                      onClick={() => handlePostNow(content)}
                      className="flex items-center space-x-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      <Send className="w-4 h-4" />
                      <span className="text-sm">Post Now</span>
                    </button>
                  </div>
                </div>

                {/* Engagement Preview */}
                {content.engagementPreview && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center justify-between text-sm text-gray-600">
                      <div className="flex items-center space-x-4">
                        <div className="flex items-center space-x-1">
                          <Heart className="w-4 h-4" />
                          <span>~{content.engagementPreview.likes} likes</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <MessageCircle className="w-4 h-4" />
                          <span>~{content.engagementPreview.comments} comments</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Share2 className="w-4 h-4" />
                          <span>~{content.engagementPreview.shares} shares</span>
                        </div>
                      </div>
                      <span className="text-xs text-gray-500">Predicted engagement</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {generatedContent.length === 0 && !isGenerating && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
          <Bot className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-gray-900 mb-2">No content generated yet</h3>
          <p className="text-gray-600 mb-6">
            Select a domain and platforms above, then click "Generate Content with AI" to create your first posts!
          </p>
          <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
            <Sparkles className="w-4 h-4" />
            <span>AI will create engaging, platform-optimized content for you</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ContentGenerator;