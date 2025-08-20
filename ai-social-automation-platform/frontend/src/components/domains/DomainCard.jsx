import { useState } from 'react'
import { Check, Settings, TrendingUp, Users, Eye, Star } from 'lucide-react'
import Button from '../common/Button'

const DomainCard = ({ domain, isSelected, onSelect, onPreview }) => {
  const [showDetails, setShowDetails] = useState(false)
  
  const handleSelect = () => {
    onSelect(domain.id, !isSelected)
  }
  
  const getPopularityIcon = (level) => {
    switch (level) {
      case 'high': return <TrendingUp className="w-4 h-4 text-green-600" />
      case 'medium': return <Users className="w-4 h-4 text-yellow-600" />
      case 'low': return <Eye className="w-4 h-4 text-blue-600" />
      default: return <Star className="w-4 h-4 text-gray-400" />
    }
  }
  
  const getPopularityText = (level) => {
    switch (level) {
      case 'high': return 'High Engagement'
      case 'medium': return 'Medium Engagement'
      case 'low': return 'Growing Audience'
      default: return 'New Domain'
    }
  }
  
  const getPopularityColor = (level) => {
    switch (level) {
      case 'high': return 'text-green-600 bg-green-50 border-green-200'
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200'
      case 'low': return 'text-blue-600 bg-blue-50 border-blue-200'
      default: return 'text-gray-600 bg-gray-50 border-gray-200'
    }
  }
  
  const getDifficultyColor = (difficulty) => {
    switch (difficulty?.toLowerCase()) {
      case 'easy': return 'text-green-600'
      case 'medium': return 'text-yellow-600'
      case 'hard': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }
  
  return (
    <div className={`relative bg-white rounded-xl border-2 transition-all duration-200 cursor-pointer hover:shadow-md ${
      isSelected 
        ? 'border-blue-500 bg-blue-50' 
        : 'border-gray-200 hover:border-gray-300'
    }`}>
      {/* Selection Overlay */}
      {isSelected && (
        <div className="absolute top-3 right-3 w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center z-10">
          <Check className="w-4 h-4 text-white" />
        </div>
      )}
      
      {/* Card Content */}
      <div className="p-6" onClick={handleSelect}>
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center space-x-3">
            <div 
              className="w-12 h-12 rounded-lg flex items-center justify-center text-2xl"
              style={{ backgroundColor: `${domain.color || '#3B82F6'}20` }}
            >
              {domain.icon || '📝'}
            </div>
            <div>
              <h3 className="font-semibold text-gray-900">{domain.name}</h3>
              <p className="text-sm text-gray-600">{domain.category}</p>
            </div>
          </div>
          
          {/* Popularity Badge */}
          <div className={`px-2 py-1 rounded-full border text-xs font-medium flex items-center space-x-1 ${
            getPopularityColor(domain.popularity)
          }`}>
            {getPopularityIcon(domain.popularity)}
            <span>{getPopularityText(domain.popularity)}</span>
          </div>
        </div>
        
        {/* Description */}
        <p className="text-sm text-gray-600 mb-4 line-clamp-2">
          {domain.description}
        </p>
        
        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {domain.stats?.avgEngagement || '8.2%'}
            </div>
            <div className="text-xs text-gray-500">Avg Engagement</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-900">
              {domain.stats?.postsPerWeek || '12'}
            </div>
            <div className="text-xs text-gray-500">Posts/Week</div>
          </div>
          <div className="text-center">
            <div className={`text-lg font-semibold ${getDifficultyColor(domain.stats?.difficulty)}`}>
              {domain.stats?.difficulty || 'Easy'}
            </div>
            <div className="text-xs text-gray-500">Difficulty</div>
          </div>
        </div>
        
        {/* Tags */}
        <div className="flex flex-wrap gap-1 mb-4">
          {domain.tags?.slice(0, 3).map((tag, index) => (
            <span 
              key={index}
              className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full"
            >
              {tag}
            </span>
          ))}
          {domain.tags?.length > 3 && (
            <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
              +{domain.tags.length - 3} more
            </span>
          )}
        </div>
        
        {/* Platform Compatibility */}
        <div className="flex items-center space-x-2 mb-4">
          <span className="text-xs text-gray-500">Best for:</span>
          <div className="flex space-x-1">
            {domain.bestPlatforms?.map((platform, index) => (
              <span key={index} className="text-xs bg-blue-100 text-blue-600 px-2 py-1 rounded">
                {platform}
              </span>
            )) || (
              <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                All Platforms
              </span>
            )}
          </div>
        </div>
        
        {/* Examples */}
        {showDetails && (
          <div className="border-t pt-4 space-y-3">
            <h4 className="text-sm font-medium text-gray-900">Sample Content:</h4>
            <div className="space-y-2">
              {domain.examples?.map((example, index) => (
                <div key={index} className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-800">{example.text}</div>
                  <div className="flex items-center justify-between mt-1">
                    <span className="text-xs text-gray-500">
                      Platform: {example.platform}
                    </span>
                    <span className="text-xs text-green-600 font-medium">
                      Est. {example.engagement || '12%'} engagement
                    </span>
                  </div>
                </div>
              )) || (
                <div className="p-3 bg-gray-50 rounded-lg">
                  <div className="text-sm text-gray-800">
                    AI will generate relevant content for this domain based on current trends and your audience preferences.
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Sample content will be available after selection
                  </div>
                </div>
              )}
            </div>
            
            {/* Content Strategy */}
            {domain.strategy && (
              <div className="mt-3 p-3 bg-blue-50 rounded-lg">
                <h5 className="text-xs font-medium text-blue-900 mb-1">Content Strategy:</h5>
                <p className="text-xs text-blue-800">{domain.strategy}</p>
              </div>
            )}
          </div>
        )}
      </div>
      
      {/* Footer Actions */}
      <div className="px-6 pb-4 flex space-x-2">
        <Button
          variant="outline"
          size="sm"
          onClick={(e) => {
            e.stopPropagation()
            onPreview(domain)
          }}
          className="flex-1"
        >
          Preview Content
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={(e) => {
            e.stopPropagation()
            setShowDetails(!showDetails)
          }}
          className="px-3"
        >
          <Settings className="w-4 h-4" />
        </Button>
      </div>
      
      {/* Premium Badge */}
      {domain.isPremium && (
        <div className="absolute top-3 left-3 px-2 py-1 bg-gradient-to-r from-purple-500 to-pink-500 text-white text-xs font-medium rounded-full">
          ⭐ Premium
        </div>
      )}
      
      {/* Selection State Overlay */}
      {isSelected && (
        <div className="absolute inset-0 bg-blue-600 bg-opacity-5 rounded-xl pointer-events-none" />
      )}
      
      {/* Hover Effect */}
      <div className="absolute inset-0 bg-gradient-to-br from-transparent to-transparent hover:from-blue-50 hover:to-purple-50 rounded-xl pointer-events-none transition-all duration-300 opacity-0 hover:opacity-30" />
    </div>
  )
}

export default DomainCard