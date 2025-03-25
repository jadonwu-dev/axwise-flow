'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter, usePathname } from 'next/navigation';
import { FileText, BarChart3, Clock, BookOpen } from 'lucide-react';

/**
 * Client Component for Dashboard Navigation
 * Handles interactive elements and state changes using URL parameters
 */
export default function DashboardNav() {
  const router = useRouter();
  const pathname = usePathname();
  const [isHistory, setIsHistory] = useState(false);
  
  // Keep track of current path for highlighting active tab
  useEffect(() => {
    setIsHistory(pathname?.includes('/history'));
  }, [pathname]);
  
  // Handle tab navigation with clean URL parameters
  const handleTabNavigation = (tab: string) => {
    // Add cache busting to ensure clean state
    const cacheBuster = Date.now();
    router.push(`/unified-dashboard?tab=${tab}&_=${cacheBuster}`);
  };
  
  return (
    <nav className="flex space-x-1 rounded-lg bg-muted p-1">
      {/* Upload Tab */}
      <button 
        onClick={() => handleTabNavigation('upload')}
        className={`flex items-center px-3 py-2 text-sm rounded-md ${!isHistory && !pathname?.includes('visualize') && !pathname?.includes('documentation') ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
      >
        <FileText className="mr-2 h-4 w-4" />
        Upload
      </button>
      
      {/* Visualize Tab */}
      <button 
        onClick={() => handleTabNavigation('visualize')}
        className={`flex items-center px-3 py-2 text-sm rounded-md ${pathname?.includes('visualize') ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
      >
        <BarChart3 className="mr-2 h-4 w-4" />
        Visualize
      </button>
      
      {/* History Tab - Uses Link as it's a page route */}
      <Link 
        href="/unified-dashboard/history"
        className={`flex items-center px-3 py-2 text-sm rounded-md ${isHistory ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
      >
        <Clock className="mr-2 h-4 w-4" />
        History
      </Link>
      
      {/* Documentation Tab */}
      <button 
        onClick={() => handleTabNavigation('documentation')}
        className={`flex items-center px-3 py-2 text-sm rounded-md ${pathname?.includes('documentation') ? 'bg-background shadow-sm' : 'text-muted-foreground hover:text-foreground hover:bg-background/50'}`}
      >
        <BookOpen className="mr-2 h-4 w-4" />
        Documentation
      </button>
    </nav>
  );
} 