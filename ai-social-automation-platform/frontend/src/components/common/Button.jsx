import React, { forwardRef } from 'react';
import { Loader2 } from 'lucide-react';

const Button = forwardRef(({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  fullWidth = false,
  leftIcon,
  rightIcon,
  className = '',
  ...props
}, ref) => {
  
  const baseClasses = 'inline-flex items-center justify-center font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 shadow-sm hover:shadow-md',
    secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus:ring-gray-500 border border-gray-300',
    outline: 'bg-transparent text-blue-600 border border-blue-600 hover:bg-blue-50 focus:ring-blue-500',
    ghost: 'bg-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-900 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 shadow-sm hover:shadow-md',
    success: 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500 shadow-sm hover:shadow-md',
    warning: 'bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-yellow-500 shadow-sm hover:shadow-md',
    link: 'bg-transparent text-blue-600 hover:text-blue-700 underline-offset-4 hover:underline p-0'
  };
  
  const sizes = {
    xs: 'px-2.5 py-1.5 text-xs',
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-4 py-2 text-base',
    xl: 'px-6 py-3 text-base'
  };
  
  const iconSizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4',
    md: 'w-4 h-4',
    lg: 'w-5 h-5',
    xl: 'w-5 h-5'
  };
  
  const classes = [
    baseClasses,
    variants[variant],
    sizes[size],
    fullWidth ? 'w-full' : '',
    className
  ].filter(Boolean).join(' ');
  
  const iconClass = iconSizes[size];
  
  return (
    <button
      ref={ref}
      className={classes}
      disabled={disabled || loading}
      {...props}
    >
      {loading && (
        <Loader2 className={`${iconClass} animate-spin ${children ? 'mr-2' : ''}`} />
      )}
      
      {!loading && leftIcon && (
        <span className={`${iconClass} ${children ? 'mr-2' : ''}`}>
          {leftIcon}
        </span>
      )}
      
      {children}
      
      {!loading && rightIcon && (
        <span className={`${iconClass} ${children ? 'ml-2' : ''}`}>
          {rightIcon}
        </span>
      )}
    </button>
  );
});

Button.displayName = 'Button';

// Specialized button components
export const IconButton = forwardRef(({ 
  icon, 
  variant = 'ghost', 
  size = 'md',
  'aria-label': ariaLabel,
  ...props 
}, ref) => {
  const iconSizes = {
    xs: 'w-3 h-3',
    sm: 'w-4 h-4', 
    md: 'w-5 h-5',
    lg: 'w-6 h-6',
    xl: 'w-7 h-7'
  };
  
  const buttonSizes = {
    xs: 'p-1',
    sm: 'p-1.5',
    md: 'p-2', 
    lg: 'p-2.5',
    xl: 'p-3'
  };
  
  return (
    <Button
      ref={ref}
      variant={variant}
      className={`${buttonSizes[size]} rounded-full`}
      aria-label={ariaLabel}
      {...props}
    >
      <span className={iconSizes[size]}>
        {icon}
      </span>
    </Button>
  );
});

IconButton.displayName = 'IconButton';

export const ButtonGroup = ({ children, className = '', ...props }) => {
  return (
    <div 
      className={`inline-flex rounded-lg shadow-sm ${className}`}
      role="group"
      {...props}
    >
      {React.Children.map(children, (child, index) => {
        if (!React.isValidElement(child)) return child;
        
        const isFirst = index === 0;
        const isLast = index === React.Children.count(children) - 1;
        const isMiddle = !isFirst && !isLast;
        
        let additionalClasses = '';
        
        if (isFirst) {
          additionalClasses = 'rounded-r-none border-r-0';
        } else if (isLast) {
          additionalClasses = 'rounded-l-none';
        } else if (isMiddle) {
          additionalClasses = 'rounded-none border-r-0';
        }
        
        return React.cloneElement(child, {
          className: `${child.props.className || ''} ${additionalClasses}`.trim()
        });
      })}
    </div>
  );
};

export const FloatingActionButton = forwardRef(({
  icon,
  variant = 'primary',
  size = 'lg',
  position = 'bottom-right',
  className = '',
  ...props
}, ref) => {
  const positions = {
    'bottom-right': 'fixed bottom-6 right-6',
    'bottom-left': 'fixed bottom-6 left-6',
    'top-right': 'fixed top-6 right-6',
    'top-left': 'fixed top-6 left-6'
  };
  
  return (
    <IconButton
      ref={ref}
      icon={icon}
      variant={variant}
      size={size}
      className={`${positions[position]} shadow-lg hover:shadow-xl z-50 ${className}`}
      {...props}
    />
  );
});

FloatingActionButton.displayName = 'FloatingActionButton';

export const LoadingButton = forwardRef(({
  loading,
  loadingText,
  children,
  ...props
}, ref) => {
  return (
    <Button
      ref={ref}
      loading={loading}
      {...props}
    >
      {loading && loadingText ? loadingText : children}
    </Button>
  );
});

LoadingButton.displayName = 'LoadingButton';

export const SplitButton = ({ 
  mainAction, 
  dropdownActions = [], 
  variant = 'primary',
  size = 'md',
  ...props 
}) => {
  const [isOpen, setIsOpen] = React.useState(false);
  
  return (
    <div className="relative inline-flex">
      <Button
        variant={variant}
        size={size}
        className="rounded-r-none border-r-0"
        onClick={mainAction.onClick}
        {...props}
      >
        {mainAction.label}
      </Button>
      
      <div className="relative">
        <Button
          variant={variant}
          size={size}
          className="rounded-l-none px-2"
          onClick={() => setIsOpen(!isOpen)}
          aria-haspopup="true"
          aria-expanded={isOpen}
        >
          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </Button>
        
        {isOpen && (
          <>
            <div 
              className="fixed inset-0 z-10" 
              onClick={() => setIsOpen(false)}
            />
            <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border z-20">
              <div className="py-1">
                {dropdownActions.map((action, index) => (
                  <button
                    key={index}
                    className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    onClick={() => {
                      action.onClick();
                      setIsOpen(false);
                    }}
                  >
                    {action.label}
                  </button>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export const ToggleButton = forwardRef(({
  pressed = false,
  onPressedChange,
  children,
  variant = 'outline',
  ...props
}, ref) => {
  const handleClick = () => {
    onPressedChange?.(!pressed);
  };
  
  return (
    <Button
      ref={ref}
      variant={pressed ? 'primary' : variant}
      onClick={handleClick}
      aria-pressed={pressed}
      {...props}
    >
      {children}
    </Button>
  );
});

ToggleButton.displayName = 'ToggleButton';

export default Button;