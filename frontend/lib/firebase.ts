// Firebase configuration and utilities for DesignThinkingAgentAI
import { initializeApp, getApps, getApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';
import { getAuth } from 'firebase/auth';
import { getFunctions, httpsCallable } from 'firebase/functions';
import { getAnalytics, isSupported } from 'firebase/analytics';

// Firebase configuration
// These values should be replaced with your actual Firebase project configuration
const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
  measurementId: process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID,
};

// Initialize Firebase
const app = getApps().length > 0 ? getApp() : initializeApp(firebaseConfig);
const db = getFirestore(app);
const auth = getAuth(app);
const functions = getFunctions(app);

// Initialize Analytics conditionally (only in browser)
let analytics = null;
if (typeof window !== 'undefined') {
  // Check if analytics is supported in this environment
  isSupported().then(supported => {
    if (supported) {
      analytics = getAnalytics(app);
    }
  });
}

// Security logging function
export const logSecurityEvent = httpsCallable(functions, 'logSecurityEvent');

// Security event types
export const SecurityEventType = {
  // Authentication events
  LOGIN_SUCCESS: 'login_success',
  LOGIN_FAILED: 'login_failed',
  LOGOUT: 'logout',
  PASSWORD_RESET: 'password_reset',
  
  // API events
  API_RATE_LIMIT_EXCEEDED: 'api_rate_limit_exceeded',
  API_UNAUTHORIZED_ACCESS: 'api_unauthorized_access',
  API_INVALID_INPUT: 'api_invalid_input',
  
  // Data events
  DATA_ACCESS: 'data_access',
  DATA_MODIFICATION: 'data_modification',
  SENSITIVE_DATA_ACCESS: 'sensitive_data_access',
  
  // System events
  SYSTEM_ERROR: 'system_error',
  DEPENDENCY_VULNERABILITY: 'dependency_vulnerability',
  CONFIG_CHANGE: 'config_change',
};

/**
 * Log a security event to Firebase
 * 
 * @param eventType The type of security event
 * @param details Event details
 * @returns Promise that resolves when the event is logged
 */
export const logSecurityEventToFirebase = async (eventType: string, details: any) => {
  try {
    await logSecurityEvent({
      eventType,
      details,
    });
    return true;
  } catch (error) {
    console.error('Error logging security event:', error);
    return false;
  }
};

/**
 * Log an authentication event
 * 
 * @param eventType Auth event type
 * @param details Event details
 * @returns Promise that resolves when the event is logged
 */
export const logAuthEvent = async (eventType: string, details: any) => {
  return logSecurityEventToFirebase(eventType, {
    ...details,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
  });
};

/**
 * Log an API error event
 * 
 * @param endpoint API endpoint
 * @param error Error object or message
 * @param statusCode HTTP status code if available
 * @returns Promise that resolves when the event is logged
 */
export const logApiError = async (endpoint: string, error: any, statusCode?: number) => {
  return logSecurityEventToFirebase(SecurityEventType.API_UNAUTHORIZED_ACCESS, {
    endpoint,
    error: error instanceof Error ? error.message : String(error),
    statusCode,
    timestamp: new Date().toISOString(),
    userAgent: navigator.userAgent,
  });
};

export { app, db, auth, analytics };
