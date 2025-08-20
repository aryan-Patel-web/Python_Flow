import { useState } from 'react'
import { Clock, Plus, Trash2, Calendar, Settings, Save } from 'lucide-react'
import Button from '../common/Button'

const PostingSchedule = ({ selectedDomains, onSave }) => {
  const [schedules, setSchedules] = useState([
    { id: 1, time: '09:00', days: ['monday', 'wednesday', 'friday'], isActive: true },
    { id: 2, time: '15:00', days: ['tuesday', 'thursday'], isActive: true },
    { id: 3, time: '20:00', days: ['saturday', 'sunday'], isActive: false }
  ])
  
  const [globalSettings, setGlobalSettings] = useState({
    timezone: 'Asia/Kolkata',
    postsPerDay: 3,
    intervalBetweenPosts: 2, // hours
    avoidWeekends: false,
    optimalTiming: true
  })
  
  const days = [
    { id: 'monday', label: 'Mon' },
    { id: 'tuesday', label: 'Tue' },
    { id: 'wednesday', label: 'Wed' },
    { id: 'thursday', label: 'Thu' },
    { id: 'friday', label: 'Fri' },
    { id: 'saturday', label: 'Sat' },
    { id: 'sunday', label: 'Sun' }
  ]
  
  const timezones = [
    { value: 'Asia/Kolkata', label: 'India (IST)' },
    { value: 'America/New_York', label: 'US Eastern' },
    { value: 'Europe/London', label: 'UK (GMT)' },
    { value: 'Asia/Tokyo', label: 'Japan (JST)' },
    { value: 'Australia/Sydney', label: 'Australia (AEDT)' }
  ]
  
  const addSchedule = () => {
    const newSchedule = {
      id: Date.now(),
      time: '12:00',
      days: ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'],
      isActive: true
    }
    setSchedules([...schedules, newSchedule])
  }
  
  const updateSchedule = (id, updates) => {
    setSchedules(schedules.map(schedule => 
      schedule.id === id ? { ...schedule, ...updates } : schedule
    ))
  }
  
  const deleteSchedule = (id) => {
    setSchedules(schedules.filter(schedule => schedule.id !== id))
  }
  
  const toggleDay = (scheduleId, day) => {
    const schedule = schedules.find(s => s.id === scheduleId)
    const updatedDays = schedule.days.includes(day)
      ? schedule.days.filter(d => d !== day)
      : [...schedule.days, day]
    
    updateSchedule(scheduleId, { days: updatedDays })
  }
  
  const handleSave = () => {
    const scheduleData = {
      schedules: schedules.filter(s => s.isActive && s.days.length > 0),
      globalSettings,
      domains: selectedDomains
    }
    onSave(scheduleData)
  }
  
  const getOptimalTimes = () => {
    // Optimal posting times based on platform research
    const optimalTimes = {
      'instagram': ['09:00', '11:00', '15:00', '19:00'],
      'facebook': ['09:00', '13:00', '15:00'],
      'linkedin': ['08:00', '12:00', '17:00'],
      'twitter': ['09:00', '12:00', '15:00', '18:00'],
      'youtube': ['10:00', '14:00', '20:00']
    }
    
    return optimalTimes
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Posting Schedule</h3>
          <p className="text-sm text-gray-600">
            Configure when your content will be automatically posted
          </p>
        </div>
        <Button onClick={addSchedule} size="sm">
          <Plus className="w-4 h-4 mr-2" />
          Add Schedule
        </Button>
      </div>
      
      {/* Global Settings */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-4">
        <h4 className="font-medium text-gray-900 flex items-center">
          <Settings className="w-4 h-4 mr-2" />
          Global Settings
        </h4>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Timezone
            </label>
            <select
              value={globalSettings.timezone}
              onChange={(e) => setGlobalSettings(prev => ({
                ...prev,
                timezone: e.target.value
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {timezones.map(tz => (
                <option key={tz.value} value={tz.value}>
                  {tz.label}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Posts per Day
            </label>
            <select
              value={globalSettings.postsPerDay}
              onChange={(e) => setGlobalSettings(prev => ({
                ...prev,
                postsPerDay: parseInt(e.target.value)
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              {[1, 2, 3, 4, 5, 6].map(num => (
                <option key={num} value={num}>{num} posts</option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={globalSettings.avoidWeekends}
              onChange={(e) => setGlobalSettings(prev => ({
                ...prev,
                avoidWeekends: e.target.checked
              }))}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              Avoid weekends
            </span>
          </label>
          
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={globalSettings.optimalTiming}
              onChange={(e) => setGlobalSettings(prev => ({
                ...prev,
                optimalTiming: e.target.checked
              }))}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="ml-2 text-sm text-gray-700">
              Use optimal posting times
            </span>
          </label>
        </div>
      </div>
      
      {/* Schedule List */}
      <div className="space-y-4">
        <h4 className="font-medium text-gray-900">Posting Times</h4>
        
        {schedules.map((schedule) => (
          <div key={schedule.id} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-3">
                <Clock className="w-5 h-5 text-gray-400" />
                <input
                  type="time"
                  value={schedule.time}
                  onChange={(e) => updateSchedule(schedule.id, { time: e.target.value })}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={schedule.isActive}
                    onChange={(e) => updateSchedule(schedule.id, { isActive: e.target.checked })}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">Active</span>
                </label>
              </div>
              
              <button
                onClick={() => deleteSchedule(schedule.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
            
            {/* Day Selector */}
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                Active Days ({schedule.days.length} selected)
              </label>
              <div className="flex flex-wrap gap-2">
                {days.map((day) => (
                  <button
                    key={day.id}
                    onClick={() => toggleDay(schedule.id, day.id)}
                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                      schedule.days.includes(day.id)
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {day.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ))}
        
        {schedules.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <Calendar className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No posting schedules configured</p>
            <Button onClick={addSchedule} className="mt-3" size="sm">
              <Plus className="w-4 h-4 mr-2" />
              Add Your First Schedule
            </Button>
          </div>
        )}
      </div>
      
      {/* Optimal Times Suggestion */}
      {globalSettings.optimalTiming && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="font-medium text-blue-900 mb-2">📈 Optimal Posting Times</h4>
          <p className="text-sm text-blue-800 mb-3">
            Based on audience engagement patterns, here are the best times to post:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-2 text-sm">
            {Object.entries(getOptimalTimes()).map(([platform, times]) => (
              <div key={platform} className="text-blue-800">
                <div className="font-medium capitalize">{platform}</div>
                <div className="text-xs">{times.join(', ')}</div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Save Button */}
      <div className="flex justify-end pt-4 border-t">
        <Button onClick={handleSave} className="px-6">
          <Save className="w-4 h-4 mr-2" />
          Save Schedule
        </Button>
      </div>
    </div>
  )
}

export default PostingSchedule