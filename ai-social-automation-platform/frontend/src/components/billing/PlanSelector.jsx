import React, { useState } from 'react';
import { Check, X, Crown, Zap, Users, Star, ArrowRight } from 'lucide-react';

const PlanSelector = ({ 
  onPlanSelect, 
  currentPlan = null, 
  loading = false,
  showAnnualToggle = true 
}) => {
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [selectedPlan, setSelectedPlan] = useState(null);

  const plans = [
    {
      id: 'free',
      name: 'Free',
      description: 'Perfect for getting started',
      monthlyPrice: 0,
      annualPrice: 0,
      icon: Users,
      color: 'gray',
      features: [
        { text: '3 connected accounts', included: true },
        { text: '50 posts per month', included: true },
        { text: 'Basic analytics', included: true },
        { text: 'Email support', included: true },
        { text: 'Advanced scheduling', included: false },
        { text: 'AI content optimization', included: false },
        { text: 'Team collaboration', included: false },
        { text: 'Custom integrations', included: false }
      ],
      limits: {
        accounts: 3,
        posts: 50,
        storage: '1 GB',
        support: 'Email'
      },
      cta: 'Get Started'
    },
    {
      id: 'pro',
      name: 'Pro',
      description: 'Best for growing businesses',
      monthlyPrice: 29.99,
      annualPrice: 299.99, // ~$25/month
      icon: Zap,
      color: 'blue',
      popular: true,
      features: [
        { text: '10 connected accounts', included: true },
        { text: '500 posts per month', included: true },
        { text: 'Advanced analytics', included: true },
        { text: 'Priority support', included: true },
        { text: 'Advanced scheduling', included: true },
        { text: 'AI content optimization', included: true },
        { text: 'Team collaboration', included: false },
        { text: 'Custom integrations', included: false }
      ],
      limits: {
        accounts: 10,
        posts: 500,
        storage: '10 GB',
        support: 'Priority'
      },
      cta: 'Start Pro Trial',
      trialDays: 14
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      description: 'For large teams and agencies',
      monthlyPrice: 99.99,
      annualPrice: 999.99, // ~$83/month
      icon: Crown,
      color: 'purple',
      features: [
        { text: 'Unlimited accounts', included: true },
        { text: 'Unlimited posts', included: true },
        { text: 'Advanced analytics & reporting', included: true },
        { text: 'Dedicated support', included: true },
        { text: 'Advanced scheduling', included: true },
        { text: 'AI content optimization', included: true },
        { text: 'Team collaboration', included: true },
        { text: 'Custom integrations', included: true }
      ],
      limits: {
        accounts: 'Unlimited',
        posts: 'Unlimited',
        storage: 'Unlimited',
        support: 'Dedicated'
      },
      cta: 'Contact Sales'
    }
  ];

  const getPrice = (plan) => {
    return billingCycle === 'annual' ? plan.annualPrice : plan.monthlyPrice;
  };

  const getMonthlyPrice = (plan) => {
    return billingCycle === 'annual' ? plan.annualPrice / 12 : plan.monthlyPrice;
  };

  const getSavings = (plan) => {
    if (billingCycle === 'monthly' || plan.monthlyPrice === 0) return 0;
    const monthlyTotal = plan.monthlyPrice * 12;
    return monthlyTotal - plan.annualPrice;
  };

  const handlePlanSelect = (plan) => {
    setSelectedPlan(plan.id);
    onPlanSelect({
      planId: plan.id,
      billingCycle,
      price: getPrice(plan)
    });
  };

  const getColorClasses = (color, variant = 'background') => {
    const colorMap = {
      gray: {
        background: 'bg-gray-50 border-gray-200',
        button: 'bg-gray-600 hover:bg-gray-700',
        text: 'text-gray-600',
        icon: 'text-gray-500'
      },
      blue: {
        background: 'bg-blue-50 border-blue-200',
        button: 'bg-blue-600 hover:bg-blue-700',
        text: 'text-blue-600',
        icon: 'text-blue-500'
      },
      purple: {
        background: 'bg-purple-50 border-purple-200',
        button: 'bg-purple-600 hover:bg-purple-700',
        text: 'text-purple-600',
        icon: 'text-purple-500'
      }
    };
    return colorMap[color]?.[variant] || colorMap.gray[variant];
  };

  const isCurrentPlan = (planId) => {
    return currentPlan?.id === planId || currentPlan?.plan_name?.toLowerCase() === planId;
  };

  return (
    <div className="w-full max-w-7xl mx-auto">
      {/* Billing Toggle */}
      {showAnnualToggle && (
        <div className="flex justify-center mb-8">
          <div className="bg-gray-100 p-1 rounded-lg flex items-center">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                billingCycle === 'monthly'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors relative ${
                billingCycle === 'annual'
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              Annual
              <span className="absolute -top-2 -right-2 bg-green-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                Save 20%
              </span>
            </button>
          </div>
        </div>
      )}

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => {
          const Icon = plan.icon;
          const price = getPrice(plan);
          const monthlyPrice = getMonthlyPrice(plan);
          const savings = getSavings(plan);
          const currentPlanCheck = isCurrentPlan(plan.id);
          
          return (
            <div
              key={plan.id}
              className={`relative bg-white border-2 rounded-2xl p-8 transition-all hover:shadow-xl ${
                plan.popular 
                  ? 'border-blue-500 shadow-lg transform scale-105' 
                  : currentPlanCheck
                    ? 'border-green-500'
                    : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              {/* Popular Badge */}
              {plan.popular && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-full text-sm font-medium flex items-center">
                    <Star className="w-4 h-4 mr-1" />
                    Most Popular
                  </div>
                </div>
              )}

              {/* Current Plan Badge */}
              {currentPlanCheck && (
                <div className="absolute -top-4 right-4">
                  <div className="bg-green-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                    Current Plan
                  </div>
                </div>
              )}

              {/* Plan Header */}
              <div className="text-center mb-8">
                <div className={`w-16 h-16 mx-auto rounded-full flex items-center justify-center mb-4 ${getColorClasses(plan.color, 'background')}`}>
                  <Icon className={`w-8 h-8 ${getColorClasses(plan.color, 'icon')}`} />
                </div>
                
                <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                <p className="text-gray-600 mb-4">{plan.description}</p>
                
                {/* Pricing */}
                <div className="mb-4">
                  {price === 0 ? (
                    <div className="text-4xl font-bold text-gray-900">Free</div>
                  ) : (
                    <div>
                      <div className="text-4xl font-bold text-gray-900">
                        ${monthlyPrice.toFixed(0)}
                        <span className="text-lg font-normal text-gray-600">/month</span>
                      </div>
                      {billingCycle === 'annual' && (
                        <div className="text-sm text-gray-600">
                          Billed annually (${price.toFixed(0)}/year)
                        </div>
                      )}
                    </div>
                  )}
                  
                  {savings > 0 && (
                    <div className="text-sm text-green-600 font-medium mt-1">
                      Save ${savings.toFixed(0)}/year
                    </div>
                  )}
                </div>
              </div>

              {/* Features List */}
              <div className="space-y-4 mb-8">
                {plan.features.map((feature, index) => (
                  <div key={index} className="flex items-start">
                    {feature.included ? (
                      <Check className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    ) : (
                      <X className="w-5 h-5 text-gray-300 flex-shrink-0 mt-0.5" />
                    )}
                    <span className={`ml-3 text-sm ${
                      feature.included ? 'text-gray-700' : 'text-gray-400'
                    }`}>
                      {feature.text}
                    </span>
                  </div>
                ))}
              </div>

              {/* Limits Summary */}
              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h4 className="text-sm font-medium text-gray-900 mb-3">Plan Limits</h4>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Accounts:</span>
                    <span className="font-medium">{plan.limits.accounts}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Posts:</span>
                    <span className="font-medium">{plan.limits.posts}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Storage:</span>
                    <span className="font-medium">{plan.limits.storage}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Support:</span>
                    <span className="font-medium">{plan.limits.support}</span>
                  </div>
                </div>
              </div>

              {/* CTA Button */}
              <button
                onClick={() => handlePlanSelect(plan)}
                disabled={loading || selectedPlan === plan.id || currentPlanCheck}
                className={`w-full py-3 px-6 rounded-lg font-medium transition-all flex items-center justify-center ${
                  currentPlanCheck
                    ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                    : selectedPlan === plan.id
                      ? 'bg-gray-400 text-white cursor-not-allowed'
                      : plan.popular
                        ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg'
                        : `${getColorClasses(plan.color, 'button')} text-white`
                }`}
              >
                {currentPlanCheck ? (
                  'Current Plan'
                ) : selectedPlan === plan.id ? (
                  'Processing...'
                ) : (
                  <>
                    {plan.cta}
                    {plan.trialDays && <span className="ml-2 text-sm">({plan.trialDays} days free)</span>}
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </button>

              {/* Trial Notice */}
              {plan.trialDays && !currentPlanCheck && (
                <p className="text-xs text-gray-500 text-center mt-2">
                  No credit card required for trial
                </p>
              )}
            </div>
          );
        })}
      </div>

      {/* Feature Comparison Table */}
      <div className="mt-16 bg-white rounded-lg border overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b">
          <h3 className="text-lg font-semibold text-gray-900">Feature Comparison</h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Feature
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Free
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Pro
                </th>
                <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Enterprise
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {[
                ['Connected Accounts', '3', '10', 'Unlimited'],
                ['Monthly Posts', '50', '500', 'Unlimited'],
                ['AI Content Generation', '100', '1,000', 'Unlimited'],
                ['Analytics Dashboard', '✓', '✓', '✓'],
                ['Advanced Analytics', '✗', '✓', '✓'],
                ['Priority Support', '✗', '✓', '✓'],
                ['Team Collaboration', '✗', '✗', '✓'],
                ['Custom Integrations', '✗', '✗', '✓'],
                ['White-label Options', '✗', '✗', '✓']
              ].map(([feature, free, pro, enterprise], index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {feature}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
                    {free}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
                    {pro}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 text-center">
                    {enterprise}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Money-back Guarantee */}
      <div className="mt-8 text-center">
        <p className="text-sm text-gray-600">
          🛡️ 30-day money-back guarantee • Cancel anytime • No setup fees
        </p>
      </div>
    </div>
  );
};

export default PlanSelector;