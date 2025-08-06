// context/UserContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/lib/types/user';
import { getCookie } from '@/lib/utils/cookies';
import { getCurrentUser, refreshToken } from '@/lib/api/auth';
import { isTokenExpired, isTokenExpiringSoon } from '@/lib/utils/jwt';

// Hook to get JWT token from cookie
export function useToken(): string | null {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const accessToken = getCookie('access_token');
    setToken(accessToken);
  }, []);

  return token;
}

export const UserContext = createContext<{
  user: User | null;
  setUser: (user: User | null) => void;
  loading: boolean;
  refreshUser: () => Promise<void>;
  checkAndRefreshToken: () => Promise<boolean>;
} | null>(null);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const checkAndRefreshToken = async (): Promise<boolean> => {
    try {
      const accessToken = getCookie('access_token');
      
      if (!accessToken) {
        console.log('No token found');
        return false;
      }

      if (isTokenExpired(accessToken)) {
        console.log('Token is expired');
        setUser(null);
        return false;
      }

      // If token expires in the next 5 minutes, refresh it
      if (isTokenExpiringSoon(accessToken, 5)) {
        console.log('Token expires soon, refreshing...');
        try {
          await refreshToken();
          console.log('Token refreshed successfully');
          return true;
        } catch (error) {
          console.error('Failed to refresh token:', error);
          setUser(null);
          return false;
        }
      }

      return true;
    } catch (error) {
      console.error('Error checking token:', error);
      return false;
    }
  };

  const refreshUser = async () => {
    setLoading(true);
    try {
      const accessToken = getCookie('access_token');
      if (!accessToken) {
        setUser(null);
        return;
      }

      // Check if token is valid before making the request
      if (isTokenExpired(accessToken)) {
        console.log('Token expired, clearing user');
        setUser(null);
        return;
      }

      const userResponse = await getCurrentUser();
      setUser(userResponse);
    } catch (error) {
      console.error('Error fetching current user:', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();

    // Set up interval to check token expiration every minute
    const interval = setInterval(async () => {
      const isValid = await checkAndRefreshToken();
      if (!isValid && user) {
        // Token is invalid and user is logged in, refresh user state
        await refreshUser();
      }
    }, 60000); // Check every minute

    return () => clearInterval(interval);
  }, []);

  return (
    <UserContext.Provider value={{ user, setUser, loading, refreshUser, checkAndRefreshToken }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) throw new Error('useUser must be used within UserProvider');
  return context;
}
