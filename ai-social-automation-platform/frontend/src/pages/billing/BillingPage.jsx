import React, { useState, useEffect } from 'react';
import { 
  CreditCard, 
  Download, 
  Calendar, 
  Check, 
  X, 
  AlertCircle,
  Crown,
  Zap,
  Users,
  BarChart3,
  Clock,
  RefreshCw
} from 'lucide-react';
import { useToast } from '../../components/common/Toast';

const BillingPage = () => {
  const [currentPlan, setCurrentPlan] = useState(null);
  const [billingHistory, setBillingHistory] = useState([]);
  const [usage, setUsage] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchBillingData();
  }, []);

  const fetchBillingData = async () => {
    try {
      setLoading(true);
      
      // Fetch current subscription
      const subResponse = await fetch('/api/billing/subscription', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (subResponse.ok) {
        const subData = await subResponse.json();
        setCurrentPlan(subData.subscription);
      }

      // Fetch billing history
      const historyResponse = await fetch('/api/billing/history', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (historyResponse.ok) {
        const historyData = await historyResponse.json();
        setBillingHistory(historyData.invoices || []);
      }

      // Fetch usage data
      const usageResponse = await fetch('/api/billing/usage', {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (usageResponse.ok) {
        const usageData = await usageResponse.json();
        setUsage(usageData.usage);
      }

    } catch (error) {
      console.error('Error fetching billing data:', error);
      // Set demo data
      setCurrentPlan({
        plan_name: 'Pro',
        status: 'active',
        current_period_start: '2024-01-01',
        current_period_end: '2024-02-01',
        price: 29.99,
        currency: 'USD'
      });
      
      setBillingHistory([
        {
          id: 'inv_001',
          date: '2024-01-01',
          amount: 29.99,
          status: 'paid',
          description: 'Pro Plan - Monthly'
        },
        {
          id: 'inv_002',
          date: '2023-12-01',
          amount: 29.99,
          status: 'paid',
          description: 'Pro Plan - Monthly'
        }
      ]);
      
      setUsage({
        posts_generated: 156,
        posts_limit: 500,
        accounts_connected: 3,
        accounts_limit: 10,
        api_calls: 2340,
        api_limit: 10000
      });
    } finally {
      setLoading(false);
    }
  };

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      currency: 'USD',
      interval: 'month',
      features: [
        '3 connected accounts',
        '50 posts per month',
        'Basic analytics',
        'Email support'
      ],
      limits: {
        accounts: 3,
        posts: 50,
        ai_generations: 100
      },
      icon: Users,
      color: 'gray'
    },
    {
      id: 'pro',
      name: 'Pro',
      price: 29.99,
      currency: 'USD',
      interval: 'month',
      features: [
        '10 connected accounts',
        '500 posts per month',
        'Advanced analytics',
        'Priority support',
        'Custom scheduling',
        'AI content optimization'
      ],
      limits: {
        accounts: 10,
        posts: 500,
        ai_generations: 1000
      },
      icon: Zap,
      color: 'blue',
      popular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 99.99,
      currency: 'USD',
      interval: 'month',
      features: [
        'Unlimited accounts',
        'Unlimited posts',
        'Advanced analytics & reporting',
        'Dedicated support',
        'Custom integrations',
        'White-label options',
        'Team collaboration',
        'Advanced AI features'
      ],
      limits: {
        accounts: 'unlimited',
        posts: 'unlimited',
        ai_generations: 'unlimited'
      },
      icon: Crown,
      color: 'purple'
    }
  ];

  const handlePlanChange = async (planId) => {
    try {
      setSelectedPlan(planId);
      
      if (planId === 'free') {
        // Handle downgrade
        const confirmDowngrade = window.confirm(
          'Are you sure you want to downgrade to the free plan? You will lose access to premium features.'
        );
        
        if (!confirmDowngrade) return;
      }

      const response = await fetch('/api/billing/change-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ plan_id: planId })
      });

      if (response.ok) {
        toast.success('Plan updated successfully!');
        fetchBillingData();
        setShowUpgradeModal(false);
      } else {
        throw new Error('Failed to update plan');
      }
    } catch (error) {
      toast.error('Failed to update plan. Please try again.');
      console.error('Error changing plan:', error);
    } finally {
      setSelectedPlan(null);
    }
  };

  const downloadInvoice = async (invoiceId) => {
    try {
      const response = await fetch(`/api/billing/invoice/${invoiceId}/download`, {
        headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
      });
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `invoice-${invoiceId}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      }
    } catch (error) {
      toast.error('Failed to download invoice');
    }
  };

  const getUsagePercentage = (used, limit) => {
    if (limit === 'unlimited') return 0;
    return Math.min((used / limit) * 100, 100);
  };

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'bg-red-500';
    if (percentage >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  const formatCurrency = (amount, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency
    }).format(amount);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/4"></div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-64 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Billing & Subscription</h1>
            <p className="text-gray-600 mt-1">Manage your subscription and billing preferences</p>
          </div>
          <button
            onClick={fetchBillingData}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </button>
        </div>

        {/* Current Plan Status */}
        {currentPlan && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Current Plan</h2>
              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                currentPlan.status === 'active' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {currentPlan.status}
              </span>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div>
                <p className="text-sm text-gray-600">Plan</p>
                <p className="text-xl font-bold text-gray-900">{currentPlan.plan_name}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Price</p>
                <p className="text-xl font-bold text-gray-900">
                  {formatCurrency(currentPlan.price, currentPlan.currency)}/month
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Billing Period</p>
                <p className="text-sm text-gray-900">
                  {new Date(currentPlan.current_period_start).toLocaleDateString()} - {' '}
                  {new Date(currentPlan.current_period_end).toLocaleDateString()}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Next Billing</p>
                <p className="text-sm text-gray-900">
                  {new Date(currentPlan.current_period_end).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Usage Overview */}
        {usage && (
          <div className="bg-white rounded-lg shadow-sm border p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Current Usage</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-600">Posts Generated</p>
                  <p className="text-sm font-medium">
                    {usage.posts_generated} / {usage.posts_limit === 'unlimited' ? '∞' : usage.posts_limit}
                  </p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getUsageColor(getUsagePercentage(usage.posts_generated, usage.posts_limit))}`}
                    style={{ width: `${getUsagePercentage(usage.posts_generated, usage.posts_limit)}%` }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-600">Connected Accounts</p>
                  <p className="text-sm font-medium">
                    {usage.accounts_connected} / {usage.accounts_limit === 'unlimited' ? '∞' : usage.accounts_limit}
                  </p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getUsageColor(getUsagePercentage(usage.accounts_connected, usage.accounts_limit))}`}
                    style={{ width: `${getUsagePercentage(usage.accounts_connected, usage.accounts_limit)}%` }}
                  ></div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm text-gray-600">API Calls</p>
                  <p className="text-sm font-medium">
                    {usage.api_calls} / {usage.api_limit === 'unlimited' ? '∞' : usage.api_limit}
                  </p>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full transition-all ${getUsageColor(getUsagePercentage(usage.api_calls, usage.api_limit))}`}
                    style={{ width: `${getUsagePercentage(usage.api_calls, usage.api_limit)}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Available Plans */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-900">Available Plans</h2>
            <p className="text-sm text-gray-600">Choose the plan that fits your needs</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {plans.map((plan) => {
              const Icon = plan.icon;
              const isCurrentPlan = currentPlan?.plan_name?.toLowerCase() === plan.name.toLowerCase();
              
              return (
                <div
                  key={plan.id}
                  className={`relative border rounded-lg p-6 transition-all hover:shadow-md ${
                    plan.popular ? 'border-blue-500 ring-2 ring-blue-200' : 'border-gray-200'
                  } ${isCurrentPlan ? 'bg-gray-50' : 'bg-white'}`}
                >
                  {plan.popular && (
                    <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                      <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-xs font-medium">
                        Most Popular
                      </span>
                    </div>
                  )}
                  
                  <div className="text-center mb-6">
                    <Icon className={`w-8 h-8 mx-auto mb-3 text-${plan.color}-600`} />
                    <h3 className="text-xl font-bold text-gray-900">{plan.name}</h3>
                    <div className="mt-2">
                      <span className="text-3xl font-bold text-gray-900">
                        {formatCurrency(plan.price, plan.currency)}
                      </span>
                      <span className="text-gray-600">/{plan.interval}</span>
                    </div>
                  </div>
                  
                  <ul className="space-y-3 mb-6">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-center text-sm">
                        <Check className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <button
                    onClick={() => handlePlanChange(plan.id)}
                    disabled={isCurrentPlan || selectedPlan === plan.id}
                    className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
                      isCurrentPlan
                        ? 'bg-gray-100 text-gray-500 cursor-not-allowed'
                        : selectedPlan === plan.id
                          ? 'bg-gray-400 text-white cursor-not-allowed'
                          : plan.popular
                            ? 'bg-blue-600 text-white hover:bg-blue-700'
                            : 'bg-gray-900 text-white hover:bg-gray-800'
                    }`}
                  >
                    {isCurrentPlan ? 'Current Plan' : selectedPlan === plan.id ? 'Processing...' : 'Select Plan'}
                  </button>
                </div>
              );
            })}
          </div>
        </div>

        {/* Billing History */}
        <div className="bg-white rounded-lg shadow-sm border">
          <div className="p-6 border-b">
            <h2 className="text-lg font-semibold text-gray-900">Billing History</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Description
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Amount
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {billingHistory.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                      No billing history available
                    </td>
                  </tr>
                ) : (
                  billingHistory.map((invoice) => (
                    <tr key={invoice.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(invoice.date).toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {invoice.description}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatCurrency(invoice.amount)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                          invoice.status === 'paid'
                            ? 'bg-green-100 text-green-800'
                            : invoice.status === 'pending'
                              ? 'bg-yellow-100 text-yellow-800'
                              : 'bg-red-100 text-red-800'
                        }`}>
                          {invoice.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {invoice.status === 'paid' && (
                          <button
                            onClick={() => downloadInvoice(invoice.id)}
                            className="text-blue-600 hover:text-blue-900 flex items-center"
                          >
                            <Download className="w-4 h-4 mr-1" />
                            Download
                          </button>
                        )}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Payment Method */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Payment Method</h2>
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              Update Payment Method
            </button>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="w-12 h-8 bg-gray-100 rounded flex items-center justify-center">
              <CreditCard className="w-5 h-5 text-gray-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">•••• •••• •••• 4242</p>
              <p className="text-xs text-gray-500">Expires 12/25</p>
            </div>
          </div>
        </div>

        {/* Usage Alerts */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Usage Alerts</h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-gray-900">Approaching Limit</p>
                <p className="text-sm text-gray-600">
                  You've used 78% of your monthly post quota. Consider upgrading to avoid interruption.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* FAQ Section */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Frequently Asked Questions</h2>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-1">Can I change my plan at any time?</h4>
              <p className="text-sm text-gray-600">
                Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-1">What happens if I exceed my usage limits?</h4>
              <p className="text-sm text-gray-600">
                If you exceed your plan limits, you'll be notified and given the option to upgrade or wait until the next billing cycle.
              </p>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-1">Is there a free trial?</h4>
              <p className="text-sm text-gray-600">
                Yes, all new users get access to our free plan with no time limit. You can upgrade at any time.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BillingPage;