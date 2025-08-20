import { createContext, useContext, useReducer, useEffect } from 'react'

// Initial state
const initialState = {
  // User data
  user: null,
  subscription: null,
  
  // Platform connections
  platforms: [],
  connectedPlatforms: [],
  
  // Content domains
  availableDomains: [],
  selectedDomains: [],
  
  // Content & Analytics
  recentPosts: [],
  analytics: {
    totalPosts: 0,
    totalEngagement: 0,
    totalReach: 0,
    growthRate: 0
  },
  
  // App settings
  settings: {
    timezone: 'Asia/Kolkata',
    notifications: {
      email: true,
      push: true,
      weekly: true
    },
    posting: {
      autoPost: true,
      optimalTiming: true,
      retryFailed: true
    }
  },
  
  // UI state
  ui: {
    sidebarCollapsed: false,
    currentPage: 'dashboard',
    loading: false,
    notifications: []
  }
}

// Action types
const ActionTypes = {
  // User actions
  SET_USER: 'SET_USER',
  SET_SUBSCRIPTION: 'SET_SUBSCRIPTION',
  LOGOUT: 'LOGOUT',
  
  // Platform actions
  SET_PLATFORMS: 'SET_PLATFORMS',
  ADD_PLATFORM: 'ADD_PLATFORM',
  UPDATE_PLATFORM: 'UPDATE_PLATFORM',
  REMOVE_PLATFORM: 'REMOVE_PLATFORM',
  
  // Domain actions
  SET_AVAILABLE_DOMAINS: 'SET_AVAILABLE_DOMAINS',
  SET_SELECTED_DOMAINS: 'SET_SELECTED_DOMAINS',
  ADD_DOMAIN: 'ADD_DOMAIN',
  REMOVE_DOMAIN: 'REMOVE_DOMAIN',
  
  // Content actions
  SET_RECENT_POSTS: 'SET_RECENT_POSTS',
  ADD_POST: 'ADD_POST',
  UPDATE_POST: 'UPDATE_POST',
  
  // Analytics actions
  SET_ANALYTICS: 'SET_ANALYTICS',
  UPDATE_ANALYTICS: 'UPDATE_ANALYTICS',
  
  // Settings actions
  UPDATE_SETTINGS: 'UPDATE_SETTINGS',
  
  // UI actions
  SET_LOADING: 'SET_LOADING',
  TOGGLE_SIDEBAR: 'TOGGLE_SIDEBAR',
  SET_CURRENT_PAGE: 'SET_CURRENT_PAGE',
  ADD_NOTIFICATION: 'ADD_NOTIFICATION',
  REMOVE_NOTIFICATION: 'REMOVE_NOTIFICATION'
}

// Reducer function
const appReducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.SET_USER:
      return {
        ...state,
        user: action.payload
      }
      
    case ActionTypes.SET_SUBSCRIPTION:
      return {
        ...state,
        subscription: action.payload
      }
      
    case ActionTypes.LOGOUT:
      return {
        ...initialState,
        ui: {
          ...initialState.ui,
          sidebarCollapsed: state.ui.sidebarCollapsed
        }
      }
      
    case ActionTypes.SET_PLATFORMS:
      return {
        ...state,
        platforms: action.payload,
        connectedPlatforms: action.payload.filter(p => p.isConnected)
      }
      
    case ActionTypes.ADD_PLATFORM:
      const newPlatforms = [...state.platforms, action.payload]
      return {
        ...state,
        platforms: newPlatforms,
        connectedPlatforms: newPlatforms.filter(p => p.isConnected)
      }
      
    case ActionTypes.UPDATE_PLATFORM:
      const updatedPlatforms = state.platforms.map(platform =>
        platform.id === action.payload.id ? action.payload : platform
      )
      return {
        ...state,
        platforms: updatedPlatforms,
        connectedPlatforms: updatedPlatforms.filter(p => p.isConnected)
      }
      
    case ActionTypes.REMOVE_PLATFORM:
      const filteredPlatforms = state.platforms.filter(p => p.id !== action.payload)
      return {
        ...state,
        platforms: filteredPlatforms,
        connectedPlatforms: filteredPlatforms.filter(p => p.isConnected)
      }
      
    case ActionTypes.SET_AVAILABLE_DOMAINS:
      return {
        ...state,
        availableDomains: action.payload
      }
      
    case ActionTypes.SET_SELECTED_DOMAINS:
      return {
        ...state,
        selectedDomains: action.payload
      }
      
    case ActionTypes.ADD_DOMAIN:
      return {
        ...state,
        selectedDomains: [...state.selectedDomains, action.payload]
      }
      
    case ActionTypes.REMOVE_DOMAIN:
      return {
        ...state,
        selectedDomains: state.selectedDomains.filter(d => d.id !== action.payload)
      }
      
    case ActionTypes.SET_RECENT_POSTS:
      return {
        ...state,
        recentPosts: action.payload
      }
      
    case ActionTypes.ADD_POST:
      return {
        ...state,
        recentPosts: [action.payload, ...state.recentPosts].slice(0, 50)
      }
      
    case ActionTypes.UPDATE_POST:
      return {
        ...state,
        recentPosts: state.recentPosts.map(post =>
          post.id === action.payload.id ? action.payload : post
        )
      }
      
    case ActionTypes.SET_ANALYTICS:
      return {
        ...state,
        analytics: action.payload
      }
      
    case ActionTypes.UPDATE_ANALYTICS:
      return {
        ...state,
        analytics: { ...state.analytics, ...action.payload }
      }
      
    case ActionTypes.UPDATE_SETTINGS:
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
      }
      
    case ActionTypes.SET_LOADING:
      return {
        ...state,
        ui: { ...state.ui, loading: action.payload }
      }
      
    case ActionTypes.TOGGLE_SIDEBAR:
      return {
        ...state,
        ui: { ...state.ui, sidebarCollapsed: !state.ui.sidebarCollapsed }
      }
      
    case ActionTypes.SET_CURRENT_PAGE:
      return {
        ...state,
        ui: { ...state.ui, currentPage: action.payload }
      }
      
    case ActionTypes.ADD_NOTIFICATION:
      return {
        ...state,
        ui: {
          ...state.ui,
          notifications: [...state.ui.notifications, action.payload]
        }
      }
      
    case ActionTypes.REMOVE_NOTIFICATION:
      return {
        ...state,
        ui: {
          ...state.ui,
          notifications: state.ui.notifications.filter(n => n.id !== action.payload)
        }
      }
      
    default:
      return state
  }
}

// Context creation
const AppContext = createContext()

// Custom hook to use context
export const useApp = () => {
  const context = useContext(AppContext)
  if (!context) {
    throw new Error('useApp must be used within AppProvider')
  }
  return context
}

// Context Provider component
export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState)
  
  // Load data from localStorage on mount
  useEffect(() => {
    const savedData = localStorage.getItem('aiSocialApp')
    if (savedData) {
      try {
        const parsed = JSON.parse(savedData)
        if (parsed.user) dispatch({ type: ActionTypes.SET_USER, payload: parsed.user })
        if (parsed.platforms) dispatch({ type: ActionTypes.SET_PLATFORMS, payload: parsed.platforms })
        if (parsed.selectedDomains) dispatch({ type: ActionTypes.SET_SELECTED_DOMAINS, payload: parsed.selectedDomains })
        if (parsed.settings) dispatch({ type: ActionTypes.UPDATE_SETTINGS, payload: parsed.settings })
      } catch (error) {
        console.error('Error loading saved data:', error)
      }
    }
  }, [])
  
  // Save important data to localStorage
  useEffect(() => {
    const dataToSave = {
      user: state.user,
      platforms: state.platforms,
      selectedDomains: state.selectedDomains,
      settings: state.settings
    }
    localStorage.setItem('aiSocialApp', JSON.stringify(dataToSave))
  }, [state.user, state.platforms, state.selectedDomains, state.settings])
  
  // Action creators
  const actions = {
    // User actions
    setUser: (user) => dispatch({ type: ActionTypes.SET_USER, payload: user }),
    setSubscription: (subscription) => dispatch({ type: ActionTypes.SET_SUBSCRIPTION, payload: subscription }),
    logout: () => dispatch({ type: ActionTypes.LOGOUT }),
    
    // Platform actions
    setPlatforms: (platforms) => dispatch({ type: ActionTypes.SET_PLATFORMS, payload: platforms }),
    addPlatform: (platform) => dispatch({ type: ActionTypes.ADD_PLATFORM, payload: platform }),
    updatePlatform: (platform) => dispatch({ type: ActionTypes.UPDATE_PLATFORM, payload: platform }),
    removePlatform: (platformId) => dispatch({ type: ActionTypes.REMOVE_PLATFORM, payload: platformId }),
    
    // Domain actions
    setAvailableDomains: (domains) => dispatch({ type: ActionTypes.SET_AVAILABLE_DOMAINS, payload: domains }),
    setSelectedDomains: (domains) => dispatch({ type: ActionTypes.SET_SELECTED_DOMAINS, payload: domains }),
    addDomain: (domain) => dispatch({ type: ActionTypes.ADD_DOMAIN, payload: domain }),
    removeDomain: (domainId) => dispatch({ type: ActionTypes.REMOVE_DOMAIN, payload: domainId }),
    
    // Content actions
    setRecentPosts: (posts) => dispatch({ type: ActionTypes.SET_RECENT_POSTS, payload: posts }),
    addPost: (post) => dispatch({ type: ActionTypes.ADD_POST, payload: post }),
    updatePost: (post) => dispatch({ type: ActionTypes.UPDATE_POST, payload: post }),
    
    // Analytics actions
    setAnalytics: (analytics) => dispatch({ type: ActionTypes.SET_ANALYTICS, payload: analytics }),
    updateAnalytics: (updates) => dispatch({ type: ActionTypes.UPDATE_ANALYTICS, payload: updates }),
    
    // Settings actions
    updateSettings: (updates) => dispatch({ type: ActionTypes.UPDATE_SETTINGS, payload: updates }),
    
    // UI actions
    setLoading: (loading) => dispatch({ type: ActionTypes.SET_LOADING, payload: loading }),
    toggleSidebar: () => dispatch({ type: ActionTypes.TOGGLE_SIDEBAR }),
    setCurrentPage: (page) => dispatch({ type: ActionTypes.SET_CURRENT_PAGE, payload: page }),
    addNotification: (notification) => dispatch({ 
      type: ActionTypes.ADD_NOTIFICATION, 
      payload: { ...notification, id: Date.now() }
    }),
    removeNotification: (id) => dispatch({ type: ActionTypes.REMOVE_NOTIFICATION, payload: id })
  }
  
  return (
    <AppContext.Provider value={{ state, actions }}>
      {children}
    </AppContext.Provider>
  )
}

export { ActionTypes }
export default AppContext