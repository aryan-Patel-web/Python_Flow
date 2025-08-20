import { TrendingUp, TrendingDown, Users, UserPlus, Eye, Heart } from 'lucide-react'

const GrowthMetrics = ({ timeRange = '30d' }) => {
  // Mock data - replace with real API data
  const metrics = [
    {
      id: 'followers',
      name: 'Total Followers',
      value: 12456,
      change: +15.3,
      changeType: 'increase',
      icon: Users,
      color: 'blue'
    },
    {
      id: 'new_followers',
      name: 'New Followers',
      value: 234,
      change: +23.7,
      changeType: 'increase',
      icon: UserPlus,
      color: 'green'
    },
    {
      id: 'reach',
      name: 'Total Reach',
      value: 45789,
      change: +8.2,
      changeType: 'increase',
      icon: Eye,
      color: 'purple'
    },
    {
      id: 'engagement',
      name: 'Engagement Rate',
      value: 3.4,
      change: -2.1,
      changeType: 'decrease',
      icon: Heart,
      color: 'red',
      suffix: '%'
    }
  ]

  const getColorClasses = (color) => {
    const colors = {
      blue: 'bg-blue-100 text-blue-600',
      green: 'bg-green-100 text-green-600',
      purple: 'bg-purple-100 text-purple-600',
      red: 'bg-red-100 text-red-600',
      orange: 'bg-orange-100 text-orange-600'
    }
    return colors[color] || colors.blue
  }

  const formatValue = (value, suffix = '') => {
    if (value >= 1000000) {
      return `${(value / 1000000).toFixed(1)}M${suffix}`
    }
    if (value >= 1000) {
      return `${(value / 1000).toFixed(1)}K${suffix}`
    }
    return `${value}${suffix}`
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Growth Metrics</h3>
        <span className="text-sm text-gray-500">Last {timeRange === '30d' ? '30 days' : timeRange}</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric) => {
          const Icon = metric.icon
          const isIncrease = metric.changeType === 'increase'
          
          return (
            <div key={metric.id} className="bg-white p-6 rounded-lg border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className={`p-2 rounded-lg ${getColorClasses(metric.color)}`}>
                  <Icon className="w-5 h-5" />
                </div>
                <div className={`flex items-center text-sm font-medium ${
                  isIncrease ? 'text-green-600' : 'text-red-600'
                }`}>
                  {isIncrease ? (
                    <TrendingUp className="w-4 h-4 mr-1" />
                  ) : (
                    <TrendingDown className="w-4 h-4 mr-1" />
                  )}
                  {Math.abs(metric.change)}%
                </div>
              </div>
              
              <div>
                <p className="text-2xl font-bold text-gray-900 mb-1">
                  {formatValue(metric.value, metric.suffix)}
                </p>
                <p className="text-sm text-gray-600">{metric.name}</p>
              </div>
              
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-xs text-gray-500">
                  {isIncrease ? '+' : ''}{metric.change}% from last period
                </p>
              </div>
            </div>
          )
        })}
      </div>

      {/* Growth Chart Preview */}
      <div className="bg-white p-6 rounded-lg border border-gray-200">
        <h4 className="text-md font-semibold text-gray-900 mb-4">Growth Trend</h4>
        <div className="h-32 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg flex items-center justify-center">
          <p className="text-gray-500 text-sm">Growth chart visualization would go here</p>
        </div>
      </div>
    </div>
  )
}

export default GrowthMetrics