import { 
  Instagram, 
  Facebook, 
  Linkedin, 
  Youtube, 
  Twitter,
  CheckCircle,
  XCircle,
  AlertCircle,
  Settings,
  Plus
} from 'lucide-react'

const PlatformStatus = ({ platforms = [] }) => {
  const mockPlatforms = platforms.length > 0 ? platforms : [
    {
      platform: 'Instagram',
      status: 'connected',
      posts: 15,
      engagement: 450,
      lastPost: '2 hours ago',
      followers: 1200,
      growth: '+12%'
    },
    {
      platform: 'Facebook',
      status: 'connected',
      posts: 12,
      engagement: 320,
      lastPost: '4 hours ago',
      followers: 850,
      growth: '+8%'
    },
    {
      platform: 'LinkedIn',
      status: 'connected',
      posts: 8,
      engagement: 180,
      lastPost: '6 hours ago',
      followers: 650,
      growth: '+15%'
    },
    {
      platform: 'YouTube',
      status: 'connected',
      posts: 5,
      engagement: 250,
      lastPost: '1 day ago',
      followers: 420,
      growth: '+20%'
    },
    {
      platform: 'Twitter',
      status: 'disconnected',
      posts: 0,
      engagement: 0,
      lastPost: 'Never',
      followers: 0,
      growth: '0%'
    }
  ]

  const getPlatformIcon = (platform) => {
    const icons = {
      Instagram: Instagram,
      Facebook: Facebook,
      LinkedIn: Linkedin,
      YouTube: Youtube,
      Twitter: Twitter,
    }
    const Icon = icons[platform] || Instagram
    return Icon
  }

  const getPlatformColor = (platform) => {
    const colors = {
      Instagram: 'from-pink-500 to-purple-600',
      Facebook: 'from-blue-600 to-blue-700',
      LinkedIn: 'from-blue-700 to-blue-800',
      YouTube: 'from-red-600 to-red-700',
      Twitter: 'from-sky-500 to-sky-600',
    }
    return colors[platform] || 'from-gray-500 to-gray-600'
  }

  const getStatusInfo = (status) => {
    switch (status) {
      case 'connected':
        return {
          icon: CheckCircle,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
          text: 'Connected'
        }
      case 'disconnected':
        return {
          icon: XCircle,
          color: 'text-red-600',
          bgColor: 'bg-red-50',
          text: 'Disconnected'
        }
      case 'warning':
        return {
          icon: AlertCircle,
          color: 'text-yellow-600',
          bgColor: 'bg-yellow-50',
          text: 'Needs Attention'
        }
      default:
        return {
          icon: XCircle,
          color: 'text-gray-600',
          bgColor: 'bg-gray-50',
          text: 'Unknown'
        }
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Platform Status</h3>
            <p className="text-sm text-gray-500">Connected social media accounts</p>
          </div>
          <button className="flex items-center space-x-2 px-3 py-1.5 text-sm font-medium text-blue-600 hover:text-blue-500 border border-blue-200 rounded-lg hover:bg-blue-50 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Add Platform</span>
          </button>
        </div>
      </div>

      <div className="p-6">
        <div className="space-y-4">
          {mockPlatforms.map((platform) => {
            const PlatformIcon = getPlatformIcon(platform.platform)
            const statusInfo = getStatusInfo(platform.status)
            const StatusIcon = statusInfo.icon

            return (
              <div key={platform.platform} className="flex items-center justify-between p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                <div className="flex items-center space-x-4">
                  {/* Platform Icon */}
                  <div className={`w-12 h-12 rounded-lg bg-gradient-to-r ${getPlatformColor(platform.platform)} flex items-center justify-center`}>
                    <PlatformIcon className="w-6 h-6 text-white" />
                  </div>

                  {/* Platform Info */}
                  <div>
                    <div className="flex items-center space-x-2">
                      <h4 className="font-medium text-gray-900">{platform.platform}</h4>
                      <div className={`flex items-center space-x-1 px-2 py-0.5 rounded-full text-xs font-medium ${statusInfo.bgColor} ${statusInfo.color}`}>
                        <StatusIcon className="w-3 h-3" />
                        <span>{statusInfo.text}</span>
                      </div>
                    </div>
                    
                    {platform.status === 'connected' ? (
                      <div className="flex items-center space-x-4 text-sm text-gray-500 mt-1">
                        <span>{platform.followers} followers</span>
                        <span className="text-green-600">{platform.growth}</span>
                        <span>Last post: {platform.lastPost}</span>
                      </div>
                    ) : (
                      <p className="text-sm text-gray-500 mt-1">Connect to start posting</p>
                    )}
                  </div>
                </div>

                {/* Stats or Action */}
                <div className="flex items-center space-x-4">
                  {platform.status === 'connected' ? (
                    <div className="text-right">
                      <div className="grid grid-cols-2 gap-3 text-center">
                        <div>
                          <p className="text-lg font-semibold text-gray-900">{platform.posts}</p>
                          <p className="text-xs text-gray-500">Posts</p>
                        </div>
                        <div>
                          <p className="text-lg font-semibold text-blue-600">{platform.engagement}</p>
                          <p className="text-xs text-gray-500">Engagement</p>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
                      Connect
                    </button>
                  )}
                  
                  <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                    <Settings className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )
          })}
        </div>

        {/* Summary Stats */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold text-green-600">
                {mockPlatforms.filter(p => p.status === 'connected').length}
              </p>
              <p className="text-sm text-gray-500">Connected</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-blue-600">
                {mockPlatforms.reduce((sum, p) => sum + p.posts, 0)}
              </p>
              <p className="text-sm text-gray-500">Total Posts</p>
            </div>
            <div>
              <p className="text-2xl font-bold text-purple-600">
                {mockPlatforms.reduce((sum, p) => sum + p.engagement, 0)}
              </p>
              <p className="text-sm text-gray-500">Total Engagement</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PlatformStatus