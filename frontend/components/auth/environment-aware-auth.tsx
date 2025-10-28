'use client';

import { initializeApp } from 'firebase/app';
import { getAuth, signInWithCustomToken } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { useState, useEffect } from 'react';

/**
 * Environment-Aware Authentication Component
 * - Development: Clerk authentication only
 * - Production: Clerk + Firebase integration
 */

// Firebase configuration
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

// Check if Firebase integration is enabled
const isFirebaseEnabled = process.env.NEXT_PUBLIC_...=***REMOVED*** 'true';
const isProduction = process.env.NODE_ENV === 'production';

// Initialize Firebase only if enabled
let app: any = null;
let auth: any = null;
let db: any = null;

if (isFirebaseEnabled) {
  try {
    app = initializeApp(firebaseConfig);
    auth = getAuth(app);
    db = getFirestore(app);
  } catch (error) {
    console.error('Firebase initialization error:', error);
  }
}

interface EnvironmentAwareAuthProps {
  children?: React.ReactNode;
}

export function EnvironmentAwareAuth({ children }: EnvironmentAwareAuthProps) {
  const [firebaseSignedIn, setFirebaseSignedIn] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // OSS mode: no Clerk; provide mock auth state
  const userId = 'oss-mode-user';
  const isSignedIn = true;

  useEffect(() => {
    if (isFirebaseEnabled) {
      console.log('Firebase integration is enabled by env, but Clerk is removed in OSS mode. Skipping sign-in.');
    }
  }, []);

  const signIntoFirebase = async () => {
    // In OSS mode, we cannot obtain a Firebase token from Clerk
    setIsLoading(true);
    setError('Firebase integration requires Clerk; disabled in OSS mode');
    setIsLoading(false);
  };

  return (
    <div className="space-y-4">
      {/* Environment Status */}
      <div className="bg-card p-4 rounded-lg border">
        <h3 className="font-semibold mb-2">Authentication Status</h3>
        <div className="space-y-1 text-sm">
          <p><strong>Environment:</strong> {isProduction ? 'Production' : 'Development'}</p>
          <p><strong>Clerk User ID:</strong> {userId}</p>
          <p><strong>Firebase Integration:</strong> {isFirebaseEnabled ? '✅ Enabled' : '❌ Disabled'}</p>
          {isFirebaseEnabled && (
            <>
              <p><strong>Firebase Signed In:</strong> {firebaseSignedIn ? '✅ Yes' : '❌ No'}</p>
              <p><strong>Loading:</strong> {isLoading ? '⏳ Yes' : '✅ No'}</p>
              {error && <p className="text-destructive"><strong>Error:</strong> {error}</p>}
            </>
          )}
        </div>

        {/* Manual Firebase Sign-in (for testing) */}
        {isFirebaseEnabled && !firebaseSignedIn && (
          <button 
            onClick={signIntoFirebase}
            disabled={isLoading}
            className="mt-2 bg-primary text-primary-foreground px-3 py-1 rounded text-sm hover:bg-primary/90 disabled:opacity-50"
          >
            {isLoading ? 'Signing in...' : 'Sign into Firebase'}
          </button>
        )}
      </div>

      {/* Content */}
      {children}
    </div>
  );
}

// Export Firebase instances for use in other components (only if enabled)
export { auth, db, app, isFirebaseEnabled };
