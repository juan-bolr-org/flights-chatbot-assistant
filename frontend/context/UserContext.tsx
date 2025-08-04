// context/UserContext.tsx
'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '@/lib/types/user';

function parseJwt(tokenLocal: string): Partial<User> | null {
  try {
    const payload = JSON.parse(atob(tokenLocal.split('.')[1]));
    return {
      id: payload?.user_id || '',
      name: payload?.name || '',
      email: payload?.email || '',
      token: {
        access_token: tokenLocal,
        token_type: ''
      },
    };
  } catch (error) {
    console.error("Error parsing token", error);
    return null;
  }
}

export const UserContext = createContext<{
  user: User | null;
  setUser: (user: User | null) => void;
} | null>(null);

export function UserProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      const decodedUser = parseJwt(token);
      if (decodedUser) setUser(decodedUser as User);
    }
  }, []);

  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  const context = useContext(UserContext);
  if (!context) throw new Error('useUser debe usarse dentro de UserProvider');
  return context;
}
