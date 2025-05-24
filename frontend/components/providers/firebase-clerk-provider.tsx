'use client';

import { createContext, useContext, ReactNode } from 'react';
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
 * Simplified implementation for Firebase App Hosting
 * Synchronizes authentication state between Clerk and Firebase
 */
export function FirebaseClerkProvider({ children }: FirebaseClerkProviderProps): JSX.Element {
  // Use Clerk's standard auth hook
  const { isSignedIn, userId, getToken } = useClerkAuth();

  // Simplified token generation function
  const getFirebaseToken = async (): Promise<string | null> => {
    if (!isSignedIn || !userId) {
      return null;
    }

    try {
      // Use Cloud Function to generate Firebase token
      const firebaseToken = await generateFirebaseToken(userId);
      return firebaseToken;
    } catch (error) {
      console.error('Error getting Firebase token:', error);
      return null;
    }
  };

  // Use the custom hook to sync Clerk and Firebase auth
  const { firebaseUser, loading, error } = useSyncClerkWithFirebase(
    getFirebaseToken,
    !!isSignedIn
  );

  // Provide the auth state to the application
  return (
    <FirebaseClerkContext.Provider
      value={{
        firebaseUser,
        isLoading: loading,
        error
      }}
    >
      {children}
    </FirebaseClerkContext.Provider>
  );
}
