// frontend/components/visualization/VisualizationTabs.tsx
'use client';

import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { ThemeChart } from './ThemeChart';
import { PatternList } from './PatternList';
import { SentimentGraph } from './SentimentGraph';
import { PersonaList } from './PersonaList';
import { PriorityInsights } from './PriorityInsights';
import { apiClient } from '@/lib/apiClient';
import { LoadingSpinner } from '@/components/loading-spinner';
import type { AnalyzedTheme, Theme, PriorityInsightsResponse } from '@/types/api';
import type { DetailedAnalysisResult } from '@/types/api';
import CustomErrorBoundary from './ErrorBoundary';
import { Alert, AlertDescription } from '@/components/ui/alert'; // Import Alert components
import { AlertCircle } from 'lucide-react'; // Import icon

interface VisualizationTabsProps {
  analysisId?: string;
  analysisData?: DetailedAnalysisResult | null;
}

export default function VisualizationTabs({
  analysisId: propAnalysisId,
  analysisData: serverAnalysisData
}: VisualizationTabsProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialTab = searchParams.get('visualizationTab') || 'themes';
  const [activeTab, setActiveTab] = useState(initialTab);

  const [analysis, setAnalysis] = useState<DetailedAnalysisResult | null>(serverAnalysisData ?? null);
  const [priorityData, setPriorityData] = useState<PriorityInsightsResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [fetchError, setFetchError] = useState<string | null>(null); // General error for main analysis
  const [priorityError, setPriorityError] = useState<string | null>(null); // Specific error for priority insights
  const lastFetchedId = useRef<string | null>(null);

  const effectiveAnalysisId = propAnalysisId || searchParams.get('analysisId') || '';

  useEffect(() => {
    let isMounted = true;
    const fetchAllData = async () => {
      if (!effectiveAnalysisId || lastFetchedId.current === effectiveAnalysisId) {
        if (!effectiveAnalysisId) setLoading(false);
        return;
      }

      console.log(`[VisualizationTabs] Fetching all data for ID: ${effectiveAnalysisId}`);
      setLoading(true);
      setFetchError(null);
      setPriorityError(null); // Reset priority error on new fetch
      setAnalysis(serverAnalysisData ?? null);
      setPriorityData(null);
      lastFetchedId.current = effectiveAnalysisId;

      try {
        // Fetch analysis details (only if not provided by server)
        const analysisPromise = serverAnalysisData
          ? Promise.resolve(serverAnalysisData)
          : apiClient.getAnalysisById(effectiveAnalysisId).catch(err => { // Catch errors fetching main analysis
              console.error("[VisualizationTabs] Failed to fetch main analysis data:", err);
              if (isMounted) {
                setFetchError(err instanceof Error ? err.message : 'Failed to load analysis data');
              }
              return null; // Return null on error
            });

        // Fetch priority insights separately with its own error handling
        const priorityPromise = apiClient.getPriorityInsights(effectiveAnalysisId)
          .catch(err => {
            const errorMsg = err instanceof Error ? err.message : 'Unknown priority insights error';
            console.error("[VisualizationTabs] Failed to fetch priority insights:", errorMsg);
            if (isMounted) {
              setPriorityError(errorMsg); // Set specific priority error
            }
            return null; // Return null on error
          });

        // Wait for both, allowing priority to fail gracefully
        const [analysisResult, priorityResult] = await Promise.all([
          analysisPromise,
          priorityPromise
        ]);

        if (isMounted) {
          console.log(`[VisualizationTabs] Fetched Analysis: ${analysisResult ? 'OK' : 'Failed/Null'}`);
          console.log(`[VisualizationTabs] Fetched Priority Insights: ${priorityResult ? 'OK' : 'Failed/Null'}`);
          setAnalysis(analysisResult);
          setPriorityData(priorityResult);
          // General fetchError is only set if main analysis fails
          if (!analysisResult && !fetchError) {
              setFetchError('Failed to load main analysis data.');
          }
        }
      } catch (error) { // Catch unexpected errors in Promise.all or setup
        console.error('[VisualizationTabs] Unexpected error during data fetch:', error);
        if (isMounted) {
          setFetchError(error instanceof Error ? error.message : 'An unexpected error occurred');
          setAnalysis(null);
          setPriorityData(null);
        }
      } finally {
        if (isMounted) setLoading(false);
      }
    };

     if (effectiveAnalysisId) {
       fetchAllData();
     } else {
       setLoading(false); // No ID, stop loading
       setAnalysis(null);
       setPriorityData(null);
     }

    return () => { isMounted = false; };
  }, [effectiveAnalysisId, serverAnalysisData]); // Keep dependencies

  const handleTabChange = useCallback((value: string) => {
    setActiveTab(value);
    const current = new URLSearchParams(Array.from(searchParams.entries()));
    current.set('visualizationTab', value);
    const search = current.toString();
    const query = search ? `?${search}` : '';
    router.replace(`/unified-dashboard/visualize${query}`);
  }, [searchParams, router]);

  const analyzedThemes: AnalyzedTheme[] = useMemo(() => {
    return (analysis?.themes || []).map((theme: Theme, index: number) => ({
      ...theme,
      id: theme.id != null ? String(theme.id) : `generated-theme-id-${index}`,
      prevalence: theme.frequency,
    }));
  }, [analysis?.themes]);

  console.log('[VisualizationTabs] Analysis data received:', analysis ? `ID: ${analysis.id}, Keys: ${Object.keys(analysis)}` : 'null');
  if (analysis) {
    console.log('[VisualizationTabs] Sentiment Statements:', analysis.sentimentStatements ? `Positive: ${analysis.sentimentStatements.positive?.length}, Neutral: ${analysis.sentimentStatements.neutral?.length}, Negative: ${analysis.sentimentStatements.negative?.length}` : 'MISSING');
    console.log('[VisualizationTabs] Sentiment Overview:', analysis.sentimentOverview);
  }
  console.log('[VisualizationTabs] Priority Data received:', priorityData ? `${priorityData.insights?.length} insights` : 'null');
  console.log('[VisualizationTabs] Priority Error:', priorityError); // Log priority error state


  // --- RENDER LOGIC ---

  if (loading) {
    return (
       <Card className="w-full">
         <CardContent className="flex justify-center items-center py-12">
           <LoadingSpinner label="Loading analysis results..." />
         </CardContent>
       </Card>
     );
  }

  // Show general error only if main analysis failed
  if (fetchError && !analysis) {
     return (
       <Card className="w-full">
         <CardContent className="py-12 text-center text-red-600">
           <p>Error loading analysis: {fetchError}</p>
           {/* Consider adding a retry button here */}
         </CardContent>
       </Card>
     );
  }

  if (!analysis) {
     return (
       <Card className="w-full">
         <CardContent className="py-12 text-center text-muted-foreground">
           No analysis data available. Please select an analysis from history or upload a new file.
         </CardContent>
       </Card>
     );
  }

  // Main return statement when analysis data is available
  return (
     <Card className="w-full">
        <CardHeader>
          <CardTitle>Analysis Results: {analysis.fileName || `ID ${analysis.id}`}</CardTitle>
          <CardDescription>
            Displaying analysis for {analysis.fileName ? `'${analysis.fileName}'` : `ID ${analysis.id}`}.
            Completed on: {analysis.createdAt ? new Date(analysis.createdAt).toLocaleString() : 'N/A'}
          </CardDescription>
        </CardHeader>
        <CardContent>
           <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
              <TabsList className="w-full grid grid-cols-5">
                 {/* ... TabsTriggers ... */}
                 <TabsTrigger value="themes">Themes</TabsTrigger>
                 <TabsTrigger value="patterns">Patterns</TabsTrigger>
                 <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
                 <TabsTrigger value="personas">Personas</TabsTrigger>
                 <TabsTrigger value="priority">Priority</TabsTrigger>
              </TabsList>

              <TabsContent value="themes" className="mt-6">
                <CustomErrorBoundary>
                  <ThemeChart themes={analyzedThemes} />
                </CustomErrorBoundary>
              </TabsContent>
              <TabsContent value="patterns" className="mt-6">
                <CustomErrorBoundary>
                  <PatternList patterns={analysis.patterns || []} />
                </CustomErrorBoundary>
              </TabsContent>
              <TabsContent value="sentiment" className="mt-6">
                <CustomErrorBoundary>
                  {analysis.sentimentOverview ? (
                    <SentimentGraph
                      data={analysis.sentimentOverview}
                      supportingStatements={analysis.sentimentStatements}
                    />
                  ) : (
                    <div className="text-center py-8 text-muted-foreground">Sentiment overview not available.</div>
                  )}
                </CustomErrorBoundary>
              </TabsContent>
              <TabsContent value="personas" className="mt-6">
                <CustomErrorBoundary>
                  <PersonaList personas={analysis.personas || []} />
                </CustomErrorBoundary>
              </TabsContent>
              <TabsContent value="priority" className="mt-6">
                 <CustomErrorBoundary>
                   {effectiveAnalysisId ? (
                     // Pass priorityData, which might be null if fetch failed
                     <PriorityInsights analysisId={effectiveAnalysisId} initialData={priorityData} />
                   ) : (
                     <div className="text-center py-8 text-muted-foreground">Analysis ID missing.</div>
                   )}
                   {/* Display specific priority error if it occurred */}
                   {priorityError && (
                      <Alert variant="destructive" className="mt-4">
                        <AlertCircle className="h-4 w-4" />
                        <AlertDescription>
                          Could not load Priority Insights: {priorityError}
                        </AlertDescription>
                      </Alert>
                   )}
                 </CustomErrorBoundary>
              </TabsContent>
           </Tabs>
        </CardContent>
     </Card>
  );
}
