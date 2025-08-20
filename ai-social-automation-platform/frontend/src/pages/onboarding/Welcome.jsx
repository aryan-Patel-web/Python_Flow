import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, Bot, Zap, TrendingUp, Users, CheckCircle } from 'lucide-react'
import Button from '../../components/common/Button'
import { useAuth } from '../../context/AuthContext'
import useToast from '../../hooks/useToast'

const Welcome = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { success } = useToast()
  const [currentStep, setCurrentStep] = useState(0)

  const features = [
    {
      icon: Bot,
      title: 'AI-Powered Content Creation',
      description: 'Our AI generates engaging content tailored to your brand voice and audience preferences.',
      color: 'text-blue-600 bg-blue-100'
    },
    {
      icon: Zap,
      title: 'Complete Automation',
      description: 'Set it and forget it. Our platform handles posting, scheduling, and optimization automatically.',
      color: 'text-purple-600 bg-purple-100'
    },
    {
      icon: TrendingUp,
      title: 'Smart Analytics',
      description: 'Track your growth with detailed analytics and insights to improve your social media strategy.',
      color: 'text-green-600 bg-green-100'
    },
    {
      icon: Users,
      title: 'Multi-Platform Support',
      description: 'Manage all your social media accounts from one powerful dashboard.',
      color: 'text-orange-600 bg-orange-100'
    }
  ]

  const steps = [
    'Choose Your Plan',
    'Connect Platforms', 
    'Select Content Domains',
    'Start Automation'
  ]

  const handleGetStarted = () => {
    success('Welcome to AI Social! Let\'s get you set up.')
    navigate('/onboarding/plan-selection')
  }

  const handleSkip = () => {
    navigate('/dashboard')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Social Automation</h1>
                <p className="text-sm text-gray-500">Setup Wizard</p>
              </div>
            </div>
            <button 
              onClick={handleSkip}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Skip for now
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Progress Steps */}
        <div className="mb-12">
          <div className="flex items-center justify-center space-x-4">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  index === 0 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-200 text-gray-600'
                }`}>
                  {index < 0 ? <CheckCircle className="w-5 h-5" /> : index + 1}
                </div>
                {index < steps.length - 1 && (
                  <div className="w-12 h-1 bg-gray-200 mx-2" />
                )}
              </div>
            ))}
          </div>
          <div className="flex justify-center mt-4">
            <span className="text-sm text-gray-600">Step 1 of {steps.length}</span>
          </div>
        </div>

        {/* Welcome Content */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Welcome to the Future of 
            <span className="text-blue-600"> Social Media</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Hello {user?.name || 'there'}! 👋 Let's set up your AI-powered social media automation platform. 
            In just a few minutes, you'll have AI managing all your social media accounts.
          </p>
          
          {/* Key Benefits */}
          <div className="grid md:grid-cols-3 gap-6 mb-12 max-w-4xl mx-auto">
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
              <div className="text-3xl mb-3">⏱️</div>
              <h3 className="font-semibold text-gray-900 mb-2">Save 10+ Hours/Week</h3>
              <p className="text-gray-600 text-sm">Let AI handle content creation, posting, and engagement</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
              <div className="text-3xl mb-3">📈</div>
              <h3 className="font-semibold text-gray-900 mb-2">Grow 3x Faster</h3>
              <p className="text-gray-600 text-sm">AI-optimized content and timing for maximum engagement</p>
            </div>
            <div className="bg-white rounded-lg p-6 shadow-sm border border-gray-100">
              <div className="text-3xl mb-3">🎯</div>
              <h3 className="font-semibold text-gray-900 mb-2">100% Consistent</h3>
              <p className="text-gray-600 text-sm">Never miss a post with 24/7 automated publishing</p>
            </div>
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          {features.map((feature, index) => (
            <div 
              key={index}
              className="bg-white rounded-xl p-8 shadow-sm border border-gray-100 hover:shadow-md transition-shadow"
            >
              <div className={`w-12 h-12 rounded-lg ${feature.color} flex items-center justify-center mb-4`}>
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
              <p className="text-gray-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* How It Works */}
        <div className="bg-white rounded-2xl p-8 md:p-12 shadow-sm border border-gray-100 mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-12">How It Works</h2>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              { step: '1', title: 'Connect Accounts', desc: 'Securely link your social media platforms' },
              { step: '2', title: 'Choose Content', desc: 'Select topics and content types you want' },
              { step: '3', title: 'AI Creates', desc: 'Our AI generates engaging posts automatically' },
              { step: '4', title: 'Auto Posts', desc: 'Content goes live at optimal times' }
            ].map((item, index) => (
              <div key={index} className="text-center">
                <div className="w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-lg mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-600 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Testimonial */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 md:p-12 text-white text-center mb-16">
          <div className="max-w-3xl mx-auto">
            <div className="text-6xl mb-6">💬</div>
            <blockquote className="text-xl md:text-2xl font-medium mb-6 leading-relaxed">
              "This platform saved me 15 hours a week and tripled my engagement. The AI creates content that perfectly matches my brand voice!"
            </blockquote>
            <div className="flex items-center justify-center space-x-4">
              <div className="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <span className="text-lg">👤</span>
              </div>
              <div className="text-left">
                <div className="font-semibold">Sarah Johnson</div>
                <div className="text-blue-200">Digital Marketing Agency Owner</div>
              </div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <h2 className="text-3xl font-bold text-gray-900 mb-6">Ready to Transform Your Social Media?</h2>
          <p className="text-xl text-gray-600 mb-8">
            Join thousands of creators and businesses already using AI to grow their online presence.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-4">
            <Button 
              onClick={handleGetStarted}
              size="lg"
              className="px-8 py-4 text-lg"
            >
              Get Started Now
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <button 
              onClick={handleSkip}
              className="text-gray-500 hover:text-gray-700 font-medium"
            >
              I'll set this up later
            </button>
          </div>
          
          <p className="text-sm text-gray-500 mt-6">
            ✨ Free 7-day trial • No credit card required • Cancel anytime
          </p>
        </div>
      </div>
    </div>
  )
}

export default Welcome