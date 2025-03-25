// Server component for fetching history data
import { serverApiClient } from '@/lib/serverApiClient';
import HistoryTabClient from './HistoryTabClient';
import { ListAnalysesParams } from '@/types/api';

interface HistoryTabProps {
  searchParams?: { 
    sortBy?: 'date' | 'name',
    sortDirection?: 'asc' | 'desc',
    status?: 'all' | 'completed' | 'pending' | 'failed'
  }
}

export default async function HistoryTab({ searchParams }: HistoryTabProps) {
  // Default sorting and filtering parameters
  const sortBy = searchParams?.sortBy || 'date';
  const sortDirection = searchParams?.sortDirection || 'desc';
  const filterStatus = searchParams?.status || 'all';
  
  // Convert to API params format
  const apiParams: ListAnalysesParams = {
    sortBy: sortBy === 'date' ? 'createdAt' : 'fileName',
    sortDirection: sortDirection,
    status: filterStatus === 'all' ? undefined : filterStatus,
  };
  
  // Fetch analyses using serverApiClient
  const analyses = await serverApiClient.listAnalyses(apiParams);
  
  return (
    <HistoryTabClient 
      initialAnalyses={analyses}
      sortBy={sortBy}
      sortDirection={sortDirection}
      filterStatus={filterStatus}
    />
  );
}
