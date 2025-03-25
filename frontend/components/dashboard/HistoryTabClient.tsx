'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, FileText, Calendar, Clock, ChevronRight } from 'lucide-react';
import { DetailedAnalysisResult } from '@/types/api';
import { useToast } from '@/components/providers/toast-provider';
import { useAnalysisStore } from '@/store/useAnalysisStore';

/**
 * Props interface for HistoryTabClient
 */
interface HistoryTabClientProps {
  initialAnalyses: DetailedAnalysisResult[];
  sortBy: 'date' | 'name';
  sortDirection: 'asc' | 'desc';
  filterStatus: 'all' | 'completed' | 'pending' | 'failed';
}

/**
 * Client component for displaying analysis history 
 */
const HistoryTabClient = ({ 
  initialAnalyses,
  sortBy: initialSortBy,
  sortDirection: initialSortDirection, 
  filterStatus: initialFilterStatus
}: HistoryTabClientProps) => {
  const router = useRouter();
  const { showToast } = useToast();
  
  // History state
  const [analyses] = useState<DetailedAnalysisResult[]>(initialAnalyses);
  const [loading, setLoading] = useState(false);
  
  // Temporary: Update Zustand store with initial analyses for compatibility
  useState(() => {
    if (initialAnalyses.length > 0) {
      useAnalysisStore.setState({
        analysisHistory: initialAnalyses,
        isLoadingHistory: false,
        historyError: null
      });
    }
  });
  
  // Handle URL parameter updates
  const updateUrlParams = (param: string, value: string) => {
    // Update the URL parameters to trigger a server refetch
    router.push(`/unified-dashboard/history?${param}=${value}`);
  };
  
  // Handle manual refresh
  const handleRefresh = () => {
    setLoading(true);
    router.refresh();
    setTimeout(() => setLoading(false), 500); // Just for UI feedback
  };
  
  // Handle viewing an analysis
  const handleViewAnalysis = (id: string) => {
    try {
      // Reset store state with only valid properties from AnalysisState
      useAnalysisStore.setState({
        currentAnalysis: null,
        isLoadingAnalysis: true
      });
      
      // Add cache-busting parameter to ensure a fresh fetch
      const cacheBuster = Date.now();
      
      // Navigate to visualization tab with the analysis ID and cache buster
      router.push(`/unified-dashboard/visualize?analysisId=${id}&_=${cacheBuster}`);
      
      // Also update the Zustand store for backward compatibility
      const analysisStore = useAnalysisStore.getState();
      analysisStore.fetchAnalysisById(id);
      
      console.log('Navigating to analysis:', id, 'with cache buster:', cacheBuster);
    } catch (error) {
      console.error('Error navigating to analysis:', error);
      showToast('Error loading analysis. Please try again.', { variant: 'error' });
    }
  };
  
  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };
  
  // Format time for display
  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString();
  };
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Analysis History</CardTitle>
        <CardDescription>
          View and manage your previous analyses
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Filters */}
          <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4">
            <div className="flex-1">
              <label className="text-sm font-medium mb-1 block">Sort By</label>
              <Select 
                value={initialSortBy} 
                onValueChange={(value) => updateUrlParams('sortBy', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="date">Date</SelectItem>
                  <SelectItem value="name">File Name</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex-1">
              <label className="text-sm font-medium mb-1 block">Direction</label>
              <Select 
                value={initialSortDirection} 
                onValueChange={(value) => updateUrlParams('sortDirection', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="asc">Ascending</SelectItem>
                  <SelectItem value="desc">Descending</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="flex-1">
              <label className="text-sm font-medium mb-1 block">Status</label>
              <Select 
                value={initialFilterStatus} 
                onValueChange={(value) => updateUrlParams('status', value)}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All</SelectItem>
                  <SelectItem value="completed">Completed</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="failed">Failed</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-end">
              <Button variant="outline" onClick={handleRefresh} disabled={loading}>
                {loading ? 'Refreshing...' : 'Refresh'}
              </Button>
            </div>
          </div>
          
          {/* Loading state */}
          {loading && (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}
          
          {/* Empty state */}
          {!loading && analyses.length === 0 && (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No analyses found</h3>
              <p className="text-muted-foreground mb-4">
                You haven't performed any analyses yet or none match your current filters.
              </p>
              <Button 
                onClick={() => {
                  // Reset only valid store properties
                  useAnalysisStore.setState({
                    currentAnalysis: null,
                    isLoadingAnalysis: false
                  });
                  
                  // Add cache busting to ensure clean state
                  const cacheBuster = Date.now();
                  router.push(`/unified-dashboard/upload?_=${cacheBuster}`);
                }}
                variant="outline"
              >
                Start a New Analysis
              </Button>
            </div>
          )}
          
          {/* Analysis list */}
          {!loading && analyses.length > 0 && (
            <div className="space-y-4">
              {analyses.map((analysis) => (
                <div 
                  key={analysis.id} 
                  className="p-4 border rounded-md hover:bg-accent hover:border-accent transition-colors cursor-pointer"
                  onClick={() => handleViewAnalysis(analysis.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{analysis.fileName || 'Unnamed Analysis'}</h3>
                      <div className="flex items-center text-sm text-muted-foreground mt-1">
                        <Calendar className="h-4 w-4 mr-1" />
                        {analysis.createdAt && formatDate(analysis.createdAt)}
                        <Clock className="h-4 w-4 ml-3 mr-1" />
                        {analysis.createdAt && formatTime(analysis.createdAt)}
                      </div>
                    </div>
                    <Button 
                      variant="ghost" 
                      size="sm" 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleViewAnalysis(analysis.id);
                      }}
                    >
                      View <ChevronRight className="h-4 w-4 ml-1" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default HistoryTabClient; 