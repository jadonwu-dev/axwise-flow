import React from 'react';
import Link from 'next/link';
import { FileText, BarChart3, Clock, BookOpen } from 'lucide-react';
import { headers } from 'next/headers';

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
  // Get the current pathname to highlight active tab
  const headersList = headers();
  const pathname = headersList.get('x-pathname') || '';
  const isHistory = pathname.includes('/history');
  
  return (
    <div className="container mx-auto py-6 space-y-8">
      {/* Consistent Navigation Header */}
      <div className="flex justify-between items-center border-b pb-4">
        <h1 className="text-2xl font-bold">Interview Analysis</h1>
        
        {/* Tab Navigation */}
        <nav className="flex space-x-1 rounded-lg bg-muted p-1">
          <Link 
            href="/unified-dashboard?tab=upload"
            className={`flex items-center px-3 py-2 text-sm rounded-md ${!isHistory && !pathname.includes('visualize') && !pathname.includes('documentation') ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
          >
            <FileText className="mr-2 h-4 w-4" />
            Upload
          </Link>
          
          <Link 
            href="/unified-dashboard?tab=visualize"
            className={`flex items-center px-3 py-2 text-sm rounded-md ${pathname.includes('visualize') ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
          >
            <BarChart3 className="mr-2 h-4 w-4" />
            Visualize
          </Link>
          
          <Link 
            href="/unified-dashboard/history"
            className={`flex items-center px-3 py-2 text-sm rounded-md ${isHistory ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
          >
            <Clock className="mr-2 h-4 w-4" />
            History
          </Link>
          
          <Link 
            href="/unified-dashboard?tab=documentation"
            className={`flex items-center px-3 py-2 text-sm rounded-md ${pathname.includes('documentation') ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
          >
            <BookOpen className="mr-2 h-4 w-4" />
            Documentation
          </Link>
        </nav>
      </div>
      
      {/* Page Content */}
      {children}
    </div>
  );
} 