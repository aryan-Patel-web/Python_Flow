import { useState } from 'react'
import { 
  Instagram, 
  Facebook, 
  Linkedin, 
  Youtube, 
  Twitter,
  Heart,
  MessageCircle,
  Share2,
  Eye,
  ExternalLink,
  MoreHorizontal
} from 'lucide-react'

const RecentPosts = ({ posts = [] }) => {
  const [activeFilter, setActiveFilter] = useState('all')

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
      Instagram: 'text-pink-600 bg-pink-50',
      Facebook: 'text-blue-600 bg-blue-50',
      LinkedIn: 'text-blue-700 bg-blue-50',
      YouTube: 'text-red-600 bg-red-50',
      Twitter: 'text-sky-600 bg-sky-50',
    }
    return colors[platform] || 'text-gray-600 bg-gray-50'
  }

  const getStatusColor = (status) => {
    const colors = {
      published: 'text-green-700 bg-green-50 border-green-200',
      scheduled: 'text-yellow-700 bg-yellow-50 border-yellow-200',
      draft: 'text-gray-700 bg-gray-50 border-gray-200',
      failed: 'text-red-700 bg-red-50 border-red-200',
    }
    return colors[status] || 'text-gray-700 bg-gray-50 border-gray-200'
  }

  const mockPosts = posts.length > 0 ? posts : [
    {
      id: 1,
      platform: 'Instagram',
      title: 'Funny programming meme',
      content: 'When you finally fix a bug that\'s been bothering you for days... 😅',
      image: '/api/placeholder/400/300',
      status: 'published',
      engagement: { likes: 124, comments: 8, shares: 12, views: 450 },
      publishedAt: '2 hours ago',
      type: 'image'
    },
    {
      id: 2,
      platform: 'LinkedIn',
      title: 'Tech industry insights',
      content: 'The future of AI in software development: 5 trends to watch in 2024',
      status: 'published',
      engagement: { likes: 89, comments: 15, shares: 23, views: 567 },
      publishedAt: '4 hours ago',
      type: 'article'
    },
    {
      id: 3,
      platform: 'Facebook',
      title: 'Business growth tips',
      content: 'How small businesses can leverage social media automation to scale faster',
      status: 'scheduled',
      engagement: { likes: 0, comments: 0, shares: 0, views: 0 },
      publishedAt: 'in 2 hours',
      type: 'text'
    },
    {
      id: 4,
      platform: 'YouTube',
      title: 'Tutorial: React Hooks',
      content: 'Complete guide to React Hooks - useState, useEffect, and custom hooks',
      thumbnail: '/api/placeholder/300/200',
      status: 'published',
      engagement: { likes: 45, comments: 12, shares: 8, views: 234 },
      publishedAt: '1 day ago',
      type: 'video'
    },
    {
      id: 5,
      platform: 'Twitter',
      title: 'Quick coding tip',
      content: '💡 Pro tip: Use console.table() instead of console.log() for better array/object debugging in JavaScript!',
      status: 'published',
      engagement: { likes: 67, comments: 5, shares: 18, views: 123 },
      publishedAt: '6 hours ago',
      type: 'text'
    }
  ]

  const platforms = ['all', 'Instagram', 'Facebook', 'LinkedIn', 'YouTube', 'Twitter']
  
  const filteredPosts = activeFilter === 'all' 
    ? mockPosts 
    : mockPosts.filter(post => post.platform === activeFilter)

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Recent Posts</h3>
            <p className="text-sm text-gray-500">Latest content across all platforms</p>
          </div>
          <button className="text-sm text-blue-600 hover:text-blue-500 font-medium">
            View All
          </button>
        </div>

        {/* Platform Filter */}
        <div className="flex space-x-2 mt-4">
          {platforms.map((platform) => (
            <button
              key={platform}
              onClick={() => setActiveFilter(platform)}
              className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                activeFilter === platform
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {platform === 'all' ? 'All Platforms' : platform}
            </button>
          ))}
        </div>
      </div>

      <div className="p-6">
        <div className="space-y-4">
          {filteredPosts.map((post) => {
            const PlatformIcon = getPlatformIcon(post.platform)
            return (
              <div key={post.id} className="flex items-start space-x-4 p-4 border border-gray-100 rounded-lg hover:bg-gray-50 transition-colors">
                {/* Platform Icon */}
                <div className={`flex-shrink-0 w-10 h-10 rounded-lg flex items-center justify-center ${getPlatformColor(post.platform)}`}>
                  <PlatformIcon className="w-5 h-5" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <h4 className="text-sm font-medium text-gray-900 truncate">
                        {post.title}
                      </h4>
                      <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(post.status)}`}>
                        {post.status}
                      </span>
                    </div>
                    <button className="flex-shrink-0 p-1 text-gray-400 hover:text-gray-600">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </div>

                  <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                    {post.content}
                  </p>

                  {/* Engagement Stats */}
                  {post.status === 'published' && (
                    <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                      <div className="flex items-center space-x-1">
                        <Heart className="w-3 h-3" />
                        <span>{post.engagement.likes}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <MessageCircle className="w-3 h-3" />
                        <span>{post.engagement.comments}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Share2 className="w-3 h-3" />
                        <span>{post.engagement.shares}</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Eye className="w-3 h-3" />
                        <span>{post.engagement.views}</span>
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between mt-3">
                    <span className="text-xs text-gray-500">
                      {post.status === 'scheduled' ? 'Scheduled ' : 'Posted '}
                      {post.publishedAt}
                    </span>
                    <button className="text-xs text-blue-600 hover:text-blue-500 flex items-center space-x-1">
                      <span>View post</span>
                      <ExternalLink className="w-3 h-3" />
                    </button>
                  </div>
                </div>

                {/* Thumbnail for video/image posts */}
                {(post.image || post.thumbnail) && (
                  <div className="flex-shrink-0">
                    <img
                      src={post.image || post.thumbnail}
                      alt={post.title}
                      className="w-16 h-16 rounded-lg object-cover"
                    />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {filteredPosts.length === 0 && (
          <div className="text-center py-8">
            <div className="text-gray-400 mb-2">
              <FileText className="w-12 h-12 mx-auto" />
            </div>
            <p className="text-gray-500">No posts found for {activeFilter === 'all' ? 'any platform' : activeFilter}</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default RecentPosts