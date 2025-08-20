import { useState } from 'react'
import { Download, FileText, BarChart3, Calendar, CheckCircle } from 'lucide-react'
import Button from '../common/Button'

const ExportData = () => {
  const [selectedFormat, setSelectedFormat] = useState('csv')
  const [selectedTimeRange, setSelectedTimeRange] = useState('30d')
  const [selectedMetrics, setSelectedMetrics] = useState(['engagement', 'reach', 'followers'])
  const [isExporting, setIsExporting] = useState(false)
  const [exportComplete, setExportComplete] = useState(false)

  const formats = [
    { id: 'csv', name: 'CSV', description: 'Comma-separated values', icon: FileText },
    { id: 'xlsx', name: 'Excel', description: 'Excel spreadsheet', icon: BarChart3 },
    { id: 'pdf', name: 'PDF', description: 'PDF report', icon: FileText },
    { id: 'json', name: 'JSON', description: 'JSON data format', icon: FileText }
  ]

  const timeRanges = [
    { id: '7d', name: 'Last 7 days' },
    { id: '30d', name: 'Last 30 days' },
    { id: '90d', name: 'Last 90 days' },
    { id: '1y', name: 'Last year' },
    { id: 'custom', name: 'Custom range' }
  ]

  const metrics = [
    { id: 'engagement', name: 'Engagement Metrics', description: 'Likes, comments, shares' },
    { id: 'reach', name: 'Reach & Impressions', description: 'Post reach and impressions' },
    { id: 'followers', name: 'Follower Growth', description: 'Follower count changes' },
    { id: 'posts', name: 'Post Performance', description: 'Individual post metrics' },
    { id: 'demographics', name: 'Audience Demographics', description: 'Age, location, interests' },
    { id: 'timing', name: 'Optimal Timing', description: 'Best posting times' }
  ]

  const handleMetricToggle = (metricId) => {
    setSelectedMetrics(prev => 
      prev.includes(metricId)
        ? prev.filter(id => id !== metricId)
        : [...prev, metricId]
    )
  }

  const handleExport = async () => {
    setIsExporting(true)
    setExportComplete(false)
    
    try {
      // Simulate export process
      await new Promise(resolve => setTimeout(resolve, 3000))
      
      // In real implementation, this would call your API
      const exportData = {
        format: selectedFormat,
        timeRange: selectedTimeRange,
        metrics: selectedMetrics,
        timestamp: new Date().toISOString()
      }
      
      // Simulate file download
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `analytics-export-${Date.now()}.${selectedFormat}`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
      
      setExportComplete(true)
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  if (exportComplete) {
    return (
      <div className="bg-white p-8 rounded-lg border border-gray-200 text-center">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-green-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Export Complete!</h3>
        <p className="text-gray-600 mb-6">Your analytics data has been downloaded successfully.</p>
        <div className="flex space-x-3 justify-center">
          <Button 
            variant="secondary"
            onClick={() => setExportComplete(false)}
          >
            Export Again
          </Button>
          <Button variant="primary">
            View Downloads
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">Export Analytics Data</h3>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>

      {/* Format Selection */}
      <div>
        <h4 className="text-md font-semibold text-gray-900 mb-3">Export Format</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {formats.map((format) => {
            const Icon = format.icon
            return (
              <div
                key={format.id}
                className={`p-4 border-2 rounded-lg cursor-pointer transition-all ${
                  selectedFormat === format.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedFormat(format.id)}
              >
                <div className="flex items-center space-x-3">
                  <Icon className="w-5 h-5 text-gray-600" />
                  <div>
                    <p className="font-medium text-gray-900">{format.name}</p>
                    <p className="text-xs text-gray-500">{format.description}</p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Time Range Selection */}
      <div>
        <h4 className="text-md font-semibold text-gray-900 mb-3">Time Range</h4>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {timeRanges.map((range) => (
            <button
              key={range.id}
              className={`p-3 border-2 rounded-lg text-sm font-medium transition-all ${
                selectedTimeRange === range.id
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 text-gray-700 hover:border-gray-300'
              }`}
              onClick={() => setSelectedTimeRange(range.id)}
            >
              {range.name}
            </button>
          ))}
        </div>
        
        {selectedTimeRange === 'custom' && (
          <div className="mt-3 grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
        )}
      </div>

      {/* Metrics Selection */}
      <div>
        <h4 className="text-md font-semibold text-gray-900 mb-3">Include Metrics</h4>
        <div className="space-y-3">
          {metrics.map((metric) => (
            <div
              key={metric.id}
              className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50"
            >
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id={metric.id}
                  checked={selectedMetrics.includes(metric.id)}
                  onChange={() => handleMetricToggle(metric.id)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <div>
                  <label htmlFor={metric.id} className="font-medium text-gray-900 cursor-pointer">
                    {metric.name}
                  </label>
                  <p className="text-sm text-gray-500">{metric.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Export Summary */}
      <div className="bg-gray-50 p-4 rounded-lg">
        <h4 className="text-md font-semibold text-gray-900 mb-2">Export Summary</h4>
        <div className="space-y-1 text-sm text-gray-600">
          <p><span className="font-medium">Format:</span> {formats.find(f => f.id === selectedFormat)?.name}</p>
          <p><span className="font-medium">Time Range:</span> {timeRanges.find(r => r.id === selectedTimeRange)?.name}</p>
          <p><span className="font-medium">Metrics:</span> {selectedMetrics.length} selected</p>
          <p><span className="font-medium">Estimated Size:</span> ~2.5 MB</p>
        </div>
      </div>

      {/* Export Button */}
      <div className="flex justify-end space-x-3">
        <Button variant="secondary">
          Preview Data
        </Button>
        <Button 
          variant="primary"
          leftIcon={<Download className="w-4 h-4" />}
          loading={isExporting}
          onClick={handleExport}
          disabled={selectedMetrics.length === 0}
        >
          {isExporting ? 'Exporting...' : 'Export Data'}
        </Button>
      </div>

      {/* Recent Exports */}
      <div className="border-t border-gray-200 pt-6">
        <h4 className="text-md font-semibold text-gray-900 mb-3">Recent Exports</h4>
        <div className="space-y-2">
          {[
            { name: 'analytics-export-2024-01-15.csv', date: '2024-01-15', size: '2.3 MB' },
            { name: 'analytics-export-2024-01-08.xlsx', date: '2024-01-08', size: '3.1 MB' },
            { name: 'analytics-export-2024-01-01.pdf', date: '2024-01-01', size: '1.8 MB' }
          ].map((file, index) => (
            <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <FileText className="w-4 h-4 text-gray-500" />
                <div>
                  <p className="text-sm font-medium text-gray-900">{file.name}</p>
                  <p className="text-xs text-gray-500">{file.date} • {file.size}</p>
                </div>
              </div>
              <Button variant="ghost" size="sm">
                Download
              </Button>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ExportData