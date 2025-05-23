'use client';

/**
 * Clerk configuration for static site generation
 * This file provides utilities to handle Clerk authentication during static site generation
 */

// Check if we're in a browser environment
export const isBrowser = typeof window !== 'undefined';

// Check if we're in a static site generation environment
export const isSSG = 
  !isBrowser || 
  (process.env.NODE_ENV === 'production' && 
   typeof navigator !== 'undefined' && 
   navigator.userAgent.includes('Firebase'));

// Check if Clerk is configured
export const isClerkConfigured = 
  typeof process.env.NEXT_PUBLIC_CLERK_...=***REMOVED*** 'string' && 
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY !== '' &&
  process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY !== 'your_clerk_publishable_key_here';

/**
 * Get Clerk configuration for the ClerkProvider component
 * This function returns a configuration object that works during static site generation
 */
export function getClerkProviderConfig() {
  return {
    publishableKey: process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY,
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

/**
 * Create a safe auth hook for use during static site generation
 * This function returns a mock auth hook when in SSG mode
 * @param useAuthHook The real useAuth hook from Clerk
 * @returns A safe auth hook that works during static site generation
 */
export function createSafeAuthHook(useAuthHook: any) {
  return function useSafeAuth() {
    // If we're in SSG mode, return a mock auth hook
    if (isSSG) {
      return {
        isSignedIn: false,
        userId: null,
        getToken: async () => null,
        isLoaded: true,
        isLoading: false
      };
    }

    // Otherwise, use the real auth hook
    try {
      return useAuthHook();
    } catch (error) {
      console.error('Error using Clerk auth hook:', error);
      // Return a mock auth hook if there's an error
      return {
        isSignedIn: false,
        userId: null,
        getToken: async () => null,
        isLoaded: true,
        isLoading: false
      };
    }
  };
}
