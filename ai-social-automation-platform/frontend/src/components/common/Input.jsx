import React, { forwardRef, useState } from 'react';
import { Eye, EyeOff, Search, X, AlertCircle, CheckCircle, Info } from 'lucide-react';

const Input = forwardRef(({
  type = 'text',
  label,
  placeholder,
  value,
  onChange,
  error,
  success,
  hint,
  required = false,
  disabled = false,
  fullWidth = false,
  size = 'md',
  leftIcon,
  rightIcon,
  leftElement,
  rightElement,
  className = '',
  containerClassName = '',
  labelClassName = '',
  ...props
}, ref) => {
  
  const [showPassword, setShowPassword] = useState(false);
  const [focused, setFocused] = useState(false);
  
  const baseClasses = 'block border rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  };
  
  const variants = {
    default: 'border-gray-300 focus:border-blue-500 focus:ring-blue-500',
    error: 'border-red-300 focus:border-red-500 focus:ring-red-500',
    success: 'border-green-300 focus:border-green-500 focus:ring-green-500'
  };
  
  const getVariant = () => {
    if (error) return 'error';
    if (success) return 'success';
    return 'default';
  };
  
  const hasLeftElement = leftIcon || leftElement;
  const hasRightElement = rightIcon || rightElement || type === 'password' || type === 'search';
  
  const inputClasses = [
    baseClasses,
    sizes[size],
    variants[getVariant()],
    hasLeftElement ? 'pl-10' : '',
    hasRightElement ? 'pr-10' : '',
    fullWidth ? 'w-full' : '',
    className
  ].filter(Boolean).join(' ');
  
  const iconSize = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4';
  
  const handlePasswordToggle = () => {
    setShowPassword(!showPassword);
  };
  
  const inputType = type === 'password' && showPassword ? 'text' : type;
  
  return (
    <div className={`${fullWidth ? 'w-full' : ''} ${containerClassName}`}>
      {/* Label */}
      {label && (
        <label className={`block text-sm font-medium text-gray-700 mb-1 ${labelClassName}`}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {/* Input Container */}
      <div className="relative">
        {/* Left Icon/Element */}
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span className={`text-gray-400 ${iconSize}`}>
              {leftIcon}
            </span>
          </div>
        )}
        
        {leftElement && (
          <div className="absolute inset-y-0 left-0 flex items-center">
            {leftElement}
          </div>
        )}
        
        {/* Input */}
        <input
          ref={ref}
          type={inputType}
          value={value}
          onChange={onChange}
          placeholder={placeholder}
          disabled={disabled}
          required={required}
          className={inputClasses}
          onFocus={() => setFocused(true)}
          onBlur={() => setFocused(false)}
          {...props}
        />
        
        {/* Right Icon/Element */}
        {type === 'password' && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <button
              type="button"
              onClick={handlePasswordToggle}
              className="text-gray-400 hover:text-gray-600 focus:outline-none"
              tabIndex={-1}
            >
              {showPassword ? (
                <EyeOff className={iconSize} />
              ) : (
                <Eye className={iconSize} />
              )}
            </button>
          </div>
        )}
        
        {type === 'search' && value && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
            <button
              type="button"
              onClick={() => onChange?.({ target: { value: '' } })}
              className="text-gray-400 hover:text-gray-600 focus:outline-none"
              tabIndex={-1}
            >
              <X className={iconSize} />
            </button>
          </div>
        )}
        
        {rightIcon && type !== 'password' && type !== 'search' && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <span className={`text-gray-400 ${iconSize}`}>
              {rightIcon}
            </span>
          </div>
        )}
        
        {rightElement && (
          <div className="absolute inset-y-0 right-0 flex items-center">
            {rightElement}
          </div>
        )}
      </div>
      
      {/* Helper Text */}
      <div className="mt-1">
        {error && (
          <p className="text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
            {error}
          </p>
        )}
        
        {success && !error && (
          <p className="text-sm text-green-600 flex items-center">
            <CheckCircle className="w-4 h-4 mr-1 flex-shrink-0" />
            {success}
          </p>
        )}
        
        {hint && !error && !success && (
          <p className="text-sm text-gray-500 flex items-center">
            <Info className="w-4 h-4 mr-1 flex-shrink-0" />
            {hint}
          </p>
        )}
      </div>
    </div>
  );
});

Input.displayName = 'Input';

// Specialized input components
export const SearchInput = forwardRef(({
  onClear,
  showClearButton = true,
  ...props
}, ref) => {
  return (
    <Input
      ref={ref}
      type="search"
      leftIcon={<Search />}
      {...props}
    />
  );
});

SearchInput.displayName = 'SearchInput';

export const PasswordInput = forwardRef((props, ref) => {
  return (
    <Input
      ref={ref}
      type="password"
      {...props}
    />
  );
});

PasswordInput.displayName = 'PasswordInput';

export const NumberInput = forwardRef(({
  min,
  max,
  step = 1,
  showSteppers = false,
  onIncrement,
  onDecrement,
  ...props
}, ref) => {
  const handleIncrement = () => {
    const currentValue = parseFloat(props.value) || 0;
    const newValue = currentValue + step;
    if (!max || newValue <= max) {
      props.onChange?.({ target: { value: newValue.toString() } });
      onIncrement?.(newValue);
    }
  };

  const handleDecrement = () => {
    const currentValue = parseFloat(props.value) || 0;
    const newValue = currentValue - step;
    if (!min || newValue >= min) {
      props.onChange?.({ target: { value: newValue.toString() } });
      onDecrement?.(newValue);
    }
  };

  const stepperButtons = showSteppers && (
    <div className="absolute inset-y-0 right-0 flex flex-col">
      <button
        type="button"
        onClick={handleIncrement}
        className="px-2 py-1 text-gray-400 hover:text-gray-600 focus:outline-none border-l border-gray-300"
        tabIndex={-1}
      >
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
        </svg>
      </button>
      <button
        type="button"
        onClick={handleDecrement}
        className="px-2 py-1 text-gray-400 hover:text-gray-600 focus:outline-none border-l border-t border-gray-300"
        tabIndex={-1}
      >
        <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
          <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
        </svg>
      </button>
    </div>
  );

  return (
    <Input
      ref={ref}
      type="number"
      min={min}
      max={max}
      step={step}
      rightElement={stepperButtons}
      {...props}
    />
  );
});

NumberInput.displayName = 'NumberInput';

export const TextArea = forwardRef(({
  label,
  placeholder,
  value,
  onChange,
  error,
  success,
  hint,
  required = false,
  disabled = false,
  fullWidth = false,
  rows = 4,
  resize = 'vertical',
  maxLength,
  showCharCount = false,
  className = '',
  containerClassName = '',
  labelClassName = '',
  ...props
}, ref) => {
  
  const baseClasses = 'block w-full border rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed px-3 py-2 text-sm';
  
  const variants = {
    default: 'border-gray-300 focus:border-blue-500 focus:ring-blue-500',
    error: 'border-red-300 focus:border-red-500 focus:ring-red-500',
    success: 'border-green-300 focus:border-green-500 focus:ring-green-500'
  };
  
  const resizeClasses = {
    none: 'resize-none',
    vertical: 'resize-y',
    horizontal: 'resize-x',
    both: 'resize'
  };
  
  const getVariant = () => {
    if (error) return 'error';
    if (success) return 'success';
    return 'default';
  };
  
  const textareaClasses = [
    baseClasses,
    variants[getVariant()],
    resizeClasses[resize],
    fullWidth ? 'w-full' : '',
    className
  ].filter(Boolean).join(' ');
  
  const characterCount = value ? value.length : 0;
  const isOverLimit = maxLength && characterCount > maxLength;
  
  return (
    <div className={`${fullWidth ? 'w-full' : ''} ${containerClassName}`}>
      {/* Label */}
      {label && (
        <label className={`block text-sm font-medium text-gray-700 mb-1 ${labelClassName}`}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {/* TextArea */}
      <textarea
        ref={ref}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={disabled}
        required={required}
        rows={rows}
        maxLength={maxLength}
        className={textareaClasses}
        {...props}
      />
      
      {/* Footer */}
      <div className="mt-1 flex justify-between">
        <div>
          {error && (
            <p className="text-sm text-red-600 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
              {error}
            </p>
          )}
          
          {success && !error && (
            <p className="text-sm text-green-600 flex items-center">
              <CheckCircle className="w-4 h-4 mr-1 flex-shrink-0" />
              {success}
            </p>
          )}
          
          {hint && !error && !success && (
            <p className="text-sm text-gray-500 flex items-center">
              <Info className="w-4 h-4 mr-1 flex-shrink-0" />
              {hint}
            </p>
          )}
        </div>
        
        {/* Character Count */}
        {(showCharCount || maxLength) && (
          <div className={`text-sm ${isOverLimit ? 'text-red-600' : 'text-gray-500'}`}>
            {characterCount}{maxLength && `/${maxLength}`}
          </div>
        )}
      </div>
    </div>
  );
});

TextArea.displayName = 'TextArea';

export const Select = forwardRef(({
  label,
  placeholder = 'Select an option...',
  value,
  onChange,
  options = [],
  error,
  success,
  hint,
  required = false,
  disabled = false,
  fullWidth = false,
  size = 'md',
  leftIcon,
  className = '',
  containerClassName = '',
  labelClassName = '',
  ...props
}, ref) => {
  
  const baseClasses = 'block border rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-0 disabled:opacity-50 disabled:cursor-not-allowed appearance-none bg-white';
  
  const sizes = {
    sm: 'px-3 py-2 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  };
  
  const variants = {
    default: 'border-gray-300 focus:border-blue-500 focus:ring-blue-500',
    error: 'border-red-300 focus:border-red-500 focus:ring-red-500',
    success: 'border-green-300 focus:border-green-500 focus:ring-green-500'
  };
  
  const getVariant = () => {
    if (error) return 'error';
    if (success) return 'success';
    return 'default';
  };
  
  const hasLeftIcon = leftIcon;
  
  const selectClasses = [
    baseClasses,
    sizes[size],
    variants[getVariant()],
    hasLeftIcon ? 'pl-10' : '',
    'pr-10', // Always add right padding for arrow
    fullWidth ? 'w-full' : '',
    className
  ].filter(Boolean).join(' ');
  
  const iconSize = size === 'sm' ? 'w-4 h-4' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4';
  
  return (
    <div className={`${fullWidth ? 'w-full' : ''} ${containerClassName}`}>
      {/* Label */}
      {label && (
        <label className={`block text-sm font-medium text-gray-700 mb-1 ${labelClassName}`}>
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}
      
      {/* Select Container */}
      <div className="relative">
        {/* Left Icon */}
        {leftIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <span className={`text-gray-400 ${iconSize}`}>
              {leftIcon}
            </span>
          </div>
        )}
        
        {/* Select */}
        <select
          ref={ref}
          value={value}
          onChange={onChange}
          disabled={disabled}
          required={required}
          className={selectClasses}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option, index) => (
            <option 
              key={typeof option === 'object' ? option.value : index} 
              value={typeof option === 'object' ? option.value : option}
              disabled={typeof option === 'object' ? option.disabled : false}
            >
              {typeof option === 'object' ? option.label : option}
            </option>
          ))}
        </select>
        
        {/* Dropdown Arrow */}
        <div className="absolute inset-y-0 right-0 flex items-center px-2 pointer-events-none">
          <svg className="w-4 h-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </div>
      </div>
      
      {/* Helper Text */}
      <div className="mt-1">
        {error && (
          <p className="text-sm text-red-600 flex items-center">
            <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
            {error}
          </p>
        )}
        
        {success && !error && (
          <p className="text-sm text-green-600 flex items-center">
            <CheckCircle className="w-4 h-4 mr-1 flex-shrink-0" />
            {success}
          </p>
        )}
        
        {hint && !error && !success && (
          <p className="text-sm text-gray-500 flex items-center">
            <Info className="w-4 h-4 mr-1 flex-shrink-0" />
            {hint}
          </p>
        )}
      </div>
    </div>
  );
});

Select.displayName = 'Select';

export const Checkbox = forwardRef(({
  label,
  description,
  checked,
  onChange,
  disabled = false,
  size = 'md',
  error,
  className = '',
  ...props
}, ref) => {
  
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  };
  
  const checkboxClasses = [
    'rounded border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2 disabled:opacity-50',
    sizes[size],
    error ? 'border-red-300' : '',
    className
  ].filter(Boolean).join(' ');
  
  return (
    <div className="flex items-start">
      <div className="flex items-center h-5">
        <input
          ref={ref}
          type="checkbox"
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          className={checkboxClasses}
          {...props}
        />
      </div>
      {(label || description) && (
        <div className="ml-3 text-sm">
          {label && (
            <label className={`font-medium ${disabled ? 'text-gray-400' : 'text-gray-700'}`}>
              {label}
            </label>
          )}
          {description && (
            <p className={`${disabled ? 'text-gray-400' : 'text-gray-500'} ${label ? 'mt-1' : ''}`}>
              {description}
            </p>
          )}
          {error && (
            <p className="text-red-600 mt-1 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
              {error}
            </p>
          )}
        </div>
      )}
    </div>
  );
});

Checkbox.displayName = 'Checkbox';

export const Radio = forwardRef(({
  label,
  description,
  name,
  value,
  checked,
  onChange,
  disabled = false,
  size = 'md',
  error,
  className = '',
  ...props
}, ref) => {
  
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-5 h-5', 
    lg: 'w-6 h-6'
  };
  
  const radioClasses = [
    'border-gray-300 text-blue-600 focus:ring-blue-500 focus:ring-2 disabled:opacity-50',
    sizes[size],
    error ? 'border-red-300' : '',
    className
  ].filter(Boolean).join(' ');
  
  return (
    <div className="flex items-start">
      <div className="flex items-center h-5">
        <input
          ref={ref}
          type="radio"
          name={name}
          value={value}
          checked={checked}
          onChange={onChange}
          disabled={disabled}
          className={radioClasses}
          {...props}
        />
      </div>
      {(label || description) && (
        <div className="ml-3 text-sm">
          {label && (
            <label className={`font-medium ${disabled ? 'text-gray-400' : 'text-gray-700'}`}>
              {label}
            </label>
          )}
          {description && (
            <p className={`${disabled ? 'text-gray-400' : 'text-gray-500'} ${label ? 'mt-1' : ''}`}>
              {description}
            </p>
          )}
          {error && (
            <p className="text-red-600 mt-1 flex items-center">
              <AlertCircle className="w-4 h-4 mr-1 flex-shrink-0" />
              {error}
            </p>
          )}
        </div>
      )}
    </div>
  );
});

Radio.displayName = 'Radio';

export default Input;