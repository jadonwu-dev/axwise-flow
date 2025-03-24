import { Suspense } from 'react';
import HistoryTab from '@/components/dashboard/HistoryTab';
import { DetailedAnalysisResult } from '@/types/api';
import { Card } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import { serverApiClient } from '@/lib/serverApiClient';

// Force dynamic rendering to prevent static generation errors
export const dynamic = 'force-dynamic';

/**
 * Server component to fetch analyses data using the server-safe API client
 */
async function fetchAnalyses(): Promise<DetailedAnalysisResult[]> {
  try {
    // Use the server-safe API client instead of the browser-based one
    const data = await serverApiClient.listAnalyses({
      sortBy: 'createdAt',
      sortDirection: 'desc',
      status: undefined // Use undefined to get all statuses
    });
    
    return data;
  } catch (error) {
    console.error('Failed to fetch analyses on server:', error);
    return [];
  }
}

/**
 * Loading skeleton for history items
 */
function HistorySkeleton() {
  return (
    <Card className="w-full p-4">
      <div className="flex justify-center py-8">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <span className="ml-2">Loading analyses...</span>
      </div>
      <div className="space-y-4 mt-4">
        {[...Array(5)].map((_, i) => (
          <div key={i} className="h-16 bg-muted/50 animate-pulse rounded-lg" />
        ))}
      </div>
    </Card>
  );
}

/**
 * History page server component
 * Fetches analyses data and passes it to the client component
 */
export default async function HistoryPage() {
  const analyses = await fetchAnalyses();
  
  return (
    <div className="w-full max-w-5xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Analysis History</h1>
      <p className="text-muted-foreground mb-6">
        View and manage your previous analyses
      </p>
      
      <Suspense fallback={<HistorySkeleton />}>
        <HistoryTab initialAnalyses={analyses} />
      </Suspense>
    </div>
  );
} 