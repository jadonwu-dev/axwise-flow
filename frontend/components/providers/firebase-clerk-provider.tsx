'use client';

import { createContext, useContext, ReactNode, useEffect, useState } from 'react';
import { useAuth as useClerkAuth } from '@clerk/nextjs';
import { User as FirebaseUser } from 'firebase/auth';
import { useSyncClerkWithFirebase } from '@/lib/firebase-auth';
import { generateFirebaseToken } from '@/lib/firebase-functions';
import { createSafeAuthHook, isSSG } from '@/lib/clerk-config';

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
 * This component provides Firebase authentication state to the application
 * It synchronizes the authentication state between Clerk and Firebase
 */
// Create a safe version of the Clerk useAuth hook
const useSafeAuth = createSafeAuthHook(useClerkAuth);

export function FirebaseClerkProvider({ children }: FirebaseClerkProviderProps): JSX.Element {
  // Use our safe auth hook that handles static site generation
  const { isSignedIn, userId, getToken } = useSafeAuth();
  const [tokenError, setTokenError] = useState<Error | null>(null);

  // Function to get a Firebase token from Clerk
  const getFirebaseToken = async (): Promise<string | null> => {
    try {
      // Skip token generation during static site generation
      if (isSSG || !isSignedIn || !userId) {
        return null;
      }

      // First try to get a token directly from Clerk
      try {
        // Check if Clerk has a Firebase template
        const clerkToken = await getToken({ template: 'firebase' });
        if (clerkToken) {
          return clerkToken;
        }
      } catch (clerkError) {
        console.log('No Firebase template in Clerk, using Cloud Function instead');
      }

      // If Clerk doesn't have a Firebase template, use our Cloud Function
      const firebaseToken = await generateFirebaseToken(userId);
      return firebaseToken;
    } catch (error) {
      // Don't set error during static site generation
      if (!isSSG) {
        console.error('Error getting Firebase token:', error);
        setTokenError(error instanceof Error ? error : new Error(String(error)));
      }
      return null;
    }
  };

  // Use the custom hook to sync Clerk and Firebase auth
  const { firebaseUser, loading, error } = useSyncClerkWithFirebase(
    getFirebaseToken,
    !!isSignedIn && !isSSG
  );

  // Combine errors
  const combinedError = error || tokenError;

  // Provide the auth state to the application
  return (
    <FirebaseClerkContext.Provider
      value={{
        firebaseUser,
        isLoading: loading,
        error: combinedError
      }}
    >
      {children}
    </FirebaseClerkContext.Provider>
  );
}
