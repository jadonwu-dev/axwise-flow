'use client';

import { useAuth } from '@clerk/nextjs';
import { initializeApp } from 'firebase/app';
import { getAuth, signInWithCustomToken, signOut } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { useState, useEffect } from 'react';

/**
 * Official Clerk-Firebase Integration Component
 * Following the official Clerk documentation pattern:
 * https://clerk.com/docs/integrations/databases/firebase
 */

// Firebase configuration object
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

// Initialize Firebase app
const app = initializeApp(firebaseConfig);
// Connect to Firebase auth
const auth = getAuth(app);
// Connect to Firestore database
const db = getFirestore(app);

interface FirebaseAuthProps {
  children?: React.ReactNode;
}

export function FirebaseAuth({ children }: FirebaseAuthProps) {
  const { getToken, userId, isSignedIn } = useAuth();
  const [isFirebaseSignedIn, setIsFirebaseSignedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle if the user is not signed in with Clerk
  if (!userId) {
    return (
      <div className="p-4 text-center">
        <p>You need to sign in with Clerk to access Firebase features.</p>
      </div>
    );
  }

  // Sign into Firebase with Clerk token (official method)
  const signIntoFirebaseWithClerk = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Get Firebase token from Clerk using the official integration template
      const token = await getToken({ template: 'integration_firebase' });
      
      if (!token) {
        throw new Error('Failed to get Firebase token from Clerk');
      }

      // Sign in to Firebase with the custom token (official method)
      const userCredentials = await signInWithCustomToken(auth, token);
      
      console.log('Successfully signed into Firebase:', userCredentials.user);
      setIsFirebaseSignedIn(true);
    } catch (err) {
      console.error('Error signing into Firebase:', err);
      setError(err instanceof Error ? err.message : 'Failed to sign into Firebase');
    } finally {
      setIsLoading(false);
    }
  };

  // Sign out from Firebase
  const signOutFromFirebase = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      await signOut(auth);
      console.log('Successfully signed out from Firebase');
      setIsFirebaseSignedIn(false);
    } catch (err) {
      console.error('Error signing out from Firebase:', err);
      setError(err instanceof Error ? err.message : 'Failed to sign out from Firebase');
    } finally {
      setIsLoading(false);
    }
  };

  // Auto sign-in when Clerk user is available
  useEffect(() => {
    if (isSignedIn && userId && !isFirebaseSignedIn && !isLoading) {
      signIntoFirebaseWithClerk();
    }
  }, [isSignedIn, userId, isFirebaseSignedIn, isLoading]);

  return (
    <div className="space-y-4">
      <div className="bg-card p-6 rounded-lg border">
        <h2 className="text-xl font-semibold mb-4">Firebase Authentication Status</h2>
        
        <div className="space-y-2 mb-4">
          <p><strong>Clerk User ID:</strong> {userId}</p>
          <p><strong>Firebase Signed In:</strong> {isFirebaseSignedIn ? '✅ Yes' : '❌ No'}</p>
          <p><strong>Loading:</strong> {isLoading ? '⏳ Yes' : '✅ No'}</p>
          {error && <p className="text-destructive"><strong>Error:</strong> {error}</p>}
        </div>

        <div className="space-x-4">
          {!isFirebaseSignedIn ? (
            <button 
              onClick={signIntoFirebaseWithClerk}
              disabled={isLoading}
              className="bg-primary text-primary-foreground px-4 py-2 rounded hover:bg-primary/90 disabled:opacity-50"
            >
              {isLoading ? 'Signing in...' : 'Sign into Firebase'}
            </button>
          ) : (
            <button 
              onClick={signOutFromFirebase}
              disabled={isLoading}
              className="bg-destructive text-destructive-foreground px-4 py-2 rounded hover:bg-destructive/90 disabled:opacity-50"
            >
              {isLoading ? 'Signing out...' : 'Sign out from Firebase'}
            </button>
          )}
        </div>
      </div>

      {children}
    </div>
  );
}

// Export Firebase instances for use in other components
export { auth, db, app };
