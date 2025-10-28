'use client';

import { useRouter } from 'next/navigation';
import { ReactNode, useEffect, createContext } from 'react';

interface AuthContextType {
  userId: string | null;
  isAuthenticated: boolean;
}

export const DashboardAuthContext = createContext<AuthContextType>({ 
  userId: null, 
  isAuthenticated: false 
});

interface DashboardAuthProviderProps {
  children: ReactNode;
}

export const DashboardAuthProvider = ({ children }: DashboardAuthProviderProps): JSX.Element => {
  // OSS mode: always authenticated with a static user ID
  const userId = 'oss-mode-user';

  return (
    <DashboardAuthContext.Provider value={{
      userId,
      isAuthenticated: true
    }}>
      {children}
    </DashboardAuthContext.Provider>
  );
};