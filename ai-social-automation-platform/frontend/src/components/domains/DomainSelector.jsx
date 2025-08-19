import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Filter, 
  Star, 
  TrendingUp, 
  Hash, 
  Clock, 
  Users,
  Zap,
  Check,
  Plus,
  Settings
} from 'lucide-react';

const DomainSelector = ({ onDomainSelect, selectedDomains = [], showSelectedOnly = false }) => {
  const [domains, setDomains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [sortBy, setSortBy] = useState('popularity');

  useEffect(() => {
    fetchDomains();
  }, []);

  const fetchDomains = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/domains', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDomains(data.domains || []);
      }
    } catch (error) {
      console.error('Error fetching domains:', error);
      // Set demo data
      setDomains([
        {
          id: 'memes',
          name: 'memes',
          display_name: 'Memes & Humor',
          description: 'Funny content, memes, and viral humor',
          category: 'entertainment',
          keywords: ['funny', 'meme', 'humor', 'viral', 'comedy'],
          hashtags: ['#memes', '#funny', '#humor', '#viral'],
          popularity_score: 95,
          usage_count: 1250,
          tone: 'funny',
          content_types: ['image', 'text', 'video'],
          target_audience: 'General audience'
        },
        {
          id: 'tech-news',
          name: 'tech_news',
          display_name: 'Tech News',
          description: 'Latest technology news and updates',
          category: 'technology',
          keywords: ['tech', 'technology', 'innovation', 'gadgets', 'AI'],
          hashtags: ['#tech', '#technology', '#innovation', '#AI'],
          popularity_score: 88,
          usage_count: 980,
          tone: 'professional',
          content_types: ['text', 'image'],
          target_audience: 'Tech enthusiasts'
        },
        {
          id: 'business-tips',
          name: 'business_tips',
          display_name: 'Business Tips',
          description: 'Entrepreneurship and business advice',
          category: 'business',
          keywords: ['business', 'entrepreneur', 'startup', 'marketing', 'growth'],
          hashtags: ['#business', '#entrepreneur', '#startup', '#marketing'],
          popularity_score: 82,
          usage_count: 765,
          tone: 'professional',
          content_types: ['text', 'image'],
          target_audience: 'Business professionals'
        },
        {
          id: 'lifestyle',
          name: 'lifestyle',
          display_name: 'Lifestyle & Wellness',
          description: 'Health, fitness, and lifestyle content',
          category: 'lifestyle',
          keywords: ['lifestyle', 'wellness', 'health', 'fitness', 'mindfulness'],
          hashtags: ['#lifestyle', '#wellness', '#health', '#fitness'],
          popularity_score: 76,
          usage_count: 642,
          tone: 'inspirational',
          content_types: ['text', 'image', 'video'],
          target_audience: 'Health-conscious individuals'
        },
        {
          id: 'coding-tips',
          name: 'coding_tips',
          display_name: 'Coding Tips',
          description: 'Programming tutorials and coding tips',
          category: 'education',
          keywords: ['coding', 'programming', 'development', 'tutorial', 'tips'],
          hashtags: ['#coding', '#programming', '#dev', '#tutorial'],
          popularity_score: 71,
          usage_count: 523,
          tone: 'educational',
          content_types: ['text', 'image'],
          target_audience: 'Developers and programmers'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const categories = [
    { value: 'all', label: 'All Categories', icon: '📱' },
    { value: 'entertainment', label: 'Entertainment', icon: '🎭' },
    { value: 'technology', label: 'Technology', icon: '💻' },
    { value: 'business', label: 'Business', icon: '💼' },
    { value: 'lifestyle', label: 'Lifestyle', icon: '🌿' },
    { value: 'education', label: 'Education', icon: '📚' },
    { value: 'news', label: 'News', icon: '📰' },
    { value: 'sports', label: 'Sports', icon: '⚽' },
    { value: 'health', label: 'Health', icon: '🏥' },
    { value: 'fashion', label: 'Fashion', icon: '👗' }
  ];

  const sortOptions = [
    { value: 'popularity', label: 'Most Popular' },
    { value: 'usage', label: 'Most Used' },
    { value: 'alphabetical', label: 'A-Z' },
    { value: 'recent', label: 'Recently Added' }
  ];

  const filteredDomains = domains
    .filter(domain => {
      if (showSelectedOnly) {
        return selectedDomains.includes(domain.id);
      }
      
      const matchesSearch = domain.display_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           domain.keywords.some(keyword => keyword.toLowerCase().includes(searchTerm.toLowerCase()));
      const matchesCategory = selectedCategory === 'all' || domain.category === selectedCategory;
      
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'popularity':
          return b.popularity_score - a.popularity_score;
        case 'usage':
          return b.usage_count - a.usage_count;
        case 'alphabetical':
          return a.display_name.localeCompare(b.display_name);
        default:
          return 0;
      }
    });

  const handleDomainToggle = (domain) => {
    const isSelected = selectedDomains.includes(domain.id);
    const newSelection = isSelected
      ? selectedDomains.filter(id => id !== domain.id)
      : [...selectedDomains, domain.id];
    
    onDomainSelect(newSelection, domain);
  };

  const getToneColor = (tone) => {
    const colors = {
      funny: 'bg-yellow-100 text-yellow-800',
      professional: 'bg-blue-100 text-blue-800',
      inspirational: 'bg-purple-100 text-purple-800',
      educational: 'bg-green-100 text-green-800',
      casual: 'bg-gray-100 text-gray-800'
    };
    return colors[tone] || colors.casual;
  };

  const getCategoryIcon = (category) => {
    const categoryData = categories.find(cat => cat.value === category);
    return categoryData?.icon || '📱';
  };

  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(6)].map((_, i) => (
          <div key={i} className="animate-pulse">
            <div className="border rounded-lg p-4">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                <div className="flex-1 space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-1/3"></div>
                  <div className="h-3 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Content Domains</h2>
          <p className="text-gray-600 mt-1">Choose content categories for AI generation</p>
        </div>
        <div className="text-sm text-gray-500">
          {selectedDomains.length} selected
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-4">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search domains..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* Category Filter */}
        <select
          value={selectedCategory}
          onChange={(e) => setSelectedCategory(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {categories.map(category => (
            <option key={category.value} value={category.value}>
              {category.icon} {category.label}
            </option>
          ))}
        </select>

        {/* Sort */}
        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          {sortOptions.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      </div>

      {/* Domain Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredDomains.map((domain) => {
          const isSelected = selectedDomains.includes(domain.id);
          
          return (
            <div
              key={domain.id}
              onClick={() => handleDomainToggle(domain)}
              className={`relative border-2 rounded-lg p-4 cursor-pointer transition-all hover:shadow-md ${
                isSelected
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {/* Selection Indicator */}
              <div className={`absolute top-3 right-3 w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                isSelected
                  ? 'border-blue-500 bg-blue-500'
                  : 'border-gray-300'
              }`}>
                {isSelected && <Check className="w-4 h-4 text-white" />}
              </div>

              {/* Domain Header */}
              <div className="flex items-start space-x-3 mb-3">
                <div className="text-2xl">
                  {getCategoryIcon(domain.category)}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold text-gray-900 truncate">
                    {domain.display_name}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                    {domain.description}
                  </p>
                </div>
              </div>

              {/* Tone & Stats */}
              <div className="flex items-center justify-between mb-3">
                <span className={`px-2 py-1 text-xs font-medium rounded-full ${getToneColor(domain.tone)}`}>
                  {domain.tone}
                </span>
                <div className="flex items-center space-x-2 text-xs text-gray-500">
                  <div className="flex items-center">
                    <TrendingUp className="w-3 h-3 mr-1" />
                    {domain.popularity_score}
                  </div>
                  <div className="flex items-center">
                    <Users className="w-3 h-3 mr-1" />
                    {domain.usage_count}
                  </div>
                </div>
              </div>

              {/* Keywords */}
              <div className="mb-3">
                <div className="flex flex-wrap gap-1">
                  {domain.keywords.slice(0, 3).map((keyword, index) => (
                    <span
                      key={index}
                      className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded"
                    >
                      {keyword}
                    </span>
                  ))}
                  {domain.keywords.length > 3 && (
                    <span className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded">
                      +{domain.keywords.length - 3}
                    </span>
                  )}
                </div>
              </div>

              {/* Content Types */}
              <div className="flex items-center justify-between text-xs text-gray-500">
                <div className="flex items-center space-x-1">
                  {domain.content_types.includes('text') && <span>📝</span>}
                  {domain.content_types.includes('image') && <span>🖼️</span>}
                  {domain.content_types.includes('video') && <span>🎥</span>}
                </div>
                <span>{domain.target_audience}</span>
              </div>

              {/* Hover Actions */}
              {isSelected && (
                <div className="absolute inset-0 bg-blue-500 bg-opacity-10 rounded-lg flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                  <div className="flex space-x-2">
                    <button className="p-2 bg-white rounded-full shadow-md hover:shadow-lg transition-shadow">
                      <Settings className="w-4 h-4 text-gray-600" />
                    </button>
                    <button className="p-2 bg-white rounded-full shadow-md hover:shadow-lg transition-shadow">
                      <Zap className="w-4 h-4 text-gray-600" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Empty State */}
      {filteredDomains.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <Search className="w-12 h-12 mx-auto" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No domains found</h3>
          <p className="text-gray-600">
            {searchTerm ? `No domains match "${searchTerm}"` : 'No domains available in this category'}
          </p>
        </div>
      )}

      {/* Selected Summary */}
      {selectedDomains.length > 0 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div>
              <h4 className="font-medium text-blue-900">
                {selectedDomains.length} Domain{selectedDomains.length === 1 ? '' : 's'} Selected
              </h4>
              <p className="text-sm text-blue-700">
                AI will generate content for these categories
              </p>
            </div>
            <button className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors">
              <Zap className="w-4 h-4 mr-2" />
              Generate Content
            </button>
          </div>
        </div>
      )}

      {/* Quick Add Suggestions */}
      <div className="border-t pt-6">
        <h4 className="font-medium text-gray-900 mb-3">Popular Combinations</h4>
        <div className="flex flex-wrap gap-2">
          {[
            { name: 'Social Media Starter', domains: ['memes', 'lifestyle'] },
            { name: 'Business Pro', domains: ['business-tips', 'tech-news'] },
            { name: 'Content Creator', domains: ['memes', 'lifestyle', 'tech-news'] }
          ].map((combo, index) => (
            <button
              key={index}
              onClick={() => onDomainSelect(combo.domains)}
              className="flex items-center px-3 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors text-sm"
            >
              <Plus className="w-4 h-4 mr-2" />
              {combo.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DomainSelector;