'use client';

/**
 * Simplified Clerk configuration for Firebase App Hosting
 * This file provides basic utilities for Clerk authentication
 */

// Check if Clerk is configured
export const isClerkConfigured =
  typeof process.env.NEXT_PUBLIC_CLERK_...=***REMOVED*** 'string' &&
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY !== '' &&
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY !== 'your_clerk_publishable_key_here';

/**
 * Get Clerk configuration for the ClerkProvider component
 * Simplified configuration for Firebase App Hosting
 */
export function getClerkProviderConfig() {
  return {
    publishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY!,
    appearance: {
      baseTheme: undefined, // Use system theme
      variables: {
        colorPrimary: 'hsl(var(--primary))',
        colorText: 'hsl(var(--foreground))',
        colorBackground: 'hsl(var(--background))',
        colorDanger: 'hsl(var(--destructive))',
        fontFamily: 'var(--font-sans)',
        borderRadius: 'var(--radius)'
      }
    }
  };
}
