import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthContext } from '../context/AuthContext';
import LoadingSpinner from './common/LoadingSpinner';

const PublicRoute = ({ children }) => {
  const { user, loading, isAuthenticated } = useAuthContext();
  const location = useLocation();

  // Show loading spinner while checking authentication
  if (loading) {
    return <LoadingSpinner />;
  }

  // If authenticated, redirect to dashboard or intended page
  if (isAuthenticated && user) {
    const from = location.state?.from?.pathname || '/dashboard';
    return <Navigate to={from} replace />;
  }

  // User is not authenticated, show public route (login/register)
  return children;
};

export default PublicRoute;