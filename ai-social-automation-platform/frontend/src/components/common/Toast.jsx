// frontend/src/components/common/Toast.jsx (FIXED - EXPORT useToast)
import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, AlertCircle, Info, X } from 'lucide-react'

const Toast = ({
  type = 'info',
  title,
  message,
  duration = 4000,
  onClose,
  position = 'top-right'
}) => {
  const [visible, setVisible] = useState(true)

  const typeConfig = {
    success: {
      icon: CheckCircle,
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      iconColor: 'text-green-600',
      titleColor: 'text-green-800',
      textColor: 'text-green-700'
    },
    error: {
      icon: XCircle,
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      iconColor: 'text-red-600',
      titleColor: 'text-red-800',
      textColor: 'text-red-700'
    },
    warning: {
      icon: AlertCircle,
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      iconColor: 'text-yellow-600',
      titleColor: 'text-yellow-800',
      textColor: 'text-yellow-700'
    },
    info: {
      icon: Info,
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      iconColor: 'text-blue-600',
      titleColor: 'text-blue-800',
      textColor: 'text-blue-700'
    }
  }

  const config = typeConfig[type]
  const Icon = config.icon

  const positionClasses = {
    'top-right': 'top-4 right-4',
    'top-left': 'top-4 left-4',
    'bottom-right': 'bottom-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
    'bottom-center': 'bottom-4 left-1/2 transform -translate-x-1/2'
  }

  useEffect(() => {
    if (duration > 0) {
      const timer = setTimeout(() => {
        setVisible(false)
        setTimeout(onClose, 300) // Wait for fade out animation
      }, duration)

      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  const handleClose = () => {
    setVisible(false)
    setTimeout(onClose, 300)
  }

  return (
    <div
      className={`fixed z-50 ${positionClasses[position]} transition-all duration-300 ${
        visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-2'
      }`}
    >
      <div className={`max-w-sm w-full ${config.bgColor} ${config.borderColor} border rounded-lg shadow-lg p-4`}>
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <Icon className={`w-5 h-5 ${config.iconColor}`} />
          </div>
          <div className="ml-3 w-0 flex-1">
            {title && (
              <p className={`text-sm font-medium ${config.titleColor}`}>
                {title}
              </p>
            )}
            {message && (
              <p className={`text-sm ${config.textColor} ${title ? 'mt-1' : ''}`}>
                {message}
              </p>
            )}
          </div>
          <div className="ml-4 flex-shrink-0 flex">
            <button
              onClick={handleClose}
              className={`inline-flex ${config.textColor} hover:opacity-75 transition-opacity`}
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

// Toast Container Component
export const ToastContainer = ({ toasts = [], removeToast = () => {} }) => {
  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          {...toast}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </div>
  )
}

// useToast Hook - THIS WAS MISSING!
export const useToast = () => {
  const [toasts, setToasts] = useState([])

  const addToast = (type, message, title = '', duration = 4000) => {
    const id = Date.now() + Math.random()
    const newToast = { id, type, title, message, duration }
    
    setToasts(prev => [...prev, newToast])
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    return id
  }

  const removeToast = (id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }

  const success = (message, title = 'Success') => {
    return addToast('success', message, title)
  }

  const error = (message, title = 'Error') => {
    return addToast('error', message, title, 5000)
  }

  const warning = (message, title = 'Warning') => {
    return addToast('warning', message, title)
  }

  const info = (message, title = 'Info') => {
    return addToast('info', message, title)
  }

  const clearAll = () => {
    setToasts([])
  }

  return {
    toasts,
    success,
    error,
    warning,
    info,
    addToast,
    removeToast,
    clearAll
  }
}

export default Toast