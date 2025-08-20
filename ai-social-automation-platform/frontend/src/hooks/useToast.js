// frontend/src/hooks/useToast.js
import { useState, useCallback } from 'react'

const useToast = () => {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((type, title, message, duration = 4000) => {
    const id = Date.now() + Math.random()
    const newToast = { id, type, title, message, duration }
    
    setToasts(prev => [...prev, newToast])
    
    if (duration > 0) {
      setTimeout(() => {
        removeToast(id)
      }, duration)
    }
    
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(toast => toast.id !== id))
  }, [])

  const success = useCallback((message, title = 'Success') => {
    return addToast('success', title, message)
  }, [addToast])

  const error = useCallback((message, title = 'Error') => {
    return addToast('error', title, message)
  }, [addToast])

  const warning = useCallback((message, title = 'Warning') => {
    return addToast('warning', title, message)
  }, [addToast])

  const info = useCallback((message, title = 'Info') => {
    return addToast('info', title, message)
  }, [addToast])

  const clearAll = useCallback(() => {
    setToasts([])
  }, [])

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

export default useToast