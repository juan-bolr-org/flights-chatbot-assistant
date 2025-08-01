'use client';

import { createContext, useContext } from 'react';

type User = { name: string } | null;

export const UserContext = createContext<{
    user: User;
    setUser: (user: User) => void;
}>({
    user: null,
    setUser: () => { },
});

export const useUser = () => useContext(UserContext);
