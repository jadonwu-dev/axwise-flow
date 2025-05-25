'use client';

import { useAuth, useUser } from '@clerk/nextjs';
import { SignInButton, SignOutButton, SignUpButton } from '@clerk/nextjs';

/**
 * Simple test page to verify Clerk authentication is working
 * This page tests Clerk hooks directly without Firebase integration
 */
export default function TestClerkPage() {
  const { isSignedIn, userId, isLoaded } = useAuth();
  const { user } = useUser();

  if (!isLoaded) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4"></div>
          <p>Loading Clerk...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Clerk Authentication Test</h1>
        
        <div className="bg-card p-6 rounded-lg border mb-6">
          <h2 className="text-xl font-semibold mb-4">Authentication Status</h2>
          <div className="space-y-2">
            <p><strong>Is Loaded:</strong> {isLoaded ? '✅ Yes' : '❌ No'}</p>
            <p><strong>Is Signed In:</strong> {isSignedIn ? '✅ Yes' : '❌ No'}</p>
            <p><strong>User ID:</strong> {userId || 'Not available'}</p>
            <p><strong>Email:</strong> {user?.emailAddresses?.[0]?.emailAddress || 'Not available'}</p>
            <p><strong>First Name:</strong> {user?.firstName || 'Not available'}</p>
            <p><strong>Last Name:</strong> {user?.lastName || 'Not available'}</p>
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border mb-6">
          <h2 className="text-xl font-semibold mb-4">Authentication Actions</h2>
          <div className="space-x-4">
            {!isSignedIn ? (
              <>
                <SignInButton mode="modal">
                  <button className="bg-primary text-primary-foreground px-4 py-2 rounded hover:bg-primary/90">
                    Sign In
                  </button>
                </SignInButton>
                <SignUpButton mode="modal">
                  <button className="bg-secondary text-secondary-foreground px-4 py-2 rounded hover:bg-secondary/90">
                    Sign Up
                  </button>
                </SignUpButton>
              </>
            ) : (
              <SignOutButton>
                <button className="bg-destructive text-destructive-foreground px-4 py-2 rounded hover:bg-destructive/90">
                  Sign Out
                </button>
              </SignOutButton>
            )}
          </div>
        </div>

        <div className="bg-card p-6 rounded-lg border">
          <h2 className="text-xl font-semibold mb-4">Environment Information</h2>
          <div className="space-y-2 text-sm">
            <p><strong>Environment:</strong> {process.env.NODE_ENV}</p>
            <p><strong>Clerk Domain:</strong> {process.env.NEXT_PUBLIC_CLERK_DOMAIN}</p>
            <p><strong>Publishable Key:</strong> {process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY?.substring(0, 20)}...</p>
          </div>
        </div>

        <div className="mt-6 text-center">
          <a 
            href="/sign-in" 
            className="text-primary hover:underline mr-4"
          >
            Go to Sign In Page
          </a>
          <a 
            href="/unified-dashboard" 
            className="text-primary hover:underline"
          >
            Go to Dashboard
          </a>
        </div>
      </div>
    </div>
  );
}
