'use client';

import React from 'react';
import { useTokenExpiration } from '@/lib/hooks/useTokenExpiration';
import { TokenRefreshPopup } from './TokenRefreshPopup';
import { useUser } from '@/context/UserContext';
import { useRouter } from 'next/navigation';

export function TokenManager() {
  const { user } = useUser();
  const router = useRouter();
  const { 
    showPopup, 
    timeRemaining, 
    isExpired, 
    resetTimer, 
    dismissPopup 
  } = useTokenExpiration(5); // Show popup 5 minutes before expiration

  // Redirect to login if token is expired and user was logged in
  React.useEffect(() => {
    if (isExpired && user) {
      console.log('Token expired, redirecting to login');
      router.push('/login');
    }
  }, [isExpired, user, router]);

  // Only show popup for authenticated users
  if (!user) {
    return null;
  }

  const handleRefresh = async () => {
    resetTimer();
  };

  return (
    <TokenRefreshPopup
      isOpen={showPopup}
      onClose={dismissPopup}
      onRefresh={handleRefresh}
      timeRemaining={timeRemaining}
    />
  );
}
