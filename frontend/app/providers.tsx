'use client';

import { type ReactNode } from 'react';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { ToastProvider } from '@/components/providers/toast-provider';
import { ClerkProvider } from '@clerk/nextjs';
import { FirebaseClerkProvider } from '@/components/providers/firebase-clerk-provider';
import { getClerkProviderConfig } from '@/lib/clerk-config';

interface ProvidersProps {
  children: ReactNode;
}

/**
 * Providers component wraps the application with all necessary context providers
 * Simplified configuration for Firebase App Hosting deployment
 */
export function Providers({ children }: ProvidersProps): JSX.Element {
  // Get Clerk configuration
  const clerkConfig = getClerkProviderConfig();

  // Always render ClerkProvider with proper configuration
  return (
    <ClerkProvider {...clerkConfig}>
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
