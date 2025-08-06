// lib/hooks/useAuthRedirect.ts
'use client';

import { useRouter, useSearchParams } from 'next/navigation';
import { useEffect } from 'react';

export function useAuthRedirect() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const redirectAfterLogin = () => {
    const redirectPath = searchParams.get('redirect');
    
    if (redirectPath && redirectPath !== '/login') {
      console.log(`Redirecting to: ${redirectPath}`);
      router.push(redirectPath);
    } else {
      console.log('Redirecting to default page: /flights');
      router.push('/flights');
    }
  };

  return { redirectAfterLogin };
}

// Hook to automatically redirect authenticated users away from auth pages
export function useRedirectIfAuthenticated(user: any, loading: boolean) {
  const router = useRouter();
  const searchParams = useSearchParams();

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
