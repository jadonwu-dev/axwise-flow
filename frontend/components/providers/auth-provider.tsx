'use client';

import React, { createContext, useContext, ReactNode } from 'react';
import { useUser, useAuth } from '@clerk/nextjs';

/**
 * Authentication context that provides Clerk auth state
 */
interface AuthContextType {
  // Clerk auth state
  isClerkSignedIn: boolean | undefined;
  clerkUserId: string | null | undefined;
  isClerkLoaded: boolean;
  isFullyAuthenticated: boolean | undefined;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication Provider that manages Clerk authentication
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const { isSignedIn, userId, isLoaded } = useAuth();

  const authState: AuthContextType = {
    isClerkSignedIn: isSignedIn,
    clerkUserId: userId,
    isClerkLoaded: isLoaded,
    isFullyAuthenticated: isSignedIn,
  };

  return (
    <AuthContext.Provider value={authState}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Hook to use the authentication context
 * Provides access to Clerk auth state
 */
export function useAuthContext() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
}

/**
 * Authentication Status Component
 * Shows the current authentication state with color-coded feedback
 * Only visible to admin users
 */
export function AuthStatus() {
  const { isClerkSignedIn, isFullyAuthenticated } = useAuthContext();
  const { user } = useUser();

  // Only show to admin users
  const isAdmin = user?.primaryEmailAddress?.emailAddress === 'vitalijs@axwise.de';

  if (!isClerkSignedIn || !isAdmin) {
    return null; // Don't show status if not signed in or not admin
  }

  return (
    <div className="fixed bottom-4 right-4 bg-card border rounded-lg p-3 shadow-lg max-w-sm z-50">
      <div className="text-xs space-y-1">
        <div className="font-semibold">Auth Status (Admin)</div>
        <div className="flex items-center gap-2">
          <span>Clerk:</span>
          <span className={isClerkSignedIn ? 'text-green-600' : 'text-red-600'}>
            {isClerkSignedIn ? '✅' : '🔴'}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <span>Ready:</span>
          <span className={isFullyAuthenticated ? 'text-green-600' : 'text-red-600'}>
            {isFullyAuthenticated ? '✅' : '🔴'}
          </span>
        </div>
      </div>
    </div>
  );
}
