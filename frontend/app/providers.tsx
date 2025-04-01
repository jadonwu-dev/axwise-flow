'use client';

import { type ReactNode } from 'react';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { ToastProvider } from '@/components/providers/toast-provider';
import { ClerkProvider } from '@clerk/nextjs';

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