import { Instagram, Facebook, Linkedin, Youtube, Twitter, MoreHorizontal } from 'lucide-react'

const PlatformBreakdown = () => {
  const platforms = [
    {
      id: 'instagram',
      name: 'Instagram',
      icon: Instagram,
      color: '#E1306C',
      followers: 5234,
      posts: 18,
      engagement: 987,
      engagementRate: 4.2,
      growth: +12.5
    },
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: '#1877F2',
      followers: 3456,
      posts: 12,
      engagement: 654,
      engagementRate: 3.1,
      growth: +8.7
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: Linkedin,
      color: '#0A66C2',
      followers: 2198,
      posts: 8,
      engagement: 432,
      engagementRate: 5.8,
      growth: +15.3
    },
    {
      id: 'youtube',
      name: 'YouTube',
      icon: Youtube,
      color: '#FF0000',
      followers: 1876,
      posts: 4,
      engagement: 298,
      engagementRate: 2.9,
      growth: +6.2
    },
    {
      id: 'twitter',
      name: 'Twitter',
      icon: Twitter,
      color: '#1DA1F2',
      followers: 892,
      posts: 6,
      engagement: 156,
      engagementRate: 3.7,
      growth: -2.1
    }
  ]

  const formatNumber = (num) => {
    if (num >= 1000) {
      return `${(num / 1000).toFixed(1)}K`
    }
    return num.toString()
  }

  const getGrowthColor = (growth) => {
    return growth >= 0 ? 'text-green-600' : 'text-red-600'
  }

  const totalFollowers = platforms.reduce((sum, platform) => sum + platform.followers, 0)
  const totalEngagement = platforms.reduce((sum, platform) => sum + platform.engagement, 0)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Platform Breakdown</h3>
        <button className="text-sm text-blue-600 hover:text-blue-500 font-medium">
          View Details
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-gradient-to-r from-blue-50 to-blue-100 p-4 rounded-lg">
          <p className="text-sm text-blue-700 font-medium">Total Followers</p>
          <p className="text-2xl font-bold text-blue-900">{formatNumber(totalFollowers)}</p>
        </div>
        <div className="bg-gradient-to-r from-green-50 to-green-100 p-4 rounded-lg">
          <p className="text-sm text-green-700 font-medium">Total Engagement</p>
          <p className="text-2xl font-bold text-green-900">{formatNumber(totalEngagement)}</p>
        </div>
        <div className="bg-gradient-to-r from-purple-50 to-purple-100 p-4 rounded-lg">
          <p className="text-sm text-purple-700 font-medium">Active Platforms</p>
          <p className="text-2xl font-bold text-purple-900">{platforms.length}</p>
        </div>
      </div>

      {/* Platform List */}
      <div className="space-y-3">
        {platforms.map((platform) => {
          const Icon = platform.icon
          const followerPercentage = ((platform.followers / totalFollowers) * 100).toFixed(1)
          
          return (
            <div key={platform.id} className="bg-white p-4 rounded-lg border border-gray-200 hover:shadow-sm transition-shadow">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div 
                    className="w-10 h-10 rounded-lg flex items-center justify-center text-white"
                    style={{ backgroundColor: platform.color }}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900">{platform.name}</h4>
                    <p className="text-sm text-gray-500">
                      {formatNumber(platform.followers)} followers ({followerPercentage}%)
                    </p>
                  </div>
                </div>
                
                <div className="flex items-center space-x-6 text-sm">
                  <div className="text-center">
                    <p className="font-semibold text-gray-900">{platform.posts}</p>
                    <p className="text-gray-500">Posts</p>
                  </div>
                  
                  <div className="text-center">
                    <p className="font-semibold text-gray-900">{formatNumber(platform.engagement)}</p>
                    <p className="text-gray-500">Engagement</p>
                  </div>
                  
                  <div className="text-center">
                    <p className="font-semibold text-gray-900">{platform.engagementRate}%</p>
                    <p className="text-gray-500">Rate</p>
                  </div>
                  
                  <div className="text-center">
                    <p className={`font-semibold ${getGrowthColor(platform.growth)}`}>
                      {platform.growth >= 0 ? '+' : ''}{platform.growth}%
                    </p>
                    <p className="text-gray-500">Growth</p>
                  </div>
                  
                  <button className="p-1 text-gray-400 hover:text-gray-600">
                    <MoreHorizontal className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              {/* Progress bar for follower distribution */}
              <div className="mt-3">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className="h-2 rounded-full transition-all duration-300"
                    style={{ 
                      width: `${followerPercentage}%`,
                      backgroundColor: platform.color 
                    }}
                  ></div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* Performance Comparison */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-md font-semibold text-gray-900 mb-4">Performance Comparison</h4>
        <div className="space-y-4">
          {platforms.map((platform) => (
            <div key={`${platform.id}-performance`} className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div 
                  className="w-6 h-6 rounded-full flex items-center justify-center"
                  style={{ backgroundColor: platform.color }}
                >
                  <platform.icon className="w-3 h-3 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-900">{platform.name}</span>
              </div>
              
              <div className="flex items-center space-x-4 text-sm">
                <span className="text-gray-600">Engagement Rate:</span>
                <span className="font-semibold text-gray-900">{platform.engagementRate}%</span>
                <div className="w-20 bg-gray-200 rounded-full h-2">
                  <div 
                    className="h-2 rounded-full"
                    style={{ 
                      width: `${(platform.engagementRate / 6) * 100}%`,
                      backgroundColor: platform.color 
                    }}
                  ></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default PlatformBreakdown