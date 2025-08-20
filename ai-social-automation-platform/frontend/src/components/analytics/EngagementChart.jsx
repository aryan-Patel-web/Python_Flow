import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import { Calendar, TrendingUp, Eye, Heart, Share, MessageCircle } from 'lucide-react'

const EngagementChart = ({ timeRange = '7d' }) => {
  const [chartType, setChartType] = useState('line')
  const [selectedMetric, setSelectedMetric] = useState('engagement')

  // Mock data - replace with real API data
  const engagementData = [
    { date: '2024-01-01', likes: 120, comments: 25, shares: 15, views: 1500, engagement: 160 },
    { date: '2024-01-02', likes: 180, comments: 35, shares: 22, views: 2100, engagement: 237 },
    { date: '2024-01-03', likes: 150, comments: 28, shares: 18, views: 1800, engagement: 196 },
    { date: '2024-01-04', likes: 220, comments: 42, shares: 30, views: 2800, engagement: 292 },
    { date: '2024-01-05', likes: 190, comments: 38, shares: 25, views: 2200, engagement: 253 },
    { date: '2024-01-06', likes: 160, comments: 30, shares: 20, views: 1900, engagement: 210 },
    { date: '2024-01-07', likes: 240, comments: 45, shares: 35, views: 3200, engagement: 320 }
  ]

  const platformData = [
    { name: 'Instagram', value: 35, color: '#E1306C' },
    { name: 'Facebook', value: 25, color: '#1877F2' },
    { name: 'YouTube', value: 20, color: '#FF0000' },
    { name: 'LinkedIn', value: 15, color: '#0A66C2' },
    { name: 'Twitter', value: 5, color: '#1DA1F2' }
  ]

  const getChartData = () => {
    switch (selectedMetric) {
      case 'likes':
        return engagementData.map(item => ({ ...item, value: item.likes }))
      case 'comments':
        return engagementData.map(item => ({ ...item, value: item.comments }))
      case 'shares':
        return engagementData.map(item => ({ ...item, value: item.shares }))
      case 'views':
        return engagementData.map(item => ({ ...item, value: item.views }))
      default:
        return engagementData.map(item => ({ ...item, value: item.engagement }))
    }
  }

  const getMetricIcon = (metric) => {
    switch (metric) {
      case 'likes': return <Heart className="w-4 h-4" />
      case 'comments': return <MessageCircle className="w-4 h-4" />
      case 'shares': return <Share className="w-4 h-4" />
      case 'views': return <Eye className="w-4 h-4" />
      default: return <TrendingUp className="w-4 h-4" />
    }
  }

  const renderLineChart = () => (
    <ResponsiveContainer width="100%" height={350}>
      <LineChart data={getChartData()}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey="date" 
          stroke="#666"
          fontSize={12}
          tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        />
        <YAxis stroke="#666" fontSize={12} />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
          labelFormatter={(value) => new Date(value).toLocaleDateString()}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="value" 
          stroke="#3B82F6" 
          strokeWidth={3}
          dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
          activeDot={{ r: 6, stroke: '#3B82F6', strokeWidth: 2 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )

  const renderBarChart = () => (
    <ResponsiveContainer width="100%" height={350}>
      <BarChart data={engagementData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey="date" 
          stroke="#666"
          fontSize={12}
          tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
        />
        <YAxis stroke="#666" fontSize={12} />
        <Tooltip 
          contentStyle={{ 
            backgroundColor: '#fff', 
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
          }}
        />
        <Legend />
        <Bar dataKey="likes" fill="#E11D48" name="Likes" />
        <Bar dataKey="comments" fill="#3B82F6" name="Comments" />
        <Bar dataKey="shares" fill="#10B981" name="Shares" />
      </BarChart>
    </ResponsiveContainer>
  )

  const renderPieChart = () => (
    <ResponsiveContainer width="100%" height={350}>
      <PieChart>
        <Pie
          data={platformData}
          cx="50%"
          cy="50%"
          labelLine={false}
          label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          outerRadius={120}
          fill="#8884d8"
          dataKey="value"
        >
          {platformData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.color} />
          ))}
        </Pie>
        <Tooltip />
      </PieChart>
    </ResponsiveContainer>
  )

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <TrendingUp className="w-5 h-5 text-blue-600" />
          <h3 className="text-lg font-semibold text-gray-900">Engagement Analytics</h3>
        </div>
        
        <div className="flex items-center space-x-2">
          <Calendar className="w-4 h-4 text-gray-400" />
          <select 
            value={timeRange}
            className="text-sm border border-gray-300 rounded-lg px-3 py-1 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
          </select>
        </div>
      </div>

      {/* Chart Type Selector */}
      <div className="flex space-x-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        <button
          onClick={() => setChartType('line')}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
            chartType === 'line' 
              ? 'bg-white text-gray-900 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Line Chart
        </button>
        <button
          onClick={() => setChartType('bar')}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
            chartType === 'bar' 
              ? 'bg-white text-gray-900 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Bar Chart
        </button>
        <button
          onClick={() => setChartType('pie')}
          className={`px-3 py-1 rounded-md text-sm font-medium transition-colors ${
            chartType === 'pie' 
              ? 'bg-white text-gray-900 shadow-sm' 
              : 'text-gray-600 hover:text-gray-900'
          }`}
        >
          Platform Split
        </button>
      </div>

      {/* Metric Selector (for line chart) */}
      {chartType === 'line' && (
        <div className="flex flex-wrap gap-2 mb-6">
          {['engagement', 'likes', 'comments', 'shares', 'views'].map((metric) => (
            <button
              key={metric}
              onClick={() => setSelectedMetric(metric)}
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedMetric === metric
                  ? 'bg-blue-100 text-blue-700 border border-blue-200'
                  : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
              }`}
            >
              {getMetricIcon(metric)}
              <span className="capitalize">{metric}</span>
            </button>
          ))}
        </div>
      )}

      {/* Chart */}
      <div className="w-full">
        {chartType === 'line' && renderLineChart()}
        {chartType === 'bar' && renderBarChart()}
        {chartType === 'pie' && renderPieChart()}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6 pt-6 border-t border-gray-100">
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {engagementData.reduce((sum, item) => sum + item.likes, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Total Likes</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {engagementData.reduce((sum, item) => sum + item.comments, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Total Comments</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {engagementData.reduce((sum, item) => sum + item.shares, 0).toLocaleString()}
          </div>
          <div className="text-sm text-gray-600">Total Shares</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-gray-900">
            {(engagementData.reduce((sum, item) => sum + item.engagement, 0) / engagementData.length).toFixed(1)}
          </div>
          <div className="text-sm text-gray-600">Avg Engagement</div>
        </div>
      </div>
    </div>
  )
}

export default EngagementChart