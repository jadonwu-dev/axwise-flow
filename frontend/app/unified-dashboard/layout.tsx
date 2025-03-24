import React from 'react';
import { headers } from 'next/headers';
import DashboardNav from './navigation';

/**
 * Unified Dashboard Layout
 * 
 * This layout provides consistent navigation between all dashboard pages
 * including the history page.
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="container mx-auto py-6 space-y-8">
      {/* Consistent Navigation Header */}
      <div className="flex justify-between items-center border-b pb-4">
        <h1 className="text-2xl font-bold">Interview Analysis</h1>
        
        {/* Use client component for interactive navigation */}
        <DashboardNav />
      </div>
      
      {/* Page Content */}
      {children}
    </div>
  );
} 