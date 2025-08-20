import { useState } from 'react'
import { 
  Search, 
  Filter, 
  Plus, 
  Download,
  Eye,
  Edit,
  Trash2,
  Instagram,
  Facebook,
  Linkedin,
  Youtube,
  Twitter,
  Image,
  FileText,
  Video,
  Calendar
} from 'lucide-react'

const ContentLibrary = () => {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState('all')
  const [filterPlatform, setFilterPlatform] = useState('all')

  const contentTypes = [
    { value: 'all', label: 'All Content' },
    { value: 'image', label: 'Images' },
    { value: 'text', label: 'Text Posts' },
    { value: 'video', label: 'Videos' }
  ]

  const platforms = [
    { value: 'all', label: 'All Platforms' },
    { value: 'Instagram', label: 'Instagram' },
    { value: 'Facebook', label: 'Facebook' },
    { value: 'LinkedIn', label: 'LinkedIn' },
    { value: 'YouTube', label: 'YouTube' },
    { value: 'Twitter', label: 'Twitter' }
  ]

  const mockContent = [
    {
      id: 1,
      title: 'Programming Meme: Debugging Life',
      content: 'When you fix one bug and create three more... 😅 #programming #developer #debugging',
      type: 'image',
      platform: 'Instagram',
      status: 'published',
      engagement: { likes: 234, comments: 12, shares: 18 },
      createdAt: '2024-01-15',
      publishedAt: '2024-01-16',
      image: '/api/placeholder/400/400'
    },
    {
      id: 2,
      title: 'AI Industry Report 2024',
      content: 'The latest trends in AI development show remarkable growth in automation tools. Companies are increasingly adopting AI-powered solutions...',
      type: 'text',
      platform: 'LinkedIn',
      status: 'published',
      engagement: { likes: 89, comments: 23, shares: 15 },
      createdAt: '2024-01-14',
      publishedAt: '2024-01-15'
    },
    {
      id: 3,
      title: 'React Hooks Tutorial',
      content: 'Master React Hooks in 10 minutes - Complete guide to useState, useEffect, and custom hooks',
      type: 'video',
      platform: 'YouTube',
      status: 'scheduled',
      engagement: { likes: 0, comments: 0, shares: 0 },
      createdAt: '2024-01-13',
      publishedAt: '2024-01-17',
      thumbnail: '/api/placeholder/300/200'
    },
    {
      id: 4,
      title: 'Business Growth Tip',
      content: '💡 Pro tip: Automate your social media posting to save 10+ hours per week while maintaining consistent engagement!',
      type: 'text',
      platform: 'Twitter',
      status: 'published',
      engagement: { likes: 156, comments: 8, shares: 42 },
      createdAt: '2024-01-12',
      publishedAt: '2024-01-13'
    },
    {
      id: 5,
      title: 'Motivational Quote Design',
      content: 'Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill',
      type: 'image',
      platform: 'Facebook',
      status: 'draft',
      engagement: { likes: 0, comments: 0, shares: 0 },
      createdAt: '2024-01-11',
      image: '/api/placeholder/600/400'
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
    const Icon = icons[platform] || FileText
    return <Icon className="w-4 h-4" />
  }

  const getTypeIcon = (type) => {
    const icons = {
      image: Image,
      text: FileText,
      video: Video,
    }
    const Icon = icons[type] || FileText
    return <Icon className="w-4 h-4" />
  }

  const getStatusColor = (status) => {
    const colors = {
      published: 'text-green-700 bg-green-50 border-green-200',
      scheduled: 'text-yellow-700 bg-yellow-50 border-yellow-200',
      draft: 'text-gray-700 bg-gray-50 border-gray-200',
    }
    return colors[status] || 'text-gray-700 bg-gray-50 border-gray-200'
  }

  const filteredContent = mockContent.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.content.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = filterType === 'all' || item.type === filterType
    const matchesPlatform = filterPlatform === 'all' || item.platform === filterPlatform
    
    return matchesSearch && matchesType && matchesPlatform
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="md:flex md:items-center md:justify-between">
        <div className="min-w-0 flex-1">
          <h2 className="text-2xl font-bold leading-7 text-gray-900 sm:truncate sm:text-3xl">
            Content Library
          </h2>
          <p className="mt-1 text-sm text-gray-500">
            Manage all your AI-generated content across platforms
          </p>
        </div>
        <div className="mt-4 flex space-x-3 md:ml-4 md:mt-0">
          <button className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
            <Download className="w-4 h-4" />
            <span>Export</span>
          </button>
          <button className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors">
            <Plus className="w-4 h-4" />
            <span>Create Content</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          {/* Content Type Filter */}
          <div>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              {contentTypes.map(type => (
                <option key={type.value} value={type.value}>{type.label}</option>
              ))}
            </select>
          </div>

          {/* Platform Filter */}
          <div>
            <select
              value={filterPlatform}
              onChange={(e) => setFilterPlatform(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
            >
              {platforms.map(platform => (
                <option key={platform.value} value={platform.value}>{platform.label}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredContent.map((item) => (
          <div key={item.id} className="bg-white rounded-lg shadow-sm border overflow-hidden">
            {/* Content Preview */}
            {item.image && (
              <div className="aspect-video bg-gray-100">
                <img
                  src={item.image}
                  alt={item.title}
                  className="w-full h-full object-cover"
                />
              </div>
            )}
            {item.thumbnail && (
              <div className="aspect-video bg-gray-100 relative">
                <img
                  src={item.thumbnail}
                  alt={item.title}
                  className="w-full h-full object-cover"
                />
                <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                  <Video className="w-12 h-12 text-white" />
                </div>
              </div>
            )}

            {/* Content Info */}
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center space-x-2">
                  {getTypeIcon(item.type)}
                  {getPlatformIcon(item.platform)}
                </div>
                <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${getStatusColor(item.status)}`}>
                  {item.status}
                </span>
              </div>

              <h3 className="font-semibold text-gray-900 mb-2 line-clamp-1">{item.title}</h3>
              <p className="text-sm text-gray-600 mb-3 line-clamp-3">{item.content}</p>

              {/* Engagement Stats */}
              {item.status === 'published' && (
                <div className="flex items-center space-x-4 text-xs text-gray-500 mb-3">
                  <span>❤️ {item.engagement.likes}</span>
                  <span>💬 {item.engagement.comments}</span>
                  <span>🔄 {item.engagement.shares}</span>
                </div>
              )}

              {/* Metadata */}
              <div className="flex items-center justify-between text-xs text-gray-500 mb-3">
                <span>Created: {item.createdAt}</span>
                {item.publishedAt && (
                  <span>
                    {item.status === 'scheduled' ? 'Scheduled: ' : 'Published: '}
                    {item.publishedAt}
                  </span>
                )}
              </div>

              {/* Actions */}
              <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                <div className="flex items-center space-x-2">
                  <button className="p-1.5 text-gray-400 hover:text-blue-600 transition-colors">
                    <Eye className="w-4 h-4" />
                  </button>
                  <button className="p-1.5 text-gray-400 hover:text-green-600 transition-colors">
                    <Edit className="w-4 h-4" />
                  </button>
                  <button className="p-1.5 text-gray-400 hover:text-red-600 transition-colors">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
                <span className="text-xs text-gray-500">{item.platform}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Empty State */}
      {filteredContent.length === 0 && (
        <div className="text-center py-12">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No content found</h3>
          <p className="text-gray-500 mb-6">
            {searchQuery || filterType !== 'all' || filterPlatform !== 'all'
              ? 'Try adjusting your filters or search terms'
              : 'Start creating content to see it here'
            }
          </p>
          <button className="flex items-center space-x-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors mx-auto">
            <Plus className="w-4 h-4" />
            <span>Create First Content</span>
          </button>
        </div>
      )}

      {/* Stats Summary */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Content Statistics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-blue-600">{mockContent.length}</p>
            <p className="text-sm text-gray-500">Total Content</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-green-600">
              {mockContent.filter(item => item.status === 'published').length}
            </p>
            <p className="text-sm text-gray-500">Published</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-yellow-600">
              {mockContent.filter(item => item.status === 'scheduled').length}
            </p>
            <p className="text-sm text-gray-500">Scheduled</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-gray-600">
              {mockContent.filter(item => item.status === 'draft').length}
            </p>
            <p className="text-sm text-gray-500">Drafts</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ContentLibrary