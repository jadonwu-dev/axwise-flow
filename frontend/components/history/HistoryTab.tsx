import { Suspense } from 'react';
import HistoryTabClient from './HistoryTabClient';
// Removed incorrect import: import { fetchAnalysisHistory } from '@/app/actions';
import { serverApiClient } from '@/lib/serverApiClient'; // Import serverApiClient
import { ListAnalysesParams, DetailedAnalysisResult } from '@/types/api'; // Import ListAnalysesParams and DetailedAnalysisResult

// Removed unused AnalysisHistory interface

// This is a Server Component so it doesn't use 'use client'
interface HistoryTabProps { // Define props interface
  searchParams: { 
    page?: string;
    // Add other potential searchParams used for sorting/filtering if needed by serverApiClient
    sortBy?: 'createdAt' | 'fileName'; 
    sortDirection?: 'asc' | 'desc';
    status?: 'all' | 'completed' | 'pending' | 'failed';
  };
}

export default async function HistoryTab({
 searchParams
 }: HistoryTabProps): Promise<JSX.Element> { // Add return type and use interface
  // Parse current page from URL or default to 1
  const currentPage = searchParams.page ? parseInt(searchParams.page, 10) : 1;
  const pageSize = 5; // Number of items per page

  // Prepare params for API call based on searchParams
  const apiParams: ListAnalysesParams = {
    limit: pageSize,
    offset: (currentPage - 1) * pageSize,
    sortBy: searchParams.sortBy || 'createdAt', // Default sort
    sortDirection: searchParams.sortDirection || 'desc', // Default direction
    status: searchParams.status === 'all' ? undefined : searchParams.status, // Handle 'all' status
  };
  
  let analyses: DetailedAnalysisResult[] = [];
  let totalItems = 0;

  try {
    // Fetch data server-side using serverApiClient
    // Assuming listAnalyses returns an object like { items: DetailedAnalysisResult[], totalItems: number }
    // Adjust based on actual return type of serverApiClient.listAnalyses
    const result = await serverApiClient.listAnalyses(apiParams); 
    analyses = result || []; // Use result directly if it's the array, or result.items if nested
    // Assuming the API returns total count for pagination. Replace 0 if needed.
    // totalItems = result.totalItems || 0; 
  } catch (error) {
      console.error("Failed to fetch analysis history:", error);
      // Handle error appropriately, maybe pass an error state to client
  }
  
  const totalPages = Math.ceil(totalItems / pageSize);
  
  return (
    <Suspense fallback={<div>Loading history...</div>}>
      {/* Pass necessary props to HistoryTabClient */}
      <HistoryTabClient 
        historyItems={analyses} // Pass fetched items
        totalPages={totalPages}
        currentPage={currentPage}
        // Removed initial sort/filter props as client fetches its own state
      />
    </Suspense>
  );
}