/**
 * VisualizationTabs Component
 * 
 * ARCHITECTURAL NOTE: This is the standardized component for visualizing analysis results.
 * It should directly render the specialized visualization components:
 * - ThemeChart for themes (which includes its own Key Insights)
 * - PatternList for patterns
 * - SentimentGraph for sentiment
 * - PersonaList for personas
 * 
 * DO NOT use UnifiedVisualization to wrap these components, as this leads to 
 * duplicate UI elements (like key insights sections). This component replaces
 * the older approach of using UnifiedVisualization for all visualization types.
 */

import React, { useEffect, useState } from 'react';
import { 
  useAnalysisStore, 
  useCurrentAnalysis, 
  useVisualizationTab 
} from '@/store/useAnalysisStore';
import { ThemeChart } from '@/components/visualization/ThemeChart';
import { PatternList } from '@/components/visualization/PatternList';
import { SentimentGraph } from '@/components/visualization/SentimentGraph';
import { PersonaList } from '@/components/visualization/PersonaList';
import { PriorityInsights } from '@/components/visualization/PriorityInsights';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';
import { useRouter, useSearchParams } from 'next/navigation';

interface VisualizationTabsProps {
  analysisId?: string;
}

// Define a type for the tab values
type TabValue = 'themes' | 'patterns' | 'sentiment' | 'personas' | 'priority';

/**
 * VisualizationTabs Component
 * Displays visualization tabs for themes, patterns, sentiment, and personas
 */
export default function VisualizationTabs({ analysisId }: VisualizationTabsProps) {
  // Get current analysis and tab state
  const { analysis, isLoading, error } = useCurrentAnalysis();
  const { tab: activeTab, setTab: setActiveTab } = useVisualizationTab();
  
  // Get fetch action from store
  const fetchAnalysisById = useAnalysisStore(state => state.fetchAnalysisById);
  
  // Get the URL query parameters to support specific tab navigation
  const router = useRouter();
  const searchParams = useSearchParams();
  const defaultTab = searchParams.get('tab') as TabValue | null;
  
  // Initialize active tab state with default from URL or 'themes'
  const [activeTabState, setActiveTabState] = useState<TabValue>(defaultTab || 'themes');
  
  // Handle tab change
  const handleTabChange = (newTab: string) => {
    setActiveTabState(newTab as TabValue);
    
    // Update the URL to reflect the current tab for sharing/bookmarking
    const params = new URLSearchParams(searchParams);
    params.set('tab', newTab);
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    
    // Update global state for other components to reference
    setActiveTab(newTab as TabValue);
  };
  
  // If an analysisId is provided, fetch the analysis when the component mounts
  useEffect(() => {
    if (analysisId && (!analysis || analysis.id !== analysisId)) {
      fetchAnalysisById(analysisId, true); // Fetch with polling
    }
  }, [analysisId, analysis, fetchAnalysisById]);
  
  // If still loading, show spinner
  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="flex justify-center items-center py-12">
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Loading analysis...</p>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  // If there's an error, display it
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error Loading Analysis</AlertTitle>
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }
  
  // If no analysis is loaded, show message
  if (!analysis) {
    return (
      <Card className="w-full">
        <CardContent className="py-12">
          <div className="text-center">
            <h3 className="text-lg font-medium">No Analysis Selected</h3>
            <p className="text-muted-foreground mt-2">
              Please upload a file and run an analysis, or select an analysis from your history.
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Analysis Results: {analysis.fileName}</CardTitle>
        <CardDescription>
          Created {new Date(analysis.createdAt).toLocaleString()} • {analysis.llmProvider || 'AI'} Analysis
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <Tabs value={activeTabState} onValueChange={handleTabChange} className="w-full">
          <TabsList className="w-full grid grid-cols-5">
            <TabsTrigger value="themes">Themes</TabsTrigger>
            <TabsTrigger value="patterns">Patterns</TabsTrigger>
            <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
            <TabsTrigger value="personas">Personas</TabsTrigger>
            <TabsTrigger value="priority">Priority</TabsTrigger>
          </TabsList>
          
          <TabsContent value="themes" className="mt-6">
            {analysis.themes.length > 0 ? (
              <ThemeChart themes={analysis.themes} />
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No themes detected in this interview.
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="patterns" className="mt-6">
            {analysis.patterns.length > 0 ? (
              <PatternList patterns={analysis.patterns} />
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No patterns detected in this interview.
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="sentiment" className="mt-6">
            {analysis.sentiment.length > 0 ? (
              <SentimentGraph 
                data={analysis.sentimentOverview}
                detailedData={analysis.sentiment}
                supportingStatements={analysis.sentimentStatements}
              />
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No sentiment data available for this interview.
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="personas" className="mt-6">
            {analysis.personas && analysis.personas.length > 0 ? (
              <PersonaList personas={analysis.personas} />
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                No personas detected in this interview.
              </div>
            )}
          </TabsContent>
          
          <TabsContent value="priority" className="mt-6">
            <PriorityInsights analysisId={analysisId || ''} />
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
} 