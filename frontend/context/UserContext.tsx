// context/UserContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/lib/types/user';
import { getCookie } from '@/lib/utils/cookies';
import { getCurrentUser } from '@/lib/api/auth';

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
} | null>(null);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const refreshUser = async () => {
    setLoading(true);
    try {
      const accessToken = getCookie('access_token');
      if (!accessToken) {
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
  }, []);

  return (
    <UserContext.Provider value={{ user, setUser, loading, refreshUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) throw new Error('useUser must be used within UserProvider');
  return context;
}
