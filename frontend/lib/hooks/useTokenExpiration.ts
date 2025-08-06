'use client';

import { useState, useEffect, useCallback } from 'react';
import { getCookie } from '@/lib/utils/cookies';
import { isTokenExpired, getTokenExpirationTime } from '@/lib/utils/jwt';

interface UseTokenExpirationReturn {
  showPopup: boolean;
  timeRemaining: number; // in minutes
  isExpired: boolean;
  resetTimer: () => void;
  dismissPopup: () => void;
}

export function useTokenExpiration(
  warningMinutes: number = 5
): UseTokenExpirationReturn {
  const [showPopup, setShowPopup] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isExpired, setIsExpired] = useState(false);
  const [popupDismissed, setPopupDismissed] = useState(false);

  const checkTokenExpiration = useCallback(() => {
    const token = getCookie('access_token');
    
    if (!token) {
      setIsExpired(true);
      setShowPopup(false);
      return;
    }

    if (isTokenExpired(token)) {
      setIsExpired(true);
      setShowPopup(false);
      return;
    }

    const expirationTime = getTokenExpirationTime(token);
    if (!expirationTime) return;

    const now = Math.floor(Date.now() / 1000);
    const timeLeftSeconds = expirationTime - now;
    const timeLeftMinutes = timeLeftSeconds / 60;

    setTimeRemaining(timeLeftMinutes);
    setIsExpired(false);

    // Show popup if token expires within warning time and hasn't been dismissed
    if (timeLeftMinutes <= warningMinutes && timeLeftMinutes > 0 && !popupDismissed) {
      setShowPopup(true);
    } else if (timeLeftMinutes > warningMinutes) {
      // Reset popup state if we're back outside warning window
      setShowPopup(false);
      setPopupDismissed(false);
    }
  }, [warningMinutes, popupDismissed]);

  const resetTimer = useCallback(() => {
    setPopupDismissed(false);
    setShowPopup(false);
    checkTokenExpiration();
  }, [checkTokenExpiration]);

  const dismissPopup = useCallback(() => {
    setShowPopup(false);
    setPopupDismissed(true);
  }, []);

  useEffect(() => {
    // Initial check
    checkTokenExpiration();

    // Check every 30 seconds
    const interval = setInterval(checkTokenExpiration, 30000);

    return () => clearInterval(interval);
  }, [checkTokenExpiration]);

  return {
    showPopup,
    timeRemaining,
    isExpired,
    resetTimer,
    dismissPopup
  };
}
