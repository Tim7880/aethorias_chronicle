// Path: src/components/auth/ProtectedRoute.tsx
import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext'; // Adjust path if your AuthContext is elsewhere

const ProtectedRoute: React.FC = () => {
  const auth = useAuth();
  const location = useLocation();

  if (auth.isLoading) {
    // You can return a loading spinner or a blank page while auth state is being determined
    // especially on initial app load when checking for a stored token.
    return <div style={{textAlign: 'center', paddingTop: '100px', fontFamily: 'var(--font-body-primary)'}}>Verifying Scribe's Credentials...</div>;
  }

  if (!auth.isAuthenticated) {
    // User not authenticated, redirect to login page.
    // Pass the current location in state so we can redirect back after login.
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // User is authenticated, render the child routes (via Outlet)
  return <Outlet />;
};

export default ProtectedRoute;