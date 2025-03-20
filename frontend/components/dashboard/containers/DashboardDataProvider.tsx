'use client';

import { useState, useEffect, createContext, ReactNode, useRef, useMemo } from 'react';
import { useSearchParams } from 'next/navigation';
import { apiClient } from '@/lib/apiClient';
import { useToast } from '@/components/providers/toast-provider';
import { useAnalysisStore, useCurrentDashboardData } from '@/store/useAnalysisStore';
import { DashboardData } from '@/types/api';

interface DataContextType {
  dashboardData: DashboardData | null;
  isLoading: boolean;
  error: string | null;
}

export const DashboardDataContext = createContext<DataContextType>({
  dashboardData: null,
  isLoading: false,
  error: null
});

interface DashboardDataProviderProps {
  children: ReactNode;
}

export const DashboardDataProvider = ({ children }: DashboardDataProviderProps) => {
  const searchParams = useSearchParams();
  const { showToast } = useToast();
  const { fetchAnalysisById } = useAnalysisStore();
  const { dashboardData, isLoading, error: dashboardError } = useCurrentDashboardData();
  const [error, setError] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string>('testuser123'); // To be replaced with real auth
  
  // Use a ref to track if we've already fetched the analysis to prevent infinite fetches
  const hasAttemptedFetch = useRef(false);
  
  // Handle loading analysis results from URL - memoize analysisId and tab
  const analysisId = useMemo(() => searchParams.get('analysisId'), [searchParams]);
  const tab = useMemo(() => searchParams.get('tab'), [searchParams]);
  
  // Handle loading analysis results from URL
  useEffect(() => {
    // Only fetch if we haven't attempted a fetch yet, and we have an analysisId and tab=visualize
    if (!hasAttemptedFetch.current && analysisId && tab === 'visualize') {
      hasAttemptedFetch.current = true;
      
      const fetchAnalysis = async () => {
        try {
          setError(null);
          apiClient.setAuthToken(authToken);
          const result = await fetchAnalysisById(analysisId, true);
          if (!result) {
            throw new Error('Failed to fetch analysis');
          }
        } catch (err) {
          console.error('Error fetching analysis:', err);
          setError(`Failed to load analysis: ${err instanceof Error ? err.message : String(err)}`);
          showToast(`Failed to load analysis: ${err instanceof Error ? err.message : String(err)}`, { variant: 'error' });
        }
      };
      
      fetchAnalysis();
    }
  }, [analysisId, tab, authToken, fetchAnalysisById, showToast]);
  
  // Reset fetch attempt flag if analysisId changes
  useEffect(() => {
    if (analysisId) {
      hasAttemptedFetch.current = false;
    }
  }, [analysisId]);
  
  // Set error from dashboard if available - only when dashboardError changes
  useEffect(() => {
    if (dashboardError) {
      setError(dashboardError.message);
    }
  }, [dashboardError]);
  
  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    dashboardData, 
    isLoading, 
    error
  }), [dashboardData, isLoading, error]);
  
  return (
    <DashboardDataContext.Provider value={contextValue}>
      {children}
    </DashboardDataContext.Provider>
  );
}; 