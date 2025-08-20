import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Bot, ArrowLeft, Mail, CheckCircle } from 'lucide-react'
import Button from '../../components/common/Button'
import Input from '../../components/common/Input'
import { validateEmail } from '../../utils/validators'
import toast from 'react-hot-toast'

const ForgotPassword = () => {
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [emailSent, setEmailSent] = useState(false)
  const [errors, setErrors] = useState({})

  const validateForm = () => {
    const newErrors = {}
    
    const emailError = validateEmail(email)
    if (emailError) newErrors.email = emailError
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setLoading(true)
    
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      setEmailSent(true)
      toast.success('Password reset email sent!')
    } catch (error) {
      toast.error('Failed to send reset email. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  if (emailSent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto h-20 w-20 bg-green-100 rounded-full flex items-center justify-center mb-6">
              <CheckCircle className="h-10 w-10 text-green-600" />
            </div>
            
            <h2 className="text-3xl font-bold text-gray-900">
              Check your email
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              We've sent a password reset link to
            </p>
            <p className="font-semibold text-gray-900">{email}</p>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex">
              <Mail className="h-5 w-5 text-blue-600 mt-0.5" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-blue-900">
                  Didn't receive the email?
                </h3>
                <div className="mt-2 text-sm text-blue-700">
                  <ul className="list-disc list-inside space-y-1">
                    <li>Check your spam or junk folder</li>
                    <li>Make sure {email} is correct</li>
                    <li>Wait a few minutes for the email to arrive</li>
                  </ul>
                </div>
                <div className="mt-4">
                  <button
                    onClick={() => setEmailSent(false)}
                    className="text-sm bg-blue-100 text-blue-800 rounded-md px-3 py-2 hover:bg-blue-200 transition-colors"
                  >
                    Try a different email
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center">
            <Link 
              to="/login"
              className="flex items-center justify-center space-x-2 text-sm font-medium text-blue-600 hover:text-blue-500"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to login</span>
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <div className="flex items-center justify-center space-x-3 mb-8">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-r from-blue-600 to-purple-600">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-900">AI Social</h1>
            </div>
          </div>
          
          <h2 className="text-3xl font-bold text-center text-gray-900">
            Forgot your password?
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Enter your email address and we'll send you a link to reset your password.
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div>
            <Input
              label="Email address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              error={errors.email}
              placeholder="Enter your email address"
              leftIcon={<Mail className="w-5 h-5" />}
              required
            />
          </div>

          <div>
            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={loading}
              className="w-full"
            >
              Send reset link
            </Button>
          </div>

          <div className="text-center">
            <Link 
              to="/login"
              className="flex items-center justify-center space-x-2 text-sm font-medium text-blue-600 hover:text-blue-500"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to login</span>
            </Link>
          </div>
        </form>

        <div className="mt-6">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-2">
              Need help?
            </h3>
            <p className="text-sm text-gray-600">
              If you continue to have problems, please contact our support team at{' '}
              <a href="mailto:support@aisocial.com" className="text-blue-600 hover:text-blue-500">
                support@aisocial.com
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ForgotPassword