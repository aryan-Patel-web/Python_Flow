import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, ArrowLeft, Search, Filter, CheckCircle, Star, TrendingUp, Users, Eye, Sparkles } from 'lucide-react'
import Button from '../../components/common/Button'
import DomainCard from '../../components/domains/DomainCard'
import { useAuth } from '../../context/AuthContext'
import useDomains from '../../hooks/useDomains'
import useToast from '../../hooks/useToast'

const DomainSetup = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { availableDomains, selectedDomains, updateSelection, loading } = useDomains()
  const { success, error: showError } = useToast()
  
  const [searchQuery, setSearchQuery] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [selectedDomainIds, setSelectedDomainIds] = useState([])
  const [showPreview, setShowPreview] = useState(null)

  // Mock available domains data
  const mockDomains = [
    {
      id: 'memes',
      name: 'Memes & Humor',
      category: 'Entertainment',
      icon: '😂',
      color: '#FF6B6B',
      description: 'Funny memes, jokes, and humorous content that engages your audience',
      popularity: 'high',
      stats: { avgEngagement: '12.5%', postsPerWeek: '15', difficulty: 'Easy' },
      tags: ['funny', 'viral', 'entertainment', 'social'],
      bestPlatforms: ['Instagram', 'Facebook', 'Twitter'],
      isPremium: false,
      examples: [
        { text: "When you finally understand a programming concept after 5 hours... 🎉", platform: "Instagram" },
        { text: "Me: I'll just check social media for 5 minutes. Also me: *3 hours later*", platform: "Twitter" }
      ]
    },
    {
      id: 'tech-news',
      name: 'Tech News',
      category: 'Technology',
      icon: '💻',
      color: '#4ECDC4',
      description: 'Latest technology news, gadget reviews, and industry updates',
      popularity: 'high',
      stats: { avgEngagement: '8.7%', postsPerWeek: '12', difficulty: 'Medium' },
      tags: ['technology', 'news', 'gadgets', 'innovation'],
      bestPlatforms: ['LinkedIn', 'Twitter', 'Facebook'],
      isPremium: false,
      examples: [
        { text: "🚀 Breaking: New AI breakthrough promises 10x faster processing speeds", platform: "LinkedIn" },
        { text: "The future of work is here: How AI is transforming industries", platform: "Twitter" }
      ]
    },
    {
      id: 'business-tips',
      name: 'Business Tips',
      category: 'Business',
      icon: '💼',
      color: '#45B7D1',
      description: 'Entrepreneurship advice, business strategies, and success tips',
      popularity: 'medium',
      stats: { avgEngagement: '6.8%', postsPerWeek: '10', difficulty: 'Medium' },
      tags: ['business', 'entrepreneurship', 'success', 'tips'],
      bestPlatforms: ['LinkedIn', 'Facebook', 'Instagram'],
      isPremium: false,
      examples: [
        { text: "💡 5 productivity hacks that transformed my business in 2024", platform: "LinkedIn" },
        { text: "The #1 mistake new entrepreneurs make (and how to avoid it)", platform: "Facebook" }
      ]
    },
    {
      id: 'coding-tips',
      name: 'Coding & Programming',
      category: 'Technology',
      icon: '⌨️',
      color: '#96CEB4',
      description: 'Programming tutorials, coding tips, and developer resources',
      popularity: 'medium',
      stats: { avgEngagement: '9.2%', postsPerWeek: '8', difficulty: 'Hard' },
      tags: ['programming', 'coding', 'development', 'tech'],
      bestPlatforms: ['LinkedIn', 'Twitter', 'YouTube'],
      isPremium: true,
      examples: [
        { text: "🔥 Clean Code Tip: Always name your variables like you're explaining to your future self", platform: "Twitter" },
        { text: "Why every developer should learn these 3 design patterns in 2024", platform: "LinkedIn" }
      ]
    },
    {
      id: 'lifestyle',
      name: 'Lifestyle & Wellness',
      category: 'Lifestyle',
      icon: '🌿',
      color: '#FECA57',
      description: 'Health tips, wellness advice, and lifestyle inspiration',
      popularity: 'high',
      stats: { avgEngagement: '11.3%', postsPerWeek: '14', difficulty: 'Easy' },
      tags: ['health', 'wellness', 'lifestyle', 'inspiration'],
      bestPlatforms: ['Instagram', 'Pinterest', 'Facebook'],
      isPremium: false,
      examples: [
        { text: "🌅 Morning routine that changed my life: 5 simple habits for better days", platform: "Instagram" },
        { text: "Self-care isn't selfish: Why putting yourself first makes you a better person", platform: "Facebook" }
      ]
    },
    {
      id: 'motivation',
      name: 'Motivational Content',
      category: 'Inspiration',
      icon: '✨',
      color: '#FF9FF3',
      description: 'Inspiring quotes, motivational content, and personal development',
      popularity: 'high',
      stats: { avgEngagement: '13.1%', postsPerWeek: '20', difficulty: 'Easy' },
      tags: ['motivation', 'inspiration', 'quotes', 'personal-development'],
      bestPlatforms: ['Instagram', 'LinkedIn', 'Facebook'],
      isPremium: false,
      examples: [
        { text: "'Success is not final, failure is not fatal: it is the courage to continue that counts.' - Winston Churchill", platform: "Instagram" },
        { text: "Your only limit is the one you set for yourself. Break through it today! 💪", platform: "Facebook" }
      ]
    }
  ]

  const categories = ['all', ...new Set(mockDomains.map(d => d.category))]

  useEffect(() => {
    // Initialize with already selected domains if any
    if (selectedDomains.length > 0) {
      setSelectedDomainIds(selectedDomains.map(d => d.id))
    }
  }, [selectedDomains])

  const filteredDomains = mockDomains.filter(domain => {
    const matchesSearch = domain.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         domain.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         domain.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    
    const matchesCategory = categoryFilter === 'all' || domain.category === categoryFilter
    
    return matchesSearch && matchesCategory
  })

  const handleDomainSelect = (domainId, isSelected) => {
    if (isSelected) {
      if (selectedDomainIds.length >= 5) {
        showError('You can select up to 5 content domains for optimal performance')
        return
      }
      setSelectedDomainIds(prev => [...prev, domainId])
    } else {
      setSelectedDomainIds(prev => prev.filter(id => id !== domainId))
    }
  }

  const handlePreview = (domain) => {
    setShowPreview(domain)
  }

  const handleContinue = async () => {
    if (selectedDomainIds.length === 0) {
      showError('Please select at least one content domain to continue')
      return
    }

    try {
      await updateSelection(selectedDomainIds)
      success(`Selected ${selectedDomainIds.length} content domain(s)! Almost done!`)
      navigate('/onboarding/complete')
    } catch (error) {
      showError('Failed to save domain selection')
    }
  }

  const handleBack = () => {
    navigate('/onboarding/credentials-setup')
  }

  const handleQuickSelect = (type) => {
    let recommendations = []
    
    switch (type) {
      case 'beginner':
        recommendations = ['memes', 'motivation', 'lifestyle']
        break
      case 'business':
        recommendations = ['business-tips', 'tech-news', 'motivation']
        break
      case 'creator':
        recommendations = ['memes', 'lifestyle', 'motivation', 'tech-news']
        break
      default:
        recommendations = []
    }
    
    setSelectedDomainIds(recommendations)
    success(`Selected ${type} recommended domains!`)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Choose Your Content Domains</h1>
              <p className="text-gray-600">Select the types of content you want AI to create for you</p>
            </div>
            <div className="text-sm text-gray-500">
              Step 3 of 4
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Selection */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <h3 className="font-semibold text-gray-900 mb-4">🚀 Quick Start Recommendations</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <button
              onClick={() => handleQuickSelect('beginner')}
              className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
            >
              <div className="font-medium text-gray-900 mb-2">👋 First Timer</div>
              <div className="text-sm text-gray-600 mb-3">Perfect for getting started with high-engagement content</div>
              <div className="text-xs text-blue-600">Memes, Motivation, Lifestyle</div>
            </button>
            
            <button
              onClick={() => handleQuickSelect('business')}
              className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
            >
              <div className="font-medium text-gray-900 mb-2">💼 Professional</div>
              <div className="text-sm text-gray-600 mb-3">Build authority and thought leadership</div>
              <div className="text-xs text-blue-600">Business Tips, Tech News, Motivation</div>
            </button>
            
            <button
              onClick={() => handleQuickSelect('creator')}
              className="p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
            >
              <div className="font-medium text-gray-900 mb-2">🎨 Content Creator</div>
              <div className="text-sm text-gray-600 mb-3">Diverse content for maximum reach</div>
              <div className="text-xs text-blue-600">Mixed content types</div>
            </button>
          </div>
        </div>

        {/* Selection Summary */}
        {selectedDomainIds.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-semibold text-green-900">
                  ✓ {selectedDomainIds.length} domain(s) selected
                </h3>
                <p className="text-green-700 text-sm">
                  AI will create content for: {selectedDomainIds.map(id => 
                    mockDomains.find(d => d.id === id)?.name
                  ).join(', ')}
                </p>
              </div>
              <Sparkles className="w-6 h-6 text-green-600" />
            </div>
          </div>
        )}

        {/* Filters */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0">
            <div className="flex-1 lg:mr-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search content domains..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <Filter className="w-4 h-4 text-gray-400" />
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category === 'all' ? 'All Categories' : category}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* Domains Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {filteredDomains.map((domain) => (
            <DomainCard
              key={domain.id}
              domain={domain}
              isSelected={selectedDomainIds.includes(domain.id)}
              onSelect={handleDomainSelect}
              onPreview={handlePreview}
            />
          ))}
        </div>

        {filteredDomains.length === 0 && (
          <div className="text-center py-12">
            <div className="text-gray-400 text-6xl mb-4">🔍</div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No domains found</h3>
            <p className="text-gray-600">Try adjusting your search or filter criteria</p>
          </div>
        )}

        {/* Content Strategy Tips */}
        <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-4">💡 Content Strategy Tips</h3>
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div>
              <h4 className="font-medium text-gray-800 mb-2">🎯 For Maximum Engagement:</h4>
              <ul className="text-gray-600 space-y-1">
                <li>• Mix entertainment (memes) with value (tips)</li>
                <li>• Include motivational content for emotional connection</li>
                <li>• Keep variety to avoid audience fatigue</li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium text-gray-800 mb-2">📈 For Building Authority:</h4>
              <ul className="text-gray-600 space-y-1">
                <li>• Focus on your expertise area (tech, business, etc.)</li>
                <li>• Add educational and news content</li>
                <li>• Balance professional with personal touches</li>
              </ul>
            </div>
          </div>
        </div>

        {/* AI Preview */}
        {selectedDomainIds.length > 0 && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
            <h3 className="font-semibold text-gray-900 mb-4">🤖 AI Content Preview</h3>
            <p className="text-gray-600 mb-4">
              Here's what AI will create for your selected domains:
            </p>
            <div className="space-y-4">
              {selectedDomainIds.slice(0, 2).map(domainId => {
                const domain = mockDomains.find(d => d.id === domainId)
                const example = domain?.examples?.[0]
                return example ? (
                  <div key={domainId} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">{domain.icon}</span>
                      <span className="font-medium text-gray-900">{domain.name}</span>
                      <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                        {example.platform}
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm italic">"{example.text}"</p>
                  </div>
                ) : null
              })}
              {selectedDomainIds.length > 2 && (
                <div className="text-center text-gray-500 text-sm">
                  + {selectedDomainIds.length - 2} more content types...
                </div>
              )}
            </div>
          </div>
        )}

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <Button
            onClick={handleBack}
            variant="outline"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          <div className="flex space-x-4">
            <Button
              onClick={() => navigate('/onboarding/complete')}
              variant="outline"
            >
              Skip for now
            </Button>
            <Button
              onClick={handleContinue}
              disabled={selectedDomainIds.length === 0 || loading}
            >
              Continue ({selectedDomainIds.length} selected)
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-96 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <span className="text-2xl">{showPreview.icon}</span>
                  <h3 className="text-xl font-semibold text-gray-900">{showPreview.name}</h3>
                </div>
                <button
                  onClick={() => setShowPreview(null)}
                  className="text-gray-400 hover:text-gray-600 text-xl"
                >
                  ×
                </button>
              </div>
              
              <div className="space-y-4">
                <p className="text-gray-600">{showPreview.description}</p>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <h4 className="font-medium text-gray-900 mb-3">Sample Content:</h4>
                  <div className="space-y-3">
                    {showPreview.examples?.map((example, index) => (
                      <div key={index} className="bg-white rounded-lg p-3 border border-gray-200">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                            {example.platform}
                          </span>
                        </div>
                        <p className="text-sm text-gray-700 italic">"{example.text}"</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-3 gap-4 text-center text-sm">
                  <div>
                    <div className="font-semibold text-gray-900">{showPreview.stats.avgEngagement}</div>
                    <div className="text-gray-600">Avg Engagement</div>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{showPreview.stats.postsPerWeek}</div>
                    <div className="text-gray-600">Posts/Week</div>
                  </div>
                  <div>
                    <div className="font-semibold text-gray-900">{showPreview.stats.difficulty}</div>
                    <div className="text-gray-600">Difficulty</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DomainSetup