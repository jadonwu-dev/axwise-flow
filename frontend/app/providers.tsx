'use client';

import { type ReactNode } from 'react';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { ToastProvider } from '@/components/providers/toast-provider';
import { ClerkProvider } from '@clerk/nextjs';
import { FirebaseClerkProvider } from '@/components/providers/firebase-clerk-provider';
import { isClerkConfigured, getClerkProviderConfig } from '@/lib/clerk-config';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Providers component wraps the application with all necessary context providers
 * This ensures consistent access to theme, toast notifications, and other app-wide
 * functionality throughout the component tree.
 *
 */
export function Providers({ children }: ProvidersProps): JSX.Element {
  // If Clerk is not configured, render without ClerkProvider
  if (!isClerkConfigured) {
    console.warn('Clerk authentication is not configured. Running in development mode without authentication.');
    return (
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <ToastProvider defaultPosition="top-right" defaultDuration={5000}>
          {children}
        </ToastProvider>
      </ThemeProvider>
    );
  }

  // Get Clerk configuration
  const clerkConfig = getClerkProviderConfig();

  // If Clerk is configured, use ClerkProvider with FirebaseClerkProvider
  return (
    <ClerkProvider
      {...clerkConfig}
    >
      <FirebaseClerkProvider>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <ToastProvider defaultPosition="top-right" defaultDuration={5000}>
            {children}
          </ToastProvider>
        </ThemeProvider>
      </FirebaseClerkProvider>
    </ClerkProvider>
  );
}

export default Providers;
