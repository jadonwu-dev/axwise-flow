'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@clerk/nextjs';
import DashboardTabs from './DashboardTabs';
import { DashboardData } from '@/types/api';
import { apiClient } from '@/lib/apiClient';
import { useToast } from '@/components/providers/toast-provider';
import { useAnalysisStore, useCurrentDashboardData } from '@/store/useAnalysisStore';

/**
 * Main container component for the unified dashboard
 * This component handles:
 * - Authentication checking
 * - Loading analysis data when needed
 * - Error handling
 */
const UnifiedDashboardContainer = () => {
  const { userId, isLoaded } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { showToast } = useToast();
  const { fetchAnalysisById, setCurrentAnalysis } = useAnalysisStore();
  const { dashboardData, isLoading, error: dashboardError } = useCurrentDashboardData();
  const [error, setError] = useState<string | null>(null);
  const [authToken, setAuthToken] = useState<string>('testuser123'); // To be replaced with real auth
  
  // Handle authentication redirection
  useEffect(() => {
    if (isLoaded && !userId) {
      router.push('/sign-in');
    }
  }, [isLoaded, userId, router]);
  
  // Handle loading analysis results from URL
  useEffect(() => {
    const analysisId = searchParams.get('analysisId');
    const tab = searchParams.get('tab');
    
    // Only fetch analysis if we're on the visualize tab and have an analysisId
    if (analysisId && tab === 'visualize') {
      const fetchAnalysis = async () => {
        try {
          setError(null);
          
          // Set auth token
          apiClient.setAuthToken(authToken);
          
          // Fetch analysis using the store
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
  }, [searchParams, showToast, authToken, fetchAnalysisById]);
  
  // Set error from dashboard if available
  useEffect(() => {
    if (dashboardError) {
      setError(dashboardError.message);
    }
  }, [dashboardError]);
  
  // If still loading auth, show minimal loading UI
  if (!isLoaded) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }
  
  // Show error state if we have an error
  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="p-6 border border-red-200 bg-red-50 text-red-600 rounded-md">
          <h2 className="text-xl font-semibold mb-2">Error</h2>
          <p>{error}</p>
          <button 
            onClick={() => router.push('/unified-dashboard')}
            className="mt-4 px-4 py-2 bg-red-100 hover:bg-red-200 text-red-700 rounded-md transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Interview Analysis Dashboard</h1>
      
      <DashboardTabs dashboardData={dashboardData} />
      
      {isLoading && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-center">Loading analysis data...</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default UnifiedDashboardContainer;
