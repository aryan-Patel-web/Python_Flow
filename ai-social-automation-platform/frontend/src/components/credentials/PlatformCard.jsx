import { useState } from 'react'
import { Settings, Trash2, AlertCircle, CheckCircle, Plus, MoreHorizontal } from 'lucide-react'
import Button from '../common/Button'

const PlatformCard = ({ platform, onSetup, onEdit, onDelete, onToggle }) => {
  const [isLoading, setIsLoading] = useState(false)
  const [showMenu, setShowMenu] = useState(false)
  
  const handleToggle = async () => {
    setIsLoading(true)
    try {
      await onToggle(platform.id, !platform.isActive)
    } finally {
      setIsLoading(false)
    }
  }
  
  const getStatusColor = () => {
    if (!platform.isConnected) return 'text-gray-500'
    if (!platform.isActive) return 'text-yellow-600'
    return 'text-green-600'
  }
  
  const getStatusText = () => {
    if (!platform.isConnected) return 'Not Connected'
    if (!platform.isActive) return 'Connected (Paused)'
    return 'Active'
  }
  
  const getStatusIcon = () => {
    if (!platform.isConnected) return AlertCircle
    if (!platform.isActive) return AlertCircle
    return CheckCircle
  }
  
  const StatusIcon = getStatusIcon()
  
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div 
            className="w-12 h-12 rounded-lg flex items-center justify-center"
            style={{ backgroundColor: `${platform.color}20` }}
          >
            <platform.icon 
              className="w-6 h-6" 
              style={{ color: platform.color }} 
            />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{platform.name}</h3>
            <div className="flex items-center space-x-1 mt-1">
              <StatusIcon className={`w-4 h-4 ${getStatusColor()}`} />
              <span className={`text-sm ${getStatusColor()}`}>
                {getStatusText()}
              </span>
            </div>
          </div>
        </div>
        
        {/* Actions Menu */}
        <div className="relative">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <MoreHorizontal className="w-4 h-4 text-gray-500" />
          </button>
          
          {showMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10">
              <div className="py-1">
                <button
                  onClick={() => {
                    platform.isConnected ? onEdit(platform) : onSetup(platform)
                    setShowMenu(false)
                  }}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                >
                  <Settings className="w-4 h-4" />
                  <span>{platform.isConnected ? 'Edit Setup' : 'Setup'}</span>
                </button>
                
                {platform.isConnected && (
                  <button
                    onClick={() => {
                      handleToggle()
                      setShowMenu(false)
                    }}
                    className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50"
                    disabled={isLoading}
                  >
                    <span className="w-4 h-4 flex items-center justify-center">
                      {platform.isActive ? '⏸️' : '▶️'}
                    </span>
                    <span>{platform.isActive ? 'Pause' : 'Resume'}</span>
                  </button>
                )}
                
                <hr className="my-1" />
                <button
                  onClick={() => {
                    onDelete(platform.id)
                    setShowMenu(false)
                  }}
                  className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Remove</span>
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Stats */}
      {platform.isConnected && (
        <div className="space-y-3 mb-4">
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Posts Today</span>
            <span className="font-semibold text-gray-900">
              {platform.stats?.postsToday || 0}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Total Posts</span>
            <span className="font-semibold text-gray-900">
              {platform.stats?.totalPosts || 0}
            </span>
          </div>
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Engagement Rate</span>
            <span className="font-semibold text-green-600">
              {platform.stats?.engagementRate || '0%'}
            </span>
          </div>
        </div>
      )}
      
      {/* Action Button */}
      <div className="pt-4 border-t border-gray-100">
        {!platform.isConnected ? (
          <Button
            onClick={() => onSetup(platform)}
            className="w-full"
            size="sm"
          >
            <Plus className="w-4 h-4 mr-2" />
            Connect Platform
          </Button>
        ) : (
          <div className="flex space-x-2">
            <Button
              variant="outline"
              onClick={() => onEdit(platform)}
              className="flex-1"
              size="sm"
            >
              <Settings className="w-4 h-4 mr-2" />
              Settings
            </Button>
            <Button
              onClick={handleToggle}
              disabled={isLoading}
              className={`flex-1 ${platform.isActive 
                ? 'bg-yellow-600 hover:bg-yellow-700' 
                : 'bg-green-600 hover:bg-green-700'
              }`}
              size="sm"
            >
              {isLoading ? (
                'Loading...'
              ) : platform.isActive ? (
                <>⏸️ Pause</>
              ) : (
                <>▶️ Resume</>
              )}
            </Button>
          </div>
        )}
      </div>
      
      {/* Last Activity */}
      {platform.isConnected && platform.lastActivity && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            Last activity: {new Date(platform.lastActivity).toLocaleDateString()}
          </p>
        </div>
      )}
    </div>
  )
}

export default PlatformCard