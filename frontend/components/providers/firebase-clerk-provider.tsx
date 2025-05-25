'use client';

import { createContext, useContext, ReactNode, useState, useEffect } from 'react';
import { useAuth as useClerkAuth } from '@clerk/nextjs';
import { User as FirebaseUser } from 'firebase/auth';
import { useSyncClerkWithFirebase } from '@/lib/firebase-auth';
import { generateFirebaseToken } from '@/lib/firebase-functions';

// Define the context type
interface FirebaseClerkContextType {
  firebaseUser: FirebaseUser | null;
  isLoading: boolean;
  error: Error | null;
}

// Create the context with default values
const FirebaseClerkContext = createContext<FirebaseClerkContextType>({
  firebaseUser: null,
  isLoading: true,
  error: null,
});

// Hook to use the Firebase-Clerk context
export const useFirebaseClerkContext = () => useContext(FirebaseClerkContext);

interface FirebaseClerkProviderProps {
  children: ReactNode;
}

/**
 * Firebase-Clerk Provider component
 * Simplified implementation - temporarily disabled Firebase integration
 * to focus on getting Clerk authentication working first
 */
export function FirebaseClerkProvider({ children }: FirebaseClerkProviderProps): JSX.Element {
  // Provide a simple context without Firebase integration for now
  const authState: FirebaseClerkContextType = {
    firebaseUser: null,
    isLoading: false,
    error: null
  };

  return (
    <FirebaseClerkContext.Provider value={authState}>
      {children}
    </FirebaseClerkContext.Provider>
  );
}
