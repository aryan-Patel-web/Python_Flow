import React, { useEffect, useRef } from 'react';
import { X } from 'lucide-react';

const Modal = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  showCloseButton = true,
  closeOnOverlayClick = true,
  closeOnEscape = true,
  className = '',
  headerClassName = '',
  bodyClassName = '',
  footerClassName = '',
  footer = null
}) => {
  const modalRef = useRef(null);
  const previousActiveElement = useRef(null);

  // Size configurations
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    '2xl': 'max-w-6xl',
    full: 'max-w-full mx-4'
  };

  useEffect(() => {
    if (isOpen) {
      // Store the currently focused element
      previousActiveElement.current = document.activeElement;
      
      // Prevent body scroll
      document.body.style.overflow = 'hidden';
      
      // Focus the modal
      if (modalRef.current) {
        modalRef.current.focus();
      }
    } else {
      // Restore body scroll
      document.body.style.overflow = 'unset';
      
      // Restore focus to previously active element
      if (previousActiveElement.current) {
        previousActiveElement.current.focus();
      }
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && closeOnEscape && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose, closeOnEscape]);

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget && closeOnOverlayClick) {
      onClose();
    }
  };

  const handleModalClick = (e) => {
    e.stopPropagation();
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black bg-opacity-50 backdrop-blur-sm"
      onClick={handleOverlayClick}
      role="dialog"
      aria-modal="true"
      aria-labelledby={title ? "modal-title" : undefined}
    >
      <div
        ref={modalRef}
        className={`
          bg-white rounded-lg shadow-xl w-full ${sizeClasses[size]} 
          max-h-[90vh] overflow-hidden flex flex-col
          transform transition-all duration-200 ease-out
          ${className}
        `}
        onClick={handleModalClick}
        tabIndex={-1}
      >
        {/* Header */}
        {(title || showCloseButton) && (
          <div className={`flex items-center justify-between p-6 border-b ${headerClassName}`}>
            {title && (
              <h2 id="modal-title" className="text-lg font-semibold text-gray-900">
                {title}
              </h2>
            )}
            {showCloseButton && (
              <button
                onClick={onClose}
                className="p-1 text-gray-400 hover:text-gray-600 transition-colors rounded-lg hover:bg-gray-100"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            )}
          </div>
        )}

        {/* Body */}
        <div className={`flex-1 overflow-y-auto ${bodyClassName}`}>
          {children}
        </div>

        {/* Footer */}
        {footer && (
          <div className={`border-t bg-gray-50 ${footerClassName}`}>
            {footer}
          </div>
        )}
      </div>
    </div>
  );
};

// Pre-configured modal variants
export const ConfirmModal = ({
  isOpen,
  onClose,
  onConfirm,
  title = "Confirm Action",
  message = "Are you sure you want to proceed?",
  confirmText = "Confirm",
  cancelText = "Cancel",
  confirmVariant = "danger"
}) => {
  const confirmButtonClasses = {
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    success: 'bg-green-600 hover:bg-green-700 text-white'
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <div className="flex justify-end space-x-3 p-4">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            {cancelText}
          </button>
          <button
            onClick={() => {
              onConfirm();
              onClose();
            }}
            className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${confirmButtonClasses[confirmVariant]}`}
          >
            {confirmText}
          </button>
        </div>
      }
    >
      <div className="p-6">
        <p className="text-gray-600">{message}</p>
      </div>
    </Modal>
  );
};

export const AlertModal = ({
  isOpen,
  onClose,
  title = "Alert",
  message,
  type = "info",
  buttonText = "OK"
}) => {
  const typeStyles = {
    info: { bg: 'bg-blue-50', text: 'text-blue-800', button: 'bg-blue-600 hover:bg-blue-700' },
    success: { bg: 'bg-green-50', text: 'text-green-800', button: 'bg-green-600 hover:bg-green-700' },
    warning: { bg: 'bg-yellow-50', text: 'text-yellow-800', button: 'bg-yellow-600 hover:bg-yellow-700' },
    error: { bg: 'bg-red-50', text: 'text-red-800', button: 'bg-red-600 hover:bg-red-700' }
  };

  const style = typeStyles[type];

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={title}
      size="sm"
      footer={
        <div className="flex justify-end p-4">
          <button
            onClick={onClose}
            className={`px-4 py-2 text-sm font-medium text-white rounded-md transition-colors ${style.button}`}
          >
            {buttonText}
          </button>
        </div>
      }
    >
      <div className={`p-6 ${style.bg}`}>
        <p className={`text-sm ${style.text}`}>{message}</p>
      </div>
    </Modal>
  );
};

export const LoadingModal = ({
  isOpen,
  title = "Loading...",
  message = "Please wait while we process your request."
}) => {
  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {}} // Can't close loading modal
      title={title}
      size="sm"
      showCloseButton={false}
      closeOnOverlayClick={false}
      closeOnEscape={false}
    >
      <div className="p-6 text-center">
        <div className="flex justify-center mb-4">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
        <p className="text-gray-600">{message}</p>
      </div>
    </Modal>
  );
};

export default Modal;