import React, { useState, useEffect } from 'react';
import { Check, X, CreditCard, Download, Star, ArrowRight, Shield, Zap, Users, BarChart3, Globe, Clock, AlertCircle, Calendar } from 'lucide-react';

const BillingPage = () => {
  const [currentPlan, setCurrentPlan] = useState('pro');
  const [billingCycle, setBillingCycle] = useState('monthly');
  const [loading, setLoading] = useState(false);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [selectedNewPlan, setSelectedNewPlan] = useState(null);

  // Simulate loading user billing data
  useEffect(() => {
    // In real app, fetch from API
    setCurrentPlan('pro');
  }, []);

  const plans = [
    {
      id: 'starter',
      name: 'Starter',
      description: 'Perfect for individuals and small businesses',
      price: { monthly: 29, yearly: 290 },
      yearlyDiscount: '17%',
      features: [
        '5 social media platforms',
        '50 posts per month',
        'Basic analytics',
        'Email support',
        '1 team member',
        'Content calendar',
        'Basic automation'
      ],
      limitations: [
        'No advanced AI features',
        'Limited analytics',
        'No white-label options'
      ],
      popular: false,
      color: 'border-gray-200'
    },
    {
      id: 'pro',
      name: 'Pro',
      description: 'Best for growing businesses and teams',
      price: { monthly: 79, yearly: 790 },
      yearlyDiscount: '16%',
      features: [
        '15 social media platforms',
        '500 posts per month',
        'Advanced analytics & reporting',
        'Priority support',
        '5 team members',
        'Advanced automation',
        'AI content generation',
        'Custom scheduling',
        'Brand voice training',
        'Performance insights'
      ],
      limitations: [
        'Limited white-label options'
      ],
      popular: true,
      color: 'border-blue-500'
    },
    {
      id: 'agency',
      name: 'Agency',
      description: 'For agencies and large teams',
      price: { monthly: 199, yearly: 1990 },
      yearlyDiscount: '16%',
      features: [
        'Unlimited platforms',
        'Unlimited posts',
        'Advanced analytics & white-label reports',
        'Dedicated account manager',
        'Unlimited team members',
        'Custom integrations',
        'API access',
        'White-label solution',
        'Advanced AI features',
        'Custom automation workflows',
        'Priority phone support',
        'Custom onboarding'
      ],
      limitations: [],
      popular: false,
      color: 'border-purple-500'
    }
  ];

  const currentPlanDetails = plans.find(p => p.id === currentPlan);
  const nextBillingDate = new Date();
  nextBillingDate.setMonth(nextBillingDate.getMonth() + 1);

  const usageStats = {
    posts: { used: 342, limit: currentPlanDetails?.id === 'starter' ? 50 : currentPlanDetails?.id === 'pro' ? 500 : 'Unlimited' },
    platforms: { used: 8, limit: currentPlanDetails?.id === 'starter' ? 5 : currentPlanDetails?.id === 'pro' ? 15 : 'Unlimited' },
    teamMembers: { used: 3, limit: currentPlanDetails?.id === 'starter' ? 1 : currentPlanDetails?.id === 'pro' ? 5 : 'Unlimited' }
  };

  const invoices = [
    { id: 'INV-001', date: '2024-01-15', amount: 79, status: 'paid', plan: 'Pro Plan' },
    { id: 'INV-002', date: '2023-12-15', amount: 79, status: 'paid', plan: 'Pro Plan' },
    { id: 'INV-003', date: '2023-11-15', amount: 79, status: 'paid', plan: 'Pro Plan' }
  ];

  const handlePlanChange = (planId) => {
    if (planId === currentPlan) return;
    setSelectedNewPlan(planId);
    setShowPaymentModal(true);
  };

  const handlePayment = async () => {
    setLoading(true);
    // Simulate payment processing
    await new Promise(resolve => setTimeout(resolve, 2000));
    setCurrentPlan(selectedNewPlan);
    setShowPaymentModal(false);
    setSelectedNewPlan(null);
    setLoading(false);
  };

  const calculateSavings = (plan) => {
    const monthly = plan.price.monthly * 12;
    const yearly = plan.price.yearly;
    return monthly - yearly;
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Billing & Subscription</h1>
          <p className="text-gray-600 mt-2">Manage your subscription and billing preferences</p>
        </div>
        <button className="flex items-center space-x-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          <Download className="w-4 h-4" />
          <span>Download Invoice</span>
        </button>
      </div>

      {/* Current Plan Overview */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Current Plan</h2>
            <p className="text-gray-600">Your active subscription details</p>
          </div>
          <div className="text-right">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="text-green-600 font-medium">Active</span>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Star className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900">{currentPlanDetails?.name} Plan</h3>
                <p className="text-gray-600">${currentPlanDetails?.price[billingCycle]}/{billingCycle === 'monthly' ? 'month' : 'year'}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <Calendar className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700">Next Billing</h3>
                <p className="text-lg font-semibold text-gray-900">{nextBillingDate.toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <CreditCard className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <h3 className="text-sm font-medium text-gray-700">Payment Method</h3>
                <p className="text-lg font-semibold text-gray-900">•••• 4242</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Usage Statistics */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Usage This Month</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Posts Published</span>
              <span className="text-sm text-gray-600">{usageStats.posts.used} / {usageStats.posts.limit}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300" 
                style={{ 
                  width: usageStats.posts.limit === 'Unlimited' ? '0%' : `${(usageStats.posts.used / usageStats.posts.limit) * 100}%` 
                }}
              ></div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Platforms Connected</span>
              <span className="text-sm text-gray-600">{usageStats.platforms.used} / {usageStats.platforms.limit}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-green-600 h-2 rounded-full transition-all duration-300" 
                style={{ 
                  width: usageStats.platforms.limit === 'Unlimited' ? '0%' : `${(usageStats.platforms.used / usageStats.platforms.limit) * 100}%` 
                }}
              ></div>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Team Members</span>
              <span className="text-sm text-gray-600">{usageStats.teamMembers.used} / {usageStats.teamMembers.limit}</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-purple-600 h-2 rounded-full transition-all duration-300" 
                style={{ 
                  width: usageStats.teamMembers.limit === 'Unlimited' ? '0%' : `${(usageStats.teamMembers.used / usageStats.teamMembers.limit) * 100}%` 
                }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Billing Cycle Toggle */}
      <div className="flex items-center justify-center">
        <div className="bg-gray-100 rounded-lg p-1">
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
            <span>Yearly</span>
            <span className="ml-2 text-green-600 font-semibold">(Save up to 17%)</span>
          </button>
        </div>
      </div>

      {/* Plans Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {plans.map((plan) => (
          <div
            key={plan.id}
            className={`bg-white rounded-xl shadow-sm border-2 p-6 relative ${
              currentPlan === plan.id ? plan.color + ' ring-2 ring-offset-2 ring-blue-500' : plan.color
            } ${plan.popular ? 'transform scale-105' : ''}`}
          >
            {plan.popular && (
              <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-xs font-medium">
                  Most Popular
                </span>
              </div>
            )}

            {currentPlan === plan.id && (
              <div className="absolute -top-3 right-4">
                <span className="bg-green-600 text-white px-3 py-1 rounded-full text-xs font-medium flex items-center space-x-1">
                  <Check className="w-3 h-3" />
                  <span>Current</span>
                </span>
              </div>
            )}

            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
              <p className="text-gray-600 mt-1">{plan.description}</p>
              <div className="mt-4">
                <span className="text-4xl font-bold text-gray-900">
                  ${plan.price[billingCycle]}
                </span>
                <span className="text-gray-600">/{billingCycle === 'monthly' ? 'month' : 'year'}</span>
              </div>
              {billingCycle === 'yearly' && (
                <div className="mt-2">
                  <span className="text-green-600 text-sm font-medium">
                    Save ${calculateSavings(plan)} per year
                  </span>
                </div>
              )}
            </div>

            <ul className="space-y-3 mb-6">
              {plan.features.map((feature, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <Check className="w-5 h-5 text-green-500 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{feature}</span>
                </li>
              ))}
              {plan.limitations.map((limitation, index) => (
                <li key={index} className="flex items-start space-x-3">
                  <X className="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-gray-500">{limitation}</span>
                </li>
              ))}
            </ul>

            <button
              onClick={() => handlePlanChange(plan.id)}
              disabled={currentPlan === plan.id}
              className={`w-full py-3 rounded-lg font-medium transition-colors ${
                currentPlan === plan.id
                  ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                  : plan.popular
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-900 text-white hover:bg-gray-800'
              }`}
            >
              {currentPlan === plan.id ? 'Current Plan' : `Upgrade to ${plan.name}`}
            </button>
          </div>
        ))}
      </div>

      {/* Payment Method */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Payment Method</h2>
          <button className="text-blue-600 hover:text-blue-700 font-medium">
            Update Payment
          </button>
        </div>

        <div className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
          <div className="w-12 h-8 bg-blue-600 rounded flex items-center justify-center">
            <CreditCard className="w-6 h-6 text-white" />
          </div>
          <div className="flex-1">
            <p className="font-medium text-gray-900">Visa ending in 4242</p>
            <p className="text-sm text-gray-600">Expires 12/2027</p>
          </div>
          <div className="flex items-center space-x-2">
            <Shield className="w-4 h-4 text-green-500" />
            <span className="text-sm text-green-600">Secure</span>
          </div>
        </div>
      </div>

      {/* Billing History */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Billing History</h2>
          <button className="text-blue-600 hover:text-blue-700 font-medium">
            View All
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 text-sm font-medium text-gray-700">Invoice</th>
                <th className="text-left py-3 text-sm font-medium text-gray-700">Date</th>
                <th className="text-left py-3 text-sm font-medium text-gray-700">Amount</th>
                <th className="text-left py-3 text-sm font-medium text-gray-700">Status</th>
                <th className="text-left py-3 text-sm font-medium text-gray-700">Action</th>
              </tr>
            </thead>
            <tbody>
              {invoices.map((invoice) => (
                <tr key={invoice.id} className="border-b border-gray-100">
                  <td className="py-4 text-sm text-gray-900">{invoice.id}</td>
                  <td className="py-4 text-sm text-gray-600">{invoice.date}</td>
                  <td className="py-4 text-sm text-gray-900">${invoice.amount}</td>
                  <td className="py-4">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {invoice.status}
                    </span>
                  </td>
                  <td className="py-4">
                    <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                      Download
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Confirm Plan Change
            </h3>
            <p className="text-gray-600 mb-6">
              You're about to change from {currentPlanDetails?.name} to {plans.find(p => p.id === selectedNewPlan)?.name} plan.
            </p>
            
            <div className="flex space-x-3">
              <button
                onClick={() => setShowPaymentModal(false)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handlePayment}
                disabled={loading}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Processing...' : 'Confirm Change'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default BillingPage;