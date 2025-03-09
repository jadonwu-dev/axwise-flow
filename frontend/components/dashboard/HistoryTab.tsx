'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Loader2, FileText, Calendar, Clock, ChevronRight } from 'lucide-react';
import { DetailedAnalysisResult } from '@/types/api';
import { useToast } from '@/components/providers/toast-provider';
import { apiClient } from '@/lib/apiClient';
import { useRouter } from 'next/navigation';

/**
 * Tab for displaying analysis history
 */
const HistoryTab = () => {
  const router = useRouter();
  const { showToast } = useToast();
  
  // History state
  const [analyses, setAnalyses] = useState<DetailedAnalysisResult[]>([]);
  const [sortBy, setSortBy] = useState<'date' | 'name'>('date');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  const [filterStatus, setFilterStatus] = useState<'all' | 'completed' | 'pending' | 'failed'>('all');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [authToken] = useState<string>('testuser123'); // In future, this will come from auth store
  
  // Fetch analysis history
  useEffect(() => {
    async function fetchAnalyses() {
      try {
        setLoading(true);
        setError(null);
        
        // Set auth token
        apiClient.setAuthToken(authToken);
        
        // Use the API client to fetch real data
        try {
          const apiParams = {
            sortBy: sortBy === 'date' ? 'createdAt' : 'fileName',
            sortDirection: sortDirection,
            status: filterStatus === 'all' ? undefined : filterStatus,
          };
          
          const data = await apiClient.listAnalyses(apiParams);
          setAnalyses(data);
        } catch (apiError) {
          console.error('API error:', apiError);
          setError(apiError instanceof Error ? apiError : new Error('Failed to fetch analyses'));
          showToast('Failed to fetch analysis history', { variant: 'error' });
        }
        
        setLoading(false);
      } catch (err) {
        console.error('Error fetching analyses:', err);
        setError(err instanceof Error ? err : new Error('Failed to fetch analyses'));
        setLoading(false);
        showToast('Failed to load analyses', { variant: 'error' });
      }
    }

    fetchAnalyses();
  }, [showToast, sortBy, sortDirection, filterStatus, authToken]);
  
  // Handle viewing an analysis
  const handleViewAnalysis = (analysisId: string) => {
    router.push(`/unified-dashboard?tab=visualize&analysisId=${analysisId}`);
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
                value={sortBy} 
                onValueChange={(value) => setSortBy(value as 'date' | 'name')}
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
                value={sortDirection} 
                onValueChange={(value) => setSortDirection(value as 'asc' | 'desc')}
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
                value={filterStatus} 
                onValueChange={(value) => setFilterStatus(value as any)}
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
          </div>
          
          {/* Loading state */}
          {loading && (
            <div className="flex justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          )}
          
          {/* Error state */}
          {error && !loading && (
            <div className="p-4 border border-red-200 bg-red-50 text-red-600 rounded-md">
              {error.message}
            </div>
          )}
          
          {/* Empty state */}
          {!loading && !error && analyses.length === 0 && (
            <div className="text-center py-8">
              <FileText className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No analyses found</h3>
              <p className="text-muted-foreground mb-4">
                You haven't performed any analyses yet or none match your current filters.
              </p>
              <Button 
                onClick={() => router.push('/unified-dashboard?tab=upload')}
                variant="outline"
              >
                Start a New Analysis
              </Button>
            </div>
          )}
          
          {/* Analysis list */}
          {!loading && !error && analyses.length > 0 && (
            <div className="space-y-4">
              {analyses.map((analysis) => (
                <div 
                  key={analysis.analysisId} 
                  className="p-4 border rounded-md hover:bg-accent hover:border-accent transition-colors"
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
                      onClick={() => handleViewAnalysis(analysis.analysisId)}
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

export default HistoryTab;
