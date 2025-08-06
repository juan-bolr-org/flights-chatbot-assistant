// lib/hooks/useAuthRedirect.ts
'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';

function useSearchParamsSafe() {
  const [params, setParams] = useState<URLSearchParams | null>(null);
  
  useEffect(() => {
    // Only access searchParams on the client side after hydration
    if (typeof window !== 'undefined') {
      try {
        const searchParams = new URLSearchParams(window.location.search);
        setParams(searchParams);
      } catch {
        setParams(new URLSearchParams());
      }
    }
  }, []);

  return params || new URLSearchParams();
}

export function useAuthRedirect() {
  const router = useRouter();
  const searchParams = useSearchParamsSafe();

  const redirectAfterLogin = () => {
    const redirectPath = searchParams.get('redirect');
    const targetPath = (redirectPath && redirectPath !== '/login') ? redirectPath : '/flights';
    
    console.log(`Redirecting to: ${targetPath}`);
    
    // Use window.location.href for full page reload to ensure middleware sees the cookie
    window.location.href = targetPath;
  };

  return { redirectAfterLogin };
}

// Hook to automatically redirect authenticated users away from auth pages
export function useRedirectIfAuthenticated(user: any, loading: boolean) {
  const router = useRouter();
  const searchParams = useSearchParamsSafe();

  useEffect(() => {
    if (!loading && user) {
      const redirectPath = searchParams.get('redirect');
      
      if (redirectPath && redirectPath !== '/login' && redirectPath !== '/register') {
        router.push(redirectPath);
      } else {
        router.push('/flights');
      }
    }
  }, [user, loading, router, searchParams]);
}
