// frontend/components/visualization/PriorityInsights.tsx
'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { PrioritizedInsight, PriorityInsightsResponse } from '@/types/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/lib/apiClient';
import { AlertCircle, AlertTriangle, CheckCircle, RefreshCw, WifiOff } from 'lucide-react';
import { useToast } from '@/components/ui/use-toast';
import { Skeleton } from '@/components/ui/skeleton'; // Assuming this now exists via shadcn
import { Button } from '@/components/ui/button';

// Error types for more semantic error handling
type ErrorType = 'auth' | 'network' | 'server' | 'notFound' | 'parsing' | 'unknown';

// Enhanced type definitions (Keep these)
interface PatternOriginal {
  name?: string;
  description?: string;
  sentiment?: number;
  frequency?: number;
  category?: string;
  evidence?: string[];
  [key: string]: any; // Allow for additional properties
}
interface ThemeOriginal {
  name?: string;
  definition?: string;
  sentiment?: number;
  frequency?: number;
  examples?: string[];
  [key: string]: any; // Allow for additional properties
}
type PrioritizedInsightWithOriginal = PrioritizedInsight & { original: ThemeOriginal | PatternOriginal };
interface ErrorState {
  message: string;
  type: ErrorType;
  retryable: boolean;
  statusCode?: number;
}

// Utility function to categorize errors (Keep this)
const categorizeError = (err: any): ErrorState => {
  if (err.response) {
    const statusCode = err.response.status;
    if (statusCode === 401 || statusCode === 403) {
      return { message: 'Authentication error. Please ensure you are logged in.', type: 'auth', retryable: false, statusCode };
    } else if (statusCode === 404) {
      return { message: 'Analysis data not found or not completed yet.', type: 'notFound', retryable: true, statusCode };
    } else if (statusCode >= 500) {
      return { message: 'Server error occurred while calculating priorities.', type: 'server', retryable: true, statusCode };
    } else if (err.response.data?.detail) {
      return { message: err.response.data.detail, type: 'unknown', retryable: true, statusCode };
    }
  } else if (err.request) {
    return { message: 'Network error. Please check your connection.', type: 'network', retryable: true };
  } else if (err.message && err.message.includes('JSON')) {
    return { message: 'Error parsing response data. Please try again.', type: 'parsing', retryable: true };
  }
  return { message: err.message || 'An unknown error occurred.', type: 'unknown', retryable: true };
};

export interface PriorityInsightsProps {
  analysisId: string;
  initialData?: PriorityInsightsResponse | null; // Add optional initialData prop
}

export function PriorityInsights({ analysisId, initialData }: PriorityInsightsProps) {
  // Determine initial state based on initialData
  const getInitialLoadingState = () => {
    if (initialData) return 'loaded';
    if (!analysisId) return 'error'; // Error if no ID and no initial data
    return 'initial'; // Start fetching if ID exists but no initial data
  };

  const [loadingState, setLoadingState] = useState<'initial' | 'loading' | 'retrying' | 'loaded' | 'error'>(getInitialLoadingState);
  const [errorDetails, setErrorDetails] = useState<ErrorState | null>(!analysisId && !initialData ? { message: 'No Analysis ID provided.', type: 'unknown', retryable: false } : null);
  const [priorityData, setPriorityData] = useState<PriorityInsightsResponse | null>(initialData ?? null); // Use initialData if provided
  const [retryAttempt, setRetryAttempt] = useState(0);
  const [activeTab, setActiveTab] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const MAX_AUTO_RETRIES = 2;
  const RETRY_DELAY_MS = 1500;

  const { toast } = useToast();

  const fetchData = useCallback(async (isRetry = false, attemptNumber: number) => {
    // Skip fetch if data was provided initially or no analysisId
    if (initialData || !analysisId) {
      // If initialData was provided, state is already 'loaded'.
      // If no analysisId, state is already 'error'.
      return;
    }

    setLoadingState(isRetry ? 'retrying' : 'loading');
    setErrorDetails(null);

    try {
      console.log(`[PriorityInsights] Fetching data internally for analysis ID: ${analysisId}, Attempt: ${attemptNumber}`);
      const data = await apiClient.getPriorityInsights(analysisId);
      console.log(`[PriorityInsights] Internal fetch success: ${data.insights.length} insights found`);
      setPriorityData(data);
      setLoadingState('loaded');
    } catch (err: any) {
      console.error('[PriorityInsights] Internal fetch error:', err);
      const errorInfo = categorizeError(err);
      setErrorDetails(errorInfo);
      setLoadingState('error');

      if (attemptNumber <= MAX_AUTO_RETRIES && errorInfo.retryable) {
        console.log(`[PriorityInsights] Scheduling auto-retry #${attemptNumber + 1} in ${RETRY_DELAY_MS}ms`);
        setTimeout(() => {
          setRetryAttempt(prev => prev + 1);
        }, RETRY_DELAY_MS);
      } else if (attemptNumber > MAX_AUTO_RETRIES) {
        toast({
          title: "Error Loading Priority Insights",
          description: errorInfo.message,
          variant: errorInfo.type === 'auth' || errorInfo.type === 'server' ? 'destructive' : 'default',
        });
      }
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [analysisId, toast, initialData]); // Add initialData dependency

  // Fetch data only if initialData is not provided and we are in initial/retry state
  useEffect(() => {
    // Use a flag to prevent fetching if initialData was just set
    let shouldFetch = !initialData && analysisId && (loadingState === 'initial' || loadingState === 'retrying' || retryAttempt > 0);

    if (shouldFetch) {
      fetchData(retryAttempt > 0, retryAttempt + 1);
    }
    // If initialData is provided, ensure loading state is set correctly
    else if (initialData && loadingState !== 'loaded') {
        setLoadingState('loaded');
        setPriorityData(initialData);
    }
    // If no ID and no initial data, ensure error state
    else if (!analysisId && !initialData && loadingState !== 'error') {
        setLoadingState('error');
        setErrorDetails({ message: 'No Analysis ID provided.', type: 'unknown', retryable: false });
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [analysisId, fetchData, retryAttempt, initialData]); // Keep initialData dependency

  const handleManualRetry = () => {
    // Reset retry attempt count for manual retry? Or just increment? Let's increment.
    setRetryAttempt(prev => prev + 1);
    // Explicitly trigger fetch for manual retry - handled by useEffect now
  };

  // --- RENDER LOGIC ---

  // Render Loading state
  if (loadingState === 'loading' || loadingState === 'retrying') {
      return (
          <Card>
              <CardHeader>
                  <Skeleton className="h-8 w-48" />
                  <Skeleton className="h-4 w-64" />
              </CardHeader>
              <CardContent>
                  <div className="flex justify-center items-center py-8">
                      <RefreshCw className="h-6 w-6 mr-2 animate-spin" />
                      <span>{loadingState === 'retrying' ? `Retrying (Attempt ${retryAttempt + 1})...` : 'Loading Priority Insights...'}</span>
                  </div>
                  {/* Skeletons for content */}
                  <Skeleton className="h-10 w-full mb-4" />
                  <div className="space-y-4">
                      <Skeleton className="h-20 w-full" />
                      <Skeleton className="h-20 w-full" />
                  </div>
              </CardContent>
          </Card>
      );
  }

  // Render Error state
  if (loadingState === 'error' && errorDetails) {
      const ErrorIcon = errorDetails.type === 'network' ? WifiOff : AlertTriangle;
      return (
          <Card>
              <CardHeader>
                  <CardTitle>Priority Insights</CardTitle>
                  <CardDescription>Unable to load insights</CardDescription>
              </CardHeader>
              <CardContent>
                  <div className="p-4 border border-red-200 rounded-md bg-red-50 text-red-700 mb-4">
                      <div className="flex items-center gap-2 mb-3">
                          <ErrorIcon className="h-5 w-5" />
                          <span className="font-semibold">Error Loading Data</span>
                      </div>
                      <p>{errorDetails.message}</p>
                      {errorDetails.statusCode && (
                          <p className="mt-2 text-sm text-red-600">Status code: {errorDetails.statusCode}</p>
                      )}
                  </div>
                  {errorDetails.retryable && (
                      <div className="flex justify-end">
                          <Button onClick={handleManualRetry}>
                              <RefreshCw className="h-4 w-4 mr-2" />
                              Retry Now
                          </Button>
                      </div>
                  )}
              </CardContent>
          </Card>
      );
  }

  // Loaded State (Success)
  if (loadingState === 'loaded' && priorityData) {
    const filteredInsights = priorityData.insights.filter(insight => {
      if (activeTab === 'all') return true;
      return insight.urgency === activeTab;
    }) || [];
    // Keep helper functions: getUrgencyIcon, getUrgencyColorClass, getTypeBadge
    const getUrgencyIcon = (urgency: string) => {
        switch (urgency) {
          case 'high': return <AlertCircle className="h-4 w-4 text-red-500" />;
          case 'medium': return <AlertTriangle className="h-4 w-4 text-amber-500" />;
          case 'low': return <CheckCircle className="h-4 w-4 text-green-500" />;
          default: return null;
        }
      };
    const getUrgencyColorClass = (urgency: string) => {
        switch (urgency) {
          case 'high': return 'bg-red-50 text-red-700 border-red-200';
          case 'medium': return 'bg-amber-50 text-amber-700 border-amber-200';
          case 'low': return 'bg-green-50 text-green-700 border-green-200';
          default: return 'bg-slate-50 text-slate-700 border-slate-200';
        }
      };
    const getTypeBadge = (type: 'theme' | 'pattern') => {
        return (
          <Badge variant="outline" className={type === 'theme' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'}>
            {type.charAt(0).toUpperCase() + type.slice(1)}
          </Badge>
        );
      };

    return (
      <Card>
        <CardHeader>
          <CardTitle>Priority Insights</CardTitle>
          <CardDescription>
            Actionable insights prioritized by sentiment impact ({priorityData.insights.length} total)
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="all">All ({priorityData?.insights.length || 0})</TabsTrigger>
              <TabsTrigger value="high">High Priority ({priorityData?.metrics.high_urgency_count || 0})</TabsTrigger>
              <TabsTrigger value="medium">Medium ({priorityData?.metrics.medium_urgency_count || 0})</TabsTrigger>
              <TabsTrigger value="low">Low ({priorityData?.metrics.low_urgency_count || 0})</TabsTrigger>
            </TabsList>
            <TabsContent value={activeTab} className="mt-4">
              {filteredInsights.length === 0 ? (
                 <div className="text-center py-8 text-muted-foreground">No {activeTab !== 'all' ? activeTab + ' priority' : ''} insights found</div>
               ) : (
                 <div className="space-y-4">
                   {filteredInsights.map((insight: PrioritizedInsightWithOriginal, index) => (
                    <div
                      key={`${insight.type}-${insight.name}-${index}`}
                      className={`border rounded-lg p-4 ${getUrgencyColorClass(insight.urgency)}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                          {getUrgencyIcon(insight.urgency)}
                          <span className="font-medium capitalize">{insight.urgency} Priority</span>
                          {getTypeBadge(insight.type)}
                          {insight.category && (
                            <Badge variant="outline" className="bg-white">
                              {insight.category}
                            </Badge>
                          )}
                        </div>
                        <Badge variant="outline" className="bg-white">
                          Score: {insight.priority_score}
                        </Badge>
                      </div>

                      <h3 className="text-base font-semibold mb-1">
                        {insight.type === 'pattern' && insight.name.startsWith('Unnamed Pattern')
                          ? insight.description
                          : insight.name}
                      </h3>

                      {!(insight.type === 'pattern' && insight.name.startsWith('Unnamed Pattern')) && (
                        <p className="text-sm text-muted-foreground mb-3">{insight.description}</p>
                      )}

                      {/* Display supporting statements (evidence/examples) */}
                      {insight.type === 'pattern' && (insight.original as PatternOriginal).evidence && (insight.original as PatternOriginal).evidence!.length > 0 && (
                        <div className="mt-2 mb-3 pl-3 border-l-2 border-gray-200">
                          {(insight.original as PatternOriginal).evidence!.map((evidence: string, i: number) => (
                            <p key={i} className="text-sm text-muted-foreground italic mb-2">{evidence}</p>
                          ))}
                        </div>
                      )}
                      {insight.type === 'theme' && (insight.original as ThemeOriginal).examples && (insight.original as ThemeOriginal).examples!.length > 0 && (
                        <div className="mt-2 mb-3 pl-3 border-l-2 border-gray-200">
                          {(insight.original as ThemeOriginal).examples!.map((example: string, i: number) => (
                            <p key={i} className="text-sm text-muted-foreground italic mb-2">{example}</p>
                          ))}
                        </div>
                      )}

                      <div className="flex items-center gap-3 text-xs">
                        <span className="flex items-center gap-1">
                          <span className="font-medium">Sentiment:</span>
                          <Badge variant="outline" className={insight.sentiment > 0 ? 'bg-green-50' : (insight.sentiment < 0 ? 'bg-red-50' : 'bg-blue-50')}>
                            {insight.sentiment > 0 ? 'Positive' : (insight.sentiment < 0 ? 'Negative' : 'Neutral')}
                          </Badge>
                        </span>
                        <span className="flex items-center gap-1">
                          <span className="font-medium">Frequency:</span>
                          <Badge variant="outline" className="bg-white">
                            {Math.round(insight.frequency * 100)}%
                          </Badge>
                        </span>
                      </div>
                    </div>
                  ))}
                 </div>
               )}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    );
  }

  // Fallback / Initial state before fetch triggered (or if analysisId is missing)
   return (
      <Card>
         <CardHeader>
           <CardTitle>Priority Insights</CardTitle>
           <CardDescription>Initializing...</CardDescription>
         </CardHeader>
         <CardContent>
           <Skeleton className="h-10 w-full mb-4" />
           <div className="space-y-4">
             <Skeleton className="h-20 w-full" />
           </div>
         </CardContent>
      </Card>
   );
}

export default PriorityInsights;