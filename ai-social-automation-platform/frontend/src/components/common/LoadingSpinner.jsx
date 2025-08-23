import React from 'react';
import { Loader } from 'lucide-react';

const LoadingSpinner = ({ 
  size = 'medium', 
  text = '', 
  className = '', 
  color = 'blue',
  showIcon = true 
}) => {
  const sizeClasses = {
    small: 'w-4 h-4',
    medium: 'w-8 h-8',
    large: 'w-12 h-12',
    xlarge: 'w-16 h-16'
  };

  const colorClasses = {
    blue: 'text-blue-600',
    green: 'text-green-600',
    red: 'text-red-600',
    gray: 'text-gray-600',
    purple: 'text-purple-600',
    orange: 'text-orange-600'
  };

  const textSizeClasses = {
    small: 'text-xs',
    medium: 'text-sm',
    large: 'text-base',
    xlarge: 'text-lg'
  };

  return (
    <div className={`flex flex-col items-center justify-center ${className}`}>
      {showIcon && (
        <div className="relative">
          {/* Outer spinning ring */}
          <div className={`
            ${sizeClasses[size]} 
            animate-spin rounded-full border-2 border-gray-200 
            border-t-current ${colorClasses[color]}
          `} />
          
          {/* Inner icon (optional) */}
          <div className="absolute inset-0 flex items-center justify-center">
            <Loader className={`${
              size === 'small' ? 'w-2 h-2' :
              size === 'medium' ? 'w-4 h-4' :
              size === 'large' ? 'w-6 h-6' : 'w-8 h-8'
            } ${colorClasses[color]} opacity-20`} />
          </div>
        </div>
      )}
      
      {text && (
        <p className={`
          mt-3 font-medium ${colorClasses[color]} ${textSizeClasses[size]}
          animate-pulse
        `}>
          {text}
        </p>
      )}
    </div>
  );
};

// Preset spinner variants
export const SpinnerVariants = {
  // Small inline spinner
  Inline: ({ text = 'Loading...' }) => (
    <LoadingSpinner 
      size="small" 
      text={text} 
      className="inline-flex items-center space-x-2" 
    />
  ),

  // Page loading spinner
  Page: ({ text = 'Loading page...' }) => (
    <div className="min-h-screen flex items-center justify-center">
      <LoadingSpinner size="large" text={text} color="blue" />
    </div>
  ),

  // Modal/overlay spinner
  Overlay: ({ text = 'Processing...' }) => (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6">
        <LoadingSpinner size="large" text={text} color="blue" />
      </div>
    </div>
  ),

  // Button loading state
  Button: ({ text = 'Loading...' }) => (
    <LoadingSpinner 
      size="small" 
      text={text} 
      className="flex items-center space-x-2" 
      showIcon={true}
    />
  ),

  // Card loading state
  Card: ({ text = 'Loading...' }) => (
    <div className="p-8 text-center">
      <LoadingSpinner size="medium" text={text} color="gray" />
    </div>
  )
};

export default LoadingSpinner;