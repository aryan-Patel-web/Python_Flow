import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { 
  CheckCircle, 
  ArrowRight, 
  Bot, 
  Zap, 
  Calendar, 
  BarChart3,
  Settings,
  PlayCircle,
  Sparkles,
  Trophy
} from 'lucide-react'
import Button from '../../components/common/Button'
import { useAuth } from '../../context/AuthContext'
import { useApp } from '../../context/AppContext'
import useToast from '../../hooks/useToast'

const Complete = () => {
  const navigate = useNavigate()
  const { user, updateProfile } = useAuth()
  const { state } = useApp()
  const { success } = useToast()
  
  const [isActivating, setIsActivating] = useState(false)
  const [currentStep, setCurrentStep] = useState(0)

  const setupSteps = [
    { icon: CheckCircle, title: 'Account Created', status: 'completed' },
    { icon: CheckCircle, title: 'Plan Selected', status: 'completed' },
    { icon: CheckCircle, title: 'Platforms Connected', status: 'completed' },
    { icon: CheckCircle, title: 'Content Domains Chosen', status: 'completed' },
    { icon: Bot, title: 'AI Activation', status: 'current' }
  ]

  const features = [
    {
      icon: Bot,
      title: 'AI Content Generation',
      description: 'Your AI will start creating engaging content immediately',
      status: 'ready'
    },
    {
      icon: Calendar,
      title: 'Smart Scheduling',
      description: 'Posts will be published at optimal times for maximum reach',
      status: 'ready'
    },
    {
      icon: BarChart3,
      title: 'Analytics Tracking',
      description: 'Monitor your growth with detailed performance insights',
      status: 'ready'
    },
    {
      icon: Zap,
      title: 'Automation Engine',
      description: 'Sit back and watch your social media grow on autopilot',
      status: 'ready'
    }
  ]

  const stats = {
    platformsConnected: state.connectedPlatforms?.length || 0,
    domainsSelected: state.selectedDomains?.length || 0,
    estimatedPosts: (state.connectedPlatforms?.length || 0) * 3, // 3 posts per platform per day
    estimatedReach: ((state.connectedPlatforms?.length || 0) * 1000) // estimated reach per platform
  }

  useEffect(() => {
    // Animate through steps
    const timer = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < setupSteps.length - 1) {
          return prev + 1
        }
        clearInterval(timer)
        return prev
      })
    }, 500)

    return () => clearInterval(timer)
  }, [])

  const handleActivateAI = async () => {
    setIsActivating(true)
    
    try {
      // Mark onboarding as complete
      await updateProfile({ onboardingComplete: true })
      
      // Simulate AI activation process
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      success('🎉 AI automation activated! Your content creation has begun!')
      navigate('/dashboard')
    } catch (error) {
      console.error('Activation error:', error)
    } finally {
      setIsActivating(false)
    }
  }

  const handleGoToDashboard = () => {
    navigate('/dashboard')
  }

  const handleCustomizeSettings = () => {
    navigate('/settings')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Setup Complete!</h1>
              <p className="text-gray-600">Your AI social media automation is ready to launch</p>
            </div>
            <div className="text-sm text-gray-500">
              Step 4 of 4 ✓
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success Header */}
        <div className="text-center mb-12">
          <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
            <Trophy className="w-10 h-10 text-green-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            🎉 Congratulations, {user?.name || 'there'}!
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Your AI-powered social media automation platform is ready to transform your online presence!
          </p>
        </div>

        {/* Setup Progress */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-6">Setup Progress</h3>
          <div className="space-y-4">
            {setupSteps.map((step, index) => (
              <div key={index} className="flex items-center space-x-4">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  index <= currentStep 
                    ? 'bg-green-100 text-green-600' 
                    : 'bg-gray-100 text-gray-400'
                }`}>
                  <step.icon className="w-5 h-5" />
                </div>
                <div className={`font-medium ${
                  index <= currentStep ? 'text-gray-900' : 'text-gray-500'
                }`}>
                  {step.title}
                </div>
                {index <= currentStep && (
                  <CheckCircle className="w-5 h-5 text-green-600" />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Setup Summary */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-6">Your Setup Summary</h3>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{stats.platformsConnected}</div>
              <div className="text-sm text-blue-800">Platforms Connected</div>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{stats.domainsSelected}</div>
              <div className="text-sm text-green-800">Content Domains</div>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{stats.estimatedPosts}</div>
              <div className="text-sm text-purple-800">Posts per Day</div>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{stats.estimatedReach.toLocaleString()}</div>
              <div className="text-sm text-orange-800">Est. Daily Reach</div>
            </div>
          </div>

          <div className="text-center p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Sparkles className="w-5 h-5 text-green-600" />
              <span className="font-semibold text-gray-900">Estimated Impact</span>
            </div>
            <p className="text-sm text-gray-700">
              Save <strong>10+ hours/week</strong> • Increase engagement by <strong>3x</strong> • 
              Grow your following <strong>50% faster</strong>
            </p>
          </div>
        </div>

        {/* Features Ready */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-6">✨ What's Ready for You</h3>
          
          <div className="grid md:grid-cols-2 gap-6">
            {features.map((feature, index) => (
              <div key={index} className="flex items-start space-x-4 p-4 border border-gray-100 rounded-lg">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <feature.icon className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900 mb-1">{feature.title}</h4>
                  <p className="text-sm text-gray-600">{feature.description}</p>
                  <span className="inline-flex items-center mt-2 text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                    <CheckCircle className="w-3 h-3 mr-1" />
                    Ready
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* What Happens Next */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg text-white p-6 mb-8">
          <h3 className="font-semibold mb-4">🚀 What Happens Next?</h3>
          <div className="grid md:grid-cols-3 gap-6 text-sm">
            <div>
              <div className="font-medium mb-2">🤖 AI Starts Working</div>
              <p className="text-blue-100">
                Your AI will begin analyzing trends and generating content within minutes
              </p>
            </div>
            <div>
              <div className="font-medium mb-2">📅 Content Goes Live</div>
              <p className="text-blue-100">
                First posts will appear on your platforms within 24 hours
              </p>
            </div>
            <div>
              <div className="font-medium mb-2">📈 Track & Optimize</div>
              <p className="text-blue-100">
                Monitor performance and let AI optimize for better results
              </p>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
          <h3 className="font-semibold text-gray-900 mb-6">🎯 Recommended Next Steps</h3>
          
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 border border-gray-100 rounded-lg">
              <div className="flex items-center space-x-3">
                <PlayCircle className="w-5 h-5 text-blue-600" />
                <div>
                  <div className="font-medium text-gray-900">Activate AI Automation</div>
                  <div className="text-sm text-gray-600">Start your content generation immediately</div>
                </div>
              </div>
              <Button
                onClick={handleActivateAI}
                disabled={isActivating}
                className="px-6"
              >
                {isActivating ? 'Activating...' : 'Activate Now'}
              </Button>
            </div>

            <div className="flex items-center justify-between p-4 border border-gray-100 rounded-lg">
              <div className="flex items-center space-x-3">
                <BarChart3 className="w-5 h-5 text-green-600" />
                <div>
                  <div className="font-medium text-gray-900">Visit Your Dashboard</div>
                  <div className="text-sm text-gray-600">Monitor your AI's performance and analytics</div>
                </div>
              </div>
              <Button
                onClick={handleGoToDashboard}
                variant="outline"
                className="px-6"
              >
                Go to Dashboard
              </Button>
            </div>

            <div className="flex items-center justify-between p-4 border border-gray-100 rounded-lg">
              <div className="flex items-center space-x-3">
                <Settings className="w-5 h-5 text-purple-600" />
                <div>
                  <div className="font-medium text-gray-900">Customize Settings</div>
                  <div className="text-sm text-gray-600">Fine-tune your content preferences</div>
                </div>
              </div>
              <Button
                onClick={handleCustomizeSettings}
                variant="outline"
                className="px-6"
              >
                Customize
              </Button>
            </div>
          </div>
        </div>

        {/* Main CTA */}
        <div className="text-center">
          <Button
            onClick={handleActivateAI}
            disabled={isActivating}
            size="lg"
            className="px-8 py-4 text-lg"
          >
            {isActivating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3" />
                Activating AI...
              </>
            ) : (
              <>
                🚀 Activate AI & Start Growing
                <ArrowRight className="w-5 h-5 ml-2" />
              </>
            )}
          </Button>
          
          <p className="text-sm text-gray-500 mt-4">
            Your AI will start working immediately after activation
          </p>
        </div>

        {/* Support */}
        <div className="text-center mt-12 p-6 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">Need Help Getting Started?</h4>
          <p className="text-gray-600 text-sm mb-4">
            Our support team is here to help you maximize your results
          </p>
          <div className="flex justify-center space-x-4">
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              📖 View Quick Start Guide
            </button>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              💬 Contact Support
            </button>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              🎥 Watch Tutorial Videos
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Complete