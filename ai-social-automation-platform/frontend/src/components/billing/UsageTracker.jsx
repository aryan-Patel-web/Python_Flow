import { useState } from 'react'
import { BarChart3, Zap, Users, FileText, Calendar, AlertCircle } from 'lucide-react'

const UsageTracker = ({ currentPlan = 'pro' }) => {
  const [timeRange, setTimeRange] = useState('current')

  // Mock usage data - replace with real API data
  const usageData = {
    current: {
      posts: { used: 142, limit: 180, percentage: 79 },
      platforms: { used: 3, limit: 5, percentage: 60 },
      aiGenerations: { used: 89, limit: 200, percentage: 45 },
      teamMembers: { used: 2, limit: 3, percentage: 67 }
    },
    previous: {
      posts: { used: 165, limit: 180, percentage: 92 },
      platforms: { used: 4, limit: 5, percentage: 80 },
      aiGenerations: { used: 156, limit: 200, percentage: 78 },
      teamMembers: { used: 3, limit: 3, percentage: 100 }
    }
  }

  const planLimits = {
    free: {
      posts: 90,
      platforms: 2,
      aiGenerations: 50,
      teamMembers: 1
    },
    pro: {
      posts: 180,
      platforms: 5,
      aiGenerations: 200,
      teamMembers: 3
    },
    enterprise: {
      posts: 'unlimited',
      platforms: 'unlimited',
      aiGenerations: 'unlimited',
      teamMembers: 'unlimited'
    }
  }

  const currentUsage = usageData[timeRange]

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'bg-red-500'
    if (percentage >= 70) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  const getUsageStatus = (percentage) => {
    if (percentage >= 90) return { color: 'red', text: 'Critical' }
    if (percentage >= 70) return { color: 'yellow', text: 'Warning' }
    return { color: 'green', text: 'Good' }
  }

  const usageItems = [
    {
      id: 'posts',
      name: 'Posts This Month',
      icon: FileText,
      description: 'Published posts across all platforms',
      ...currentUsage.posts
    },
    {
      id: 'platforms',
      name: 'Connected Platforms',
      icon: BarChart3,
      description: 'Active social media connections',
      ...currentUsage.platforms
    },
    {
      id: 'aiGenerations',
      name: 'AI Generations',
      icon: Zap,
      description: 'AI-generated content pieces',
      ...currentUsage.aiGenerations
    },
    {
      id: 'teamMembers',
      name: 'Team Members',
      icon: Users,
      description: 'Active team member accounts',
      ...currentUsage.teamMembers
    }
  ]

  const totalUsageScore = Math.round(
    usageItems.reduce((sum, item) => sum + item.percentage, 0) / usageItems.length
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Usage Overview</h3>
        <div className="flex space-x-2">
          <button
            onClick={() => setTimeRange('current')}
            className={`px-3 py-1 text-sm font-medium rounded-lg transition-colors ${
              timeRange === 'current'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Current Period
          </button>
          <button
            onClick={() => setTimeRange('previous')}
            className={`px-3 py-1 text-sm font-medium rounded-lg transition-colors ${
              timeRange === 'previous'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Previous Period
          </button>
        </div>
      </div>

      {/* Overall Usage Summary */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-lg font-semibold text-gray-900">Overall Usage</h4>
            <p className="text-sm text-gray-600">
              {timeRange === 'current' ? 'This month' : 'Last month'} • {currentPlan.charAt(0).toUpperCase() + currentPlan.slice(1)} Plan
            </p>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${getUsageColor(totalUsageScore)}`}></div>
              <span className="text-2xl font-bold text-gray-900">{totalUsageScore}%</span>
            </div>
            <p className="text-sm text-gray-500">Average usage</p>
          </div>
        </div>
      </div>

      {/* Individual Usage Items */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {usageItems.map((item) => {
          const Icon = item.icon
          const status = getUsageStatus(item.percentage)
          
          return (
            <div key={item.id} className="bg-white p-6 rounded-lg border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-gray-100 rounded-lg">
                    <Icon className="w-5 h-5 text-gray-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{item.name}</h4>
                    <p className="text-sm text-gray-500">{item.description}</p>
                  </div>
                </div>
                {item.percentage >= 90 && (
                  <AlertCircle className="w-5 h-5 text-red-500" />
                )}
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-gray-600">Usage</span>
                  <span className="font-medium">
                    {item.used} / {item.limit === 'unlimited' ? '∞' : item.limit}
                  </span>
                </div>

                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${getUsageColor(item.percentage)}`}
                    style={{ width: `${Math.min(item.percentage, 100)}%` }}
                  ></div>
                </div>

                <div className="flex items-center justify-between">
                  <span className={`text-sm font-medium text-${status.color}-600`}>
                    {status.text}
                  </span>
                  <span className="text-sm text-gray-500">{item.percentage}%</span>
                </div>

                {item.percentage >= 90 && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm text-red-700">
                      You're approaching your limit. Consider upgrading your plan.
                    </p>
                  </div>
                )}
              </div>
            </div>
          )
        })}
      </div>

      {/* Usage History */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-md font-semibold text-gray-900 mb-4">Usage History</h4>
        <div className="space-y-4">
          {[
            { period: 'January 2024', posts: 165, platforms: 4, aiGenerations: 156 },
            { period: 'December 2023', posts: 142, platforms: 3, aiGenerations: 134 },
            { period: 'November 2023', posts: 127, platforms: 3, aiGenerations: 98 }
          ].map((month, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <Calendar className="w-4 h-4 text-gray-500" />
                <span className="font-medium text-gray-900">{month.period}</span>
              </div>
              <div className="flex items-center space-x-6 text-sm text-gray-600">
                <span>{month.posts} posts</span>
                <span>{month.platforms} platforms</span>
                <span>{month.aiGenerations} AI generations</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Usage Recommendations */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-md font-semibold text-blue-900 mb-2">Usage Recommendations</h4>
        <div className="space-y-2 text-sm text-blue-700">
          {totalUsageScore >= 80 ? (
            <>
              <p>• You're using {totalUsageScore}% of your plan limits</p>
              <p>• Consider upgrading to avoid hitting limits</p>
              <p>• Enterprise plan offers unlimited usage</p>
            </>
          ) : (
            <>
              <p>• Great usage efficiency at {totalUsageScore}%</p>
              <p>• You have room to grow within your current plan</p>
              <p>• Consider adding more platforms to maximize value</p>
            </>
          )}
        </div>
      </div>
    </div>
  )
}

export default UsageTracker