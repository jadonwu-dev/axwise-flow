/**
 * Authentication-related methods for the API client
 */

import { apiCore } from './core';

/**
 * Get an authentication token from Clerk if available
 */
export async function getAuthToken(): Promise<string | null> {
  try {
    // In development mode, return a development token
    if (process.env.NODE_ENV === 'development' || typeof window === 'undefined') {
      console.log('Using development token for authentication');
      return 'DEV_TOKEN_REDACTED';
    }

    // This assumes Clerk is loaded and available in the global window object
    if (window.Clerk?.session) {
      return await window.Clerk.session.getToken();
    }

    // Fallback to development token if Clerk is not available
    console.log('Clerk not available, using development token');
    return 'DEV_TOKEN_REDACTED';
  } catch (error) {
    console.error('Error getting auth token:', error);
    // Fallback to development token on error
    return 'DEV_TOKEN_REDACTED';
  }
}

/**
 * Set the authentication token for API requests
 */
export function setAuthToken(token: string): void {
  apiCore.setHeader('Authorization', `Bearer ${token}`);
  console.log('Auth token set');
}

/**
 * Initialize authentication by getting and setting the auth token
 */
export async function initializeAuth(): Promise<void> {
  try {
    const token = await getAuthToken();
    if (token) {
      setAuthToken(token);
    }
  } catch (error) {
    console.error('Error initializing authentication:', error);
  }
}
