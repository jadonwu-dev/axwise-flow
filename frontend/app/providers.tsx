'use client';

import { type ReactNode } from 'react';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { ToastProvider } from '@/components/providers/toast-provider';
import { ClerkProvider } from '@clerk/nextjs';
import { usePathname } from 'next/navigation';
import { apiClient } from '@/lib/apiClient';

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
  const pathname = usePathname();

  // Function to handle after sign in, set auth token for API client
  const handleAfterSignIn = (session: any) => {
    if (session?.token) {
      // Set the auth token in the API client
      apiClient.setAuthToken(session.token);
    }
  };

  // Function to handle authentication change
  const handleAuthChange = ({ userId, token }: { userId: string | null, token: string | null }) => {
    if (token) {
      apiClient.setAuthToken(token);
    }
  };

  return (
    <ClerkProvider
      publishableKey={process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY}
      afterSignInUrl="/unified-dashboard"
      afterSignUpUrl="/unified-dashboard"
      signInUrl="/sign-in"
      signUpUrl="/sign-up"
    >
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
    </ClerkProvider>
  );
}

export default Providers;