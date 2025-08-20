import { useState, useEffect } from 'react'
import { CreditCard, Plus, Trash2, Check, AlertCircle, Smartphone, Globe } from 'lucide-react'
import Button from '../common/Button'
import Modal from '../common/Modal'

const PaymentMethod = ({ currentPlan, onUpdatePlan }) => {
  const [paymentMethods, setPaymentMethods] = useState([])
  const [showAddMethod, setShowAddMethod] = useState(false)
  const [selectedMethod, setSelectedMethod] = useState(null)
  const [paymentType, setPaymentType] = useState('card') // 'card', 'upi'
  const [isLoading, setIsLoading] = useState(false)
  const [userLocation, setUserLocation] = useState('IN') // Default to India
  
  // Mock payment methods
  useEffect(() => {
    setPaymentMethods([
      {
        id: 1,
        type: 'card',
        last4: '4242',
        brand: 'visa',
        expiryMonth: 12,
        expiryYear: 2025,
        isDefault: true
      },
      {
        id: 2,
        type: 'upi',
        upiId: 'user@paytm',
        isDefault: false
      }
    ])
  }, [])
  
  const [newCard, setNewCard] = useState({
    number: '',
    expiry: '',
    cvc: '',
    name: '',
    country: 'IN'
  })
  
  const [newUPI, setNewUPI] = useState({
    upiId: '',
    name: ''
  })
  
  // Detect user location (mock)
  useEffect(() => {
    // In real app, use geolocation or IP-based detection
    const detectLocation = () => {
      const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
      const isIndian = timezone.includes('Asia/Kolkata') || timezone.includes('Asia/Calcutta')
      setUserLocation(isIndian ? 'IN' : 'US')
    }
    detectLocation()
  }, [])
  
  const formatCardNumber = (value) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '')
    const matches = v.match(/\d{4,16}/g)
    const match = matches && matches[0] || ''
    const parts = []
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4))
    }
    if (parts.length) {
      return parts.join(' ')
    } else {
      return v
    }
  }
  
  const formatExpiry = (value) => {
    const v = value.replace(/\D/g, '')
    if (v.length >= 2) {
      return v.substring(0, 2) + (v.length > 2 ? '/' + v.substring(2, 4) : '')
    }
    return v
  }
  
  const validateUPI = (upiId) => {
    const upiRegex = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+$/
    return upiRegex.test(upiId)
  }
  
  const handleAddPaymentMethod = async () => {
    setIsLoading(true)
    
    try {
      if (paymentType === 'card') {
        // Validate card details
        if (!newCard.number || !newCard.expiry || !newCard.cvc || !newCard.name) {
          throw new Error('Please fill all card details')
        }
        
        // Simulate Stripe payment method creation
        const paymentMethod = {
          id: Date.now(),
          type: 'card',
          last4: newCard.number.slice(-4),
          brand: 'visa', // In real app, detect from card number
          expiryMonth: parseInt(newCard.expiry.split('/')[0]),
          expiryYear: 2000 + parseInt(newCard.expiry.split('/')[1]),
          isDefault: paymentMethods.length === 0
        }
        
        setPaymentMethods([...paymentMethods, paymentMethod])
        setNewCard({ number: '', expiry: '', cvc: '', name: '', country: 'IN' })
        
      } else if (paymentType === 'upi') {
        // Validate UPI ID
        if (!validateUPI(newUPI.upiId)) {
          throw new Error('Please enter a valid UPI ID')
        }
        
        // Simulate UPI verification
        const paymentMethod = {
          id: Date.now(),
          type: 'upi',
          upiId: newUPI.upiId,
          name: newUPI.name,
          isDefault: paymentMethods.length === 0
        }
        
        setPaymentMethods([...paymentMethods, paymentMethod])
        setNewUPI({ upiId: '', name: '' })
      }
      
      setShowAddMethod(false)
    } catch (error) {
      alert(error.message)
    }
    
    setIsLoading(false)
  }
  
  const handleDeleteMethod = (id) => {
    setPaymentMethods(paymentMethods.filter(method => method.id !== id))
  }
  
  const handleSetDefault = (id) => {
    setPaymentMethods(paymentMethods.map(method => ({
      ...method,
      isDefault: method.id === id
    })))
  }
  
  const getCardIcon = (brand) => {
    const icons = {
      visa: '💳',
      mastercard: '💳',
      amex: '💳',
      discover: '💳'
    }
    return icons[brand] || '💳'
  }
  
  const renderPaymentMethod = (method) => {
    if (method.type === 'card') {
      return (
        <div key={method.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-6 bg-gray-100 rounded flex items-center justify-center text-sm">
              {getCardIcon(method.brand)}
            </div>
            <div>
              <div className="font-medium text-gray-900">
                •••• •••• •••• {method.last4}
              </div>
              <div className="text-sm text-gray-500">
                Expires {method.expiryMonth}/{method.expiryYear}
                {method.isDefault && (
                  <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                    Default
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {!method.isDefault && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSetDefault(method.id)}
              >
                Set Default
              </Button>
            )}
            <button
              onClick={() => handleDeleteMethod(method.id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      )
    }
    
    if (method.type === 'upi') {
      return (
        <div key={method.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-6 bg-orange-100 rounded flex items-center justify-center">
              <Smartphone className="w-4 h-4 text-orange-600" />
            </div>
            <div>
              <div className="font-medium text-gray-900">{method.upiId}</div>
              <div className="text-sm text-gray-500">
                UPI Payment
                {method.isDefault && (
                  <span className="ml-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                    Default
                  </span>
                )}
              </div>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {!method.isDefault && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleSetDefault(method.id)}
              >
                Set Default
              </Button>
            )}
            <button
              onClick={() => handleDeleteMethod(method.id)}
              className="p-2 text-red-600 hover:bg-red-50 rounded"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      )
    }
  }
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Payment Methods</h3>
          <p className="text-sm text-gray-600">
            Manage your payment methods for subscription billing
          </p>
        </div>
        <Button onClick={() => setShowAddMethod(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Add Payment Method
        </Button>
      </div>
      
      {/* Current Plan Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center space-x-2 mb-2">
          <Check className="w-5 h-5 text-blue-600" />
          <span className="font-medium text-blue-900">
            Current Plan: {currentPlan?.name || 'Starter'}
          </span>
        </div>
        <p className="text-sm text-blue-800">
          Next billing: {currentPlan?.nextBilling || 'N/A'} • 
          Amount: {currentPlan?.amount || '$0'}/month
        </p>
      </div>
      
      {/* Payment Methods List */}
      <div className="space-y-3">
        <h4 className="font-medium text-gray-900">Saved Payment Methods</h4>
        
        {paymentMethods.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <CreditCard className="w-12 h-12 mx-auto mb-3 text-gray-300" />
            <p className="text-sm">No payment methods added</p>
            <Button 
              onClick={() => setShowAddMethod(true)} 
              className="mt-3" 
              size="sm"
            >
              Add Your First Payment Method
            </Button>
          </div>
        ) : (
          paymentMethods.map(renderPaymentMethod)
        )}
      </div>
      
      {/* Add Payment Method Modal */}
      <Modal
        isOpen={showAddMethod}
        onClose={() => setShowAddMethod(false)}
        title="Add Payment Method"
      >
        <div className="space-y-6">
          {/* Payment Type Selector */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Choose Payment Method
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => setPaymentType('card')}
                className={`p-4 border-2 rounded-lg flex items-center justify-center space-x-2 transition-colors ${
                  paymentType === 'card'
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <Globe className="w-5 h-5" />
                <span className="font-medium">Card (Global)</span>
              </button>
              
              {userLocation === 'IN' && (
                <button
                  onClick={() => setPaymentType('upi')}
                  className={`p-4 border-2 rounded-lg flex items-center justify-center space-x-2 transition-colors ${
                    paymentType === 'upi'
                      ? 'border-blue-500 bg-blue-50 text-blue-700'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Smartphone className="w-5 h-5" />
                  <span className="font-medium">UPI (India)</span>
                </button>
              )}
            </div>
          </div>
          
          {/* Card Form */}
          {paymentType === 'card' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Card Number
                </label>
                <input
                  type="text"
                  placeholder="1234 5678 9012 3456"
                  value={newCard.number}
                  onChange={(e) => setNewCard(prev => ({
                    ...prev,
                    number: formatCardNumber(e.target.value)
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  maxLength="19"
                />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expiry Date
                  </label>
                  <input
                    type="text"
                    placeholder="MM/YY"
                    value={newCard.expiry}
                    onChange={(e) => setNewCard(prev => ({
                      ...prev,
                      expiry: formatExpiry(e.target.value)
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    maxLength="5"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    CVC
                  </label>
                  <input
                    type="text"
                    placeholder="123"
                    value={newCard.cvc}
                    onChange={(e) => setNewCard(prev => ({
                      ...prev,
                      cvc: e.target.value.replace(/\D/g, '')
                    }))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    maxLength="4"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Cardholder Name
                </label>
                <input
                  type="text"
                  placeholder="John Doe"
                  value={newCard.name}
                  onChange={(e) => setNewCard(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          )}
          
          {/* UPI Form */}
          {paymentType === 'upi' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  UPI ID
                </label>
                <input
                  type="text"
                  placeholder="yourname@paytm"
                  value={newUPI.upiId}
                  onChange={(e) => setNewUPI(prev => ({
                    ...prev,
                    upiId: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter your UPI ID (e.g., yourname@paytm, yourname@gpay)
                </p>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Name (Optional)
                </label>
                <input
                  type="text"
                  placeholder="Account holder name"
                  value={newUPI.name}
                  onChange={(e) => setNewUPI(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          )}
          
          {/* Action Buttons */}
          <div className="flex space-x-3 pt-4 border-t">
            <Button
              variant="outline"
              onClick={() => setShowAddMethod(false)}
              className="flex-1"
            >
              Cancel
            </Button>
            <Button
              onClick={handleAddPaymentMethod}
              disabled={isLoading}
              className="flex-1"
            >
              {isLoading ? 'Adding...' : 'Add Payment Method'}
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

export default PaymentMethod