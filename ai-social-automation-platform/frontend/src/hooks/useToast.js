// frontend/src/hooks/useToast.js
import { useState, useCallback } from 'react'

const useToast = () => {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback((type, message, title = '', duration = 4000) => {
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
    return addToast('success', message, title)
  }, [addToast])

  const error = useCallback((message, title = 'Error') => {
    return addToast('error', message, title, 5000)
  }, [addToast])

  const warning = useCallback((message, title = 'Warning') => {
    return addToast('warning', message, title)
  }, [addToast])

  const info = useCallback((message, title = 'Info') => {
    return addToast('info', message, title)
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

// Export both default and named export
export default useToast
export { useToast }