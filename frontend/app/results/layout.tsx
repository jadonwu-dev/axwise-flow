'use client';

import { ReactNode } from 'react';
import { ToastProvider } from '@/components/providers/toast-provider';

interface ResultsLayoutProps {
  children: ReactNode;
}

/**
 * Layout for the results section
 * Provides the ToastProvider context for all results pages
 */
export default function ResultsLayout({ children }: ResultsLayoutProps): JSX.Element {
  return (
    <ToastProvider defaultPosition="top-right" defaultDuration={5000}>
      {children}
    </ToastProvider>
  );
}