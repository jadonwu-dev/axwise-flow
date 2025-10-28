'use client';

import { type ReactNode } from 'react';
import { ThemeProvider } from '@/components/providers/theme-provider';
import { ToastProvider } from '@/components/providers/toast-provider';
import { AuthProvider } from '@/components/providers/auth-provider';
import { UnifiedResearchProvider } from '@/lib/context/unified-research-context';

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps): JSX.Element {
  return (
    <AuthProvider>
      <ThemeProvider
        attribute="class"
        defaultTheme="system"
        enableSystem
        disableTransitionOnChange
      >
        <ToastProvider defaultPosition="top-right" defaultDuration={5000}>
          <UnifiedResearchProvider>
            {children}
          </UnifiedResearchProvider>
        </ToastProvider>
      </ThemeProvider>
    </AuthProvider>
  );
}

export default Providers;
