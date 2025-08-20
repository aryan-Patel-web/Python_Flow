import { useState } from 'react'
import { 
  Target, 
  Laugh, 
  Code, 
  Briefcase, 
  Heart, 
  TrendingUp,
  Settings,
  Play,
  Pause,
  Clock,
  Check
} from 'lucide-react'

const DomainsPage = () => {
  const [selectedDomains, setSelectedDomains] = useState(['memes', 'tech'])
  const [postingSettings, setPostingSettings] = useState({
    frequency: 3,
    times: ['09:00', '14:00', '19:00']
  })

  const domains = [
    {
      id: 'memes',
      name: 'Memes & Humor',
      icon: Laugh,
      description: 'Funny memes, jokes, and humorous content',
      color: 'from-yellow-400 to-orange-500',
      examples: ['Programming memes', 'Relatable content', 'Trending jokes'],
      postsPerDay: 2,
      engagement: 'High'
    },
    {
      id: 'tech',
      name: 'Tech News',
      icon: Code,
      description: 'Latest technology news and updates',
      color: 'from-blue-500 to-purple-600',
      examples: ['AI developments', 'Software updates', 'Tech reviews'],
      postsPerDay: 1,
      engagement: 'Medium'
    },
    {
      id: 'business',
      name: 'Business Tips',
      icon: Briefcase,
      description: 'Business insights and entrepreneurship',
      color: 'from-green-500 to-teal-600',
      examples: ['Startup advice', 'Marketing tips', 'Success stories'],
      postsPerDay: 1,
      engagement: 'Medium'
    },
    {
      id: 'lifestyle',
      name: 'Lifestyle',
      icon: Heart,
      description: 'Health, wellness, and lifestyle content',
      color: 'from-pink-500 to-rose-600',
      examples: ['Wellness tips', 'Daily motivation', 'Life hacks'],
      postsPerDay: 2,
      engagement: 'High'
    },
    {
      id: 'finance',
      name: 'Finance & Investing',
      icon: TrendingUp,
      description: 'Financial advice and investment tips',
      color: 'from-emerald-500 to-green-600',
      examples: ['Investment strategies', 'Money management', 'Market insights'],
      postsPerDay: 1,
      engagement: 'Medium'
    }
  ]

  const handleDomainToggle = (domainId) => {
    setSelectedDomains(prev => 
      prev.includes(domainId)
        ? prev.filter(id => id !== domainId)
        : [...prev, domainId]
    )
  }

  const totalPostsPerDay = domains
    .filter(domain => selectedDomains.includes(domain.id))
    .reduce((sum, domain) => sum + domain.postsPerDay, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Content Domains
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Select content categories for AI to generate posts from
          </p>
        </div>
        <div className="mt-4 flex space-x-3 md:ml-4 md:mt-0">
          <button className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-green-600 rounded-lg hover:bg-green-700 transition-colors">
            <Play className="w-4 h-4" />
            <span>Start Automation</span>
          </button>
        </div>
      </div>

      {/* Current Settings Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Current Configuration</h3>
            <p className="text-sm text-gray-600 mt-1">
              {selectedDomains.length} domains selected • {totalPostsPerDay} posts per day
            </p>
          </div>
          <div className="flex items-center space-x-4 text-sm">
            <div className="text-center">
              <p className="text-2xl font-bold text-blue-600">{selectedDomains.length}</p>
              <p className="text-gray-500">Active Domains</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-green-600">{totalPostsPerDay}</p>
              <p className="text-gray-500">Posts/Day</p>
            </div>
            <div className="text-center">
              <p className="text-2xl font-bold text-purple-600">{postingSettings.times.length}</p>
              <p className="text-gray-500">Time Slots</p>
            </div>
          </div>
        </div>
      </div>

      {/* Domain Selection */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Content Domains</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {domains.map((domain) => {
            const Icon = domain.icon
            const isSelected = selectedDomains.includes(domain.id)
            
            return (
              <div 
                key={domain.id}
                className={`relative bg-white rounded-lg shadow-sm border-2 transition-all cursor-pointer ${
                  isSelected 
                    ? 'border-blue-500 ring-2 ring-blue-200' 
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleDomainToggle(domain.id)}
              >
                {/* Selection Indicator */}
                {isSelected && (
                  <div className="absolute top-3 right-3 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                    <Check className="w-4 h-4 text-white" />
                  </div>
                )}

                {/* Domain Header */}
                <div className={`h-20 bg-gradient-to-r ${domain.color} rounded-t-lg flex items-center justify-center`}>
                  <Icon className="w-8 h-8 text-white" />
                </div>

                {/* Domain Content */}
                <div className="p-6">
                  <h4 className="text-lg font-semibold text-gray-900 mb-2">{domain.name}</h4>
                  <p className="text-sm text-gray-600 mb-4">{domain.description}</p>

                  {/* Examples */}
                  <div className="mb-4">
                    <p className="text-xs font-medium text-gray-500 mb-2">CONTENT EXAMPLES:</p>
                    <div className="space-y-1">
                      {domain.examples.map((example, index) => (
                        <div key={index} className="text-xs text-gray-600 bg-gray-50 px-2 py-1 rounded">
                          {example}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="flex justify-between text-xs text-gray-500">
                    <span>{domain.postsPerDay} posts/day</span>
                    <span className={`font-medium ${
                      domain.engagement === 'High' ? 'text-green-600' : 'text-yellow-600'
                    }`}>
                      {domain.engagement} engagement
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Posting Schedule */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Posting Schedule</h3>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Frequency Setting */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Posts per day
            </label>
            <select 
              value={postingSettings.frequency}
              onChange={(e) => setPostingSettings(prev => ({...prev, frequency: parseInt(e.target.value)}))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              <option value={1}>1 post per day</option>
              <option value={2}>2 posts per day</option>
              <option value={3}>3 posts per day</option>
              <option value={4}>4 posts per day</option>
              <option value={5}>5 posts per day</option>
              <option value={6}>6 posts per day</option>
            </select>
          </div>

          {/* Time Slots */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Posting times
            </label>
            <div className="space-y-2">
              {postingSettings.times.map((time, index) => (
                <div key={index} className="flex items-center space-x-2">
                  <Clock className="w-4 h-4 text-gray-400" />
                  <input
                    type="time"
                    value={time}
                    onChange={(e) => {
                      const newTimes = [...postingSettings.times]
                      newTimes[index] = e.target.value
                      setPostingSettings(prev => ({...prev, times: newTimes}))
                    }}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Preview */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-medium text-gray-900 mb-2">Schedule Preview</h4>
          <p className="text-sm text-gray-600">
            AI will generate and post {totalPostsPerDay} pieces of content daily from your selected domains: {' '}
            <span className="font-medium">
              {domains.filter(d => selectedDomains.includes(d.id)).map(d => d.name).join(', ')}
            </span>
          </p>
          <div className="mt-2 flex flex-wrap gap-2">
            {postingSettings.times.map((time, index) => (
              <span key={index} className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                {time}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-3">
        <button className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
          Save Draft
        </button>
        <button className="px-6 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
          Save & Start Automation
        </button>
      </div>
    </div>
  )
}

export default DomainsPage