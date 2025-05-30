'use client';

import {
  UserButton,
  useUser,
  SignedIn,
  SignedOut,
  useSession
} from '@clerk/nextjs';
import { Button } from '@/components/ui/button';
import { useEffect } from 'react';
import { apiClient } from '@/lib/apiClient';
import { isClerkConfigured } from '@/lib/clerk-config';
import { SubscriptionStatus } from '@/components/subscription-status';
import Link from 'next/link';

// Component that uses Clerk hooks - only rendered when Clerk is available
function ClerkUserProfile(): JSX.Element {
  const { isSignedIn, user, isLoaded } = useUser();
  const { session } = useSession();

  console.log('ClerkUserProfile - isLoaded:', isLoaded, 'isSignedIn:', isSignedIn);

  // Set or clear the auth token based on sign-in status
  useEffect(() => {
    const manageAuthToken = async (): Promise<void> => {
      if (isSignedIn && isLoaded && session) {
        try {
          const token = await session.getToken();
          if (token) {
            console.log('Auth token set');
            // Debug: Decode the token to see the user ID
            try {
              const payload = JSON.parse(atob(token.split('.')[1]));
              console.log('🔍 Clerk token payload:', {
                sub: payload.sub,
                email: payload.email,
                exp: new Date(payload.exp * 1000).toISOString()
              });
            } catch (e) {
              console.log('Could not decode token for debugging');
            }
            // Set token in API client headers
            apiClient.setAuthToken(token);
            // Also store in localStorage for analysis functions
            if (typeof window !== 'undefined') {
              localStorage.setItem('auth_token', token);
              // Also set in cookie for server-side access
              document.cookie = `auth_token=${token}; path=/; max-age=3600; SameSite=Lax`;
            }
          }
        } catch (error) {
          console.error('Error getting token:', error);
        }
      } else if (isLoaded && !isSignedIn) {
        // Clear auth token when user is signed out
        console.log('Auth token cleared');
        apiClient.clearAuthToken();
        // Also clear from localStorage and cookie
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
          // Clear the cookie by setting it to expire in the past
          document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
        }
      }
    };

    manageAuthToken();
  }, [isSignedIn, isLoaded, session]);

  // Show loading state while Clerk is initializing
  if (!isLoaded) {
    return (
      <div className="flex items-center gap-4">
        <Link href="/sign-in">
          <Button variant="outline" size="sm">
            Sign In
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-4">
      <SignedIn>
        {user && (
          <div className="flex items-center gap-4">
            <SubscriptionStatus />
            <div className="flex items-center gap-2">
              <span className="text-sm hidden md:block">
                {user.firstName || user.username || 'User'}
              </span>
              <UserButton
                appearance={{
                  elements: {
                    userButtonAvatarBox: 'w-8 h-8',
                  }
                }}
              />
            </div>
          </div>
        )}
      </SignedIn>
      <SignedOut>
        <Link href="/sign-in">
          <Button variant="outline" size="sm">
            Sign In
          </Button>
        </Link>
      </SignedOut>
    </div>
  );
}

// Main UserProfile component that conditionally renders based on Clerk configuration
export function UserProfile(): JSX.Element {
  const clerkConfigured = isClerkConfigured();
  console.log('UserProfile rendering - Clerk configured:', clerkConfigured);

  // Development mode fallback when Clerk is not configured
  if (!clerkConfigured) {
    console.log('Rendering dev mode UserProfile');
    return (
      <div className="flex items-center gap-4">
        <SubscriptionStatus />
        <div className="flex items-center gap-2">
          <span className="text-sm text-yellow-600 dark:text-yellow-400">
            Dev Mode
          </span>
          <Link href="/sign-in">
            <Button variant="outline" size="sm">
              Sign In
            </Button>
          </Link>
        </div>
      </div>
    );
  }

  // Render Clerk-enabled component when Clerk is configured
  console.log('Rendering Clerk UserProfile');
  return <ClerkUserProfile />;
}
