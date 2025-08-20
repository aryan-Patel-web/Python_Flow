// frontend/src/context/AuthContext.jsx (FIXED - NO ROUTER)
import React, { createContext, useContext } from 'react'
import useAuth from '../hooks/useAuth'

const AuthContext = createContext()

// AuthProvider should NOT have Router - Router is in App.jsx
export const AuthProvider = ({ children }) => {
  const auth = useAuth()

  return (
    <AuthContext.Provider value={auth}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuthContext = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthContext must be used within an AuthProvider')
  }
  return context
}

export default AuthContext