// components/auth/ProtectedRoute.tsx
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser } from '@/context/UserContext';
import { getCookie } from '@/lib/utils/cookies';
import { isTokenExpired } from '@/lib/utils/jwt';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  requireAuth?: boolean;
}

export function ProtectedRoute({ 
  children, 
  fallback = <div>Loading...</div>, 
  requireAuth = true 
}: ProtectedRouteProps) {
  const { user, loading, refreshUser } = useUser();
  const router = useRouter();

  useEffect(() => {
    if (!loading && requireAuth) {
      const token = getCookie('access_token');
      
      // No token or expired token
      if (!token || isTokenExpired(token)) {
        console.log('ProtectedRoute: No valid token, redirecting to login');
        router.push('/login');
        return;
      }

      // Token exists but no user data
      if (!user && token && !isTokenExpired(token)) {
        console.log('ProtectedRoute: Token exists but no user, refreshing...');
        refreshUser();
      }
    }
  }, [user, loading, requireAuth, router, refreshUser]);

  // Show loading while checking authentication
  if (loading) {
    return <>{fallback}</>;
  }

  // If authentication is required but user is not authenticated
  if (requireAuth && !user) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

// Higher-order component version
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  requireAuth: boolean = true
) {
  return function AuthenticatedComponent(props: P) {
    return (
      <ProtectedRoute requireAuth={requireAuth}>
        <Component {...props} />
      </ProtectedRoute>
    );
  };
}
