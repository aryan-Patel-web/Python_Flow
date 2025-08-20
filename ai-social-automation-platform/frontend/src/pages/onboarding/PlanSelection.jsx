import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, ArrowLeft, Check, Star, Zap, Crown, Users } from 'lucide-react'
import Button from '../../components/common/Button'
import { useAuth } from '../../context/AuthContext'
import useToast from '../../hooks/useToast'

const PlanSelection = () => {
  const navigate = useNavigate()
  const { user } = useAuth()
  const { success } = useToast()
  const [selectedPlan, setSelectedPlan] = useState('pro')
  const [billingCycle, setBillingCycle] = useState('monthly')

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      icon: Users,
      description: 'Perfect for individuals getting started',
      monthly: 29,
      yearly: 290,
      savings: 'Save $58',
      features: [
        '2 social media platforms',
        '3 posts per day',
        'Basic content domains',
        'Standard support',
        'Basic analytics'
      ],
      limitations: [
        'Limited to 2 platforms',
        'No premium domains',
        'Basic templates only'
      ],
      popular: false,
      color: 'border-gray-200',
      buttonStyle: 'outline'
    },
    {
      id: 'pro',
      name: 'Pro',
      icon: Zap,
      description: 'Most popular for growing businesses',
      monthly: 79,
      yearly: 790,
      savings: 'Save $158',
      features: [
        '5 social media platforms',
        '6 posts per day',
        'All content domains',
        'Priority support',
        'Advanced analytics',
        'Custom scheduling',
        'Content optimization',
        'Engagement tracking'
      ],
      limitations: [],
      popular: true,
      color: 'border-blue-500',
      buttonStyle: 'primary'
    },
    {
      id: 'agency',
      name: 'Agency',
      icon: Crown,
      description: 'For agencies and power users',
      monthly: 299,
      yearly: 2990,
      savings: 'Save $598',
      features: [
        'Unlimited platforms',
        'Unlimited posts',
        'All premium domains',
        '24/7 priority support',
        'Advanced analytics & reports',
        'White-label options',
        'API access',
        'Team collaboration',
        'Custom integrations',
        'Dedicated account manager'
      ],
      limitations: [],
      popular: false,
      color: 'border-purple-500',
      buttonStyle: 'primary'
    }
  ]

  const handlePlanSelect = (planId) => {
    setSelectedPlan(planId)
  }

  const handleContinue = () => {
    const plan = plans.find(p => p.id === selectedPlan)
    success(`${plan.name} plan selected! Let's connect your platforms.`)
    navigate('/onboarding/credentials-setup')
  }

  const handleBack = () => {
    navigate('/onboarding/welcome')
  }

  const getPrice = (plan) => {
    const price = billingCycle === 'monthly' ? plan.monthly : plan.yearly
    const period = billingCycle === 'monthly' ? 'month' : 'year'
    return { price, period }
  }

  const getMonthlyPrice = (plan) => {
    return billingCycle === 'yearly' ? plan.yearly / 12 : plan.monthly
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Choose Your Plan</h1>
              <p className="text-gray-600">Select the plan that best fits your needs</p>
            </div>
            <div className="text-sm text-gray-500">
              Step 1 of 4
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Billing Toggle */}
        <div className="text-center mb-8">
          <div className="inline-flex bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                billingCycle === 'monthly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('yearly')}
              className={`px-6 py-2 rounded-md text-sm font-medium transition-colors ${
                billingCycle === 'yearly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Yearly
              <span className="ml-2 px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </div>

        {/* Plans Grid */}
        <div className="grid lg:grid-cols-3 gap-8 mb-8">
          {plans.map((plan) => {
            const { price, period } = getPrice(plan)
            const monthlyPrice = getMonthlyPrice(plan)
            const isSelected = selectedPlan === plan.id

            return (
              <div
                key={plan.id}
                onClick={() => handlePlanSelect(plan.id)}
                className={`relative bg-white rounded-xl border-2 p-8 cursor-pointer transition-all ${
                  isSelected ? plan.color : 'border-gray-200 hover:border-gray-300'
                } ${plan.popular ? 'ring-2 ring-blue-500 ring-opacity-50' : ''}`}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <div className="bg-blue-600 text-white px-4 py-1 rounded-full text-sm font-medium flex items-center">
                      <Star className="w-4 h-4 mr-1" />
                      Most Popular
                    </div>
                  </div>
                )}

                {/* Selected Indicator */}
                {isSelected && (
                  <div className="absolute top-4 right-4">
                    <div className="w-6 h-6 bg-blue-600 rounded-full flex items-center justify-center">
                      <Check className="w-4 h-4 text-white" />
                    </div>
                  </div>
                )}

                {/* Plan Header */}
                <div className="text-center mb-6">
                  <div className={`w-12 h-12 rounded-lg flex items-center justify-center mx-auto mb-4 ${
                    plan.id === 'starter' ? 'bg-gray-100 text-gray-600' :
                    plan.id === 'pro' ? 'bg-blue-100 text-blue-600' :
                    'bg-purple-100 text-purple-600'
                  }`}>
                    <plan.icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 text-sm">{plan.description}</p>
                </div>

                {/* Pricing */}
                <div className="text-center mb-6">
                  <div className="flex items-baseline justify-center mb-2">
                    <span className="text-4xl font-bold text-gray-900">${price}</span>
                    <span className="text-gray-500 ml-1">/{period}</span>
                  </div>
                  {billingCycle === 'yearly' && (
                    <div className="text-sm text-green-600 font-medium">{plan.savings}</div>
                  )}
                  <div className="text-sm text-gray-500">
                    ${monthlyPrice.toFixed(0)} per month
                  </div>
                </div>

                {/* Features */}
                <div className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <div key={index} className="flex items-start">
                      <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                      <span className="text-gray-700 text-sm">{feature}</span>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <Button
                  variant={isSelected ? 'primary' : plan.buttonStyle}
                  className="w-full"
                  onClick={() => handlePlanSelect(plan.id)}
                >
                  {isSelected ? 'Selected' : `Choose ${plan.name}`}
                </Button>

                {/* Trial Note */}
                {plan.id !== 'starter' && (
                  <p className="text-center text-xs text-gray-500 mt-3">
                    🎁 7-day free trial included
                  </p>
                )}
              </div>
            )
          })}
        </div>

        {/* Feature Comparison */}
        <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">What's included in each plan?</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 font-medium text-gray-900">Features</th>
                  <th className="text-center py-3 font-medium text-gray-900">Starter</th>
                  <th className="text-center py-3 font-medium text-gray-900">Pro</th>
                  <th className="text-center py-3 font-medium text-gray-900">Agency</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {[
                  { feature: 'Social Media Platforms', starter: '2', pro: '5', agency: 'Unlimited' },
                  { feature: 'Posts per Day', starter: '3', pro: '6', agency: 'Unlimited' },
                  { feature: 'Content Domains', starter: 'Basic', pro: 'All', agency: 'All + Premium' },
                  { feature: 'Analytics', starter: 'Basic', pro: 'Advanced', agency: 'Enterprise' },
                  { feature: 'Support', starter: 'Standard', pro: 'Priority', agency: '24/7 + Dedicated' },
                  { feature: 'API Access', starter: '✗', pro: '✗', agency: '✓' },
                  { feature: 'White-label', starter: '✗', pro: '✗', agency: '✓' }
                ].map((row, index) => (
                  <tr key={index}>
                    <td className="py-3 text-gray-700">{row.feature}</td>
                    <td className="py-3 text-center text-gray-600">{row.starter}</td>
                    <td className="py-3 text-center text-gray-600">{row.pro}</td>
                    <td className="py-3 text-center text-gray-600">{row.agency}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Trust Indicators */}
        <div className="bg-blue-50 rounded-lg p-6 mb-8">
          <div className="text-center">
            <h3 className="font-semibold text-blue-900 mb-4">Why choose AI Social Automation?</h3>
            <div className="grid md:grid-cols-3 gap-6 text-sm">
              <div>
                <div className="text-2xl mb-2">⚡</div>
                <h4 className="font-medium text-blue-800">Lightning Fast Setup</h4>
                <p className="text-blue-700">Get started in under 5 minutes</p>
              </div>
              <div>
                <div className="text-2xl mb-2">🛡️</div>
                <h4 className="font-medium text-blue-800">Enterprise Security</h4>
                <p className="text-blue-700">Bank-level encryption for your data</p>
              </div>
              <div>
                <div className="text-2xl mb-2">📈</div>
                <h4 className="font-medium text-blue-800">Proven Results</h4>
                <p className="text-blue-700">3x faster growth on average</p>
              </div>
            </div>
          </div>
        </div>

        {/* Money-back Guarantee */}
        <div className="text-center bg-green-50 rounded-lg p-6 mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 rounded-full mb-4">
            <Check className="w-6 h-6 text-green-600" />
          </div>
          <h3 className="font-semibold text-green-900 mb-2">30-Day Money-Back Guarantee</h3>
          <p className="text-green-700 text-sm">
            Not satisfied? Get a full refund within 30 days, no questions asked.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex justify-between items-center">
          <Button
            onClick={handleBack}
            variant="outline"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          <div className="flex space-x-4">
            <Button
              onClick={() => navigate('/onboarding/credentials-setup')}
              variant="outline"
            >
              Skip for now
            </Button>
            <Button
              onClick={handleContinue}
            >
              Continue with {plans.find(p => p.id === selectedPlan)?.name}
              <ArrowRight className="w-4 h-4 ml-2" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default PlanSelection