import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'

const StatsOverview = ({ stats }) => {
  // Sample chart data
  const engagementData = [
    { day: 'Mon', engagement: 45, posts: 6 },
    { day: 'Tue', engagement: 52, posts: 8 },
    { day: 'Wed', engagement: 38, posts: 5 },
    { day: 'Thu', engagement: 65, posts: 7 },
    { day: 'Fri', engagement: 78, posts: 9 },
    { day: 'Sat', engagement: 85, posts: 12 },
    { day: 'Sun', engagement: 92, posts: 10 }
  ]

  const growthData = [
    { week: 'Week 1', followers: 3200 },
    { week: 'Week 2', followers: 3350 },
    { week: 'Week 3', followers: 3480 },
    { week: 'Week 4', followers: 3580 }
  ]

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Engagement Trends */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Weekly Engagement</h3>
            <p className="text-sm text-gray-500">Engagement vs Posts Published</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-blue-600">{stats.engagementRate}%</p>
            <p className="text-sm text-green-600">+12% from last week</p>
          </div>
        </div>
        
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={engagementData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="day" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#6b7280' }}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#6b7280' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="engagement" 
                stroke="#3b82f6" 
                strokeWidth={3}
                dot={{ fill: '#3b82f6', strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, stroke: '#3b82f6', strokeWidth: 2 }}
              />
              <Line 
                type="monotone" 
                dataKey="posts" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ fill: '#10b981', strokeWidth: 2, r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
        
        <div className="flex items-center justify-center space-x-6 mt-4">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
            <span className="text-sm text-gray-600">Engagement</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-600 rounded-full"></div>
            <span className="text-sm text-gray-600">Posts</span>
          </div>
        </div>
      </div>

      {/* Follower Growth */}
      <div className="bg-white p-6 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Follower Growth</h3>
            <p className="text-sm text-gray-500">Total followers across platforms</p>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-purple-600">{stats.totalFollowers?.toLocaleString()}</p>
            <p className="text-sm text-green-600">+{stats.growthRate}% this month</p>
          </div>
        </div>
        
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={growthData}>
              <defs>
                <linearGradient id="colorGrowth" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis 
                dataKey="week" 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#6b7280' }}
              />
              <YAxis 
                axisLine={false}
                tickLine={false}
                tick={{ fontSize: 12, fill: '#6b7280' }}
              />
              <Tooltip 
                contentStyle={{
                  backgroundColor: '#fff',
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
                formatter={(value) => [value.toLocaleString(), 'Followers']}
              />
              <Area 
                type="monotone" 
                dataKey="followers" 
                stroke="#8b5cf6" 
                strokeWidth={2}
                fill="url(#colorGrowth)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}

export default StatsOverview