'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText } from 'lucide-react';
import { DashboardData } from '@/types/api';
import { ThemeChart } from '@/components/visualization/ThemeChart';
import { PatternList } from '@/components/visualization/PatternList';
import { SentimentGraph } from '@/components/visualization/SentimentGraph';
import { PersonaList } from '@/components/visualization/PersonaList';
import NoResultsView from './NoResultsView';

interface VisualizationTabProps {
  dashboardData?: DashboardData | null;
}

/**
 * Tab for visualizing analysis results with multiple visualization options
 */
const VisualizationTab = ({ dashboardData }: VisualizationTabProps) => {
  // Visualization sub-tab state
  const [activeTab, setActiveTab] = useState<'themes' | 'patterns' | 'sentiment' | 'personas'>('themes');
  
  // Update URL when visualization tab changes
  useEffect(() => {
    let isMounted = true;
    
    // Use setTimeout to slightly delay the URL update to avoid race conditions
    const updateTimer = setTimeout(() => {
      if (isMounted && typeof window !== 'undefined') {
        const url = new URL(window.location.href);
        const currentVisualizationTab = url.searchParams.get('visualizationTab');
        
        // Only update if the tab has actually changed to avoid unnecessary history entries
        if (currentVisualizationTab !== activeTab) {
          url.searchParams.set('visualizationTab', activeTab);
          window.history.replaceState({}, '', url); // Use replaceState instead of pushState
        }
      }
    }, 50); // Small delay to avoid race conditions
    
    // Cleanup function to handle component unmounting
    return () => {
      isMounted = false;
      clearTimeout(updateTimer);
    };
  }, [activeTab]);
  
  // Get visualization tab from URL
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const searchParams = new URLSearchParams(window.location.search);
      const visualizationTabParam = searchParams.get('visualizationTab');
      
      if (visualizationTabParam && (
          visualizationTabParam === 'themes' || 
          visualizationTabParam === 'patterns' || 
          visualizationTabParam === 'sentiment' || 
          visualizationTabParam === 'personas'
      )) {
        setActiveTab(visualizationTabParam as any);
      }
    }
  }, []);
  
  // Debug logging for sentiment visualization - wrapped in try/catch to prevent errors
  useEffect(() => {
    let isMounted = true;
    let logTimer: NodeJS.Timeout;

    if (dashboardData && activeTab === 'sentiment' && isMounted) {
      // Defer logging to avoid blocking tab switching
      logTimer = setTimeout(() => {
        try {
          console.log('DashboardData object for sentiment visualization:', 
            typeof dashboardData === 'object' ? 'Object' : typeof dashboardData);
          
          // Only log if the properties exist
          if (dashboardData.sentimentStatements) {
            console.log('SentimentStatements in dashboardData:', 
              typeof dashboardData.sentimentStatements === 'object' ? 'Object' : typeof dashboardData.sentimentStatements);
          }
          
          if (dashboardData.sentimentOverview) {
            console.log('Sentiment overview:', 
              typeof dashboardData.sentimentOverview === 'object' ? 'Object' : typeof dashboardData.sentimentOverview);
          }
        } catch (error) {
          // Suppress errors in logging
          console.error('Error in sentiment debug logging:', error);
        }
      }, 100);
    }
    
    return () => {
      isMounted = false;
      if (logTimer) clearTimeout(logTimer);
    };
  }, [dashboardData, activeTab]);
  
  // If no results available, show placeholder
  if (!dashboardData) {
    return <NoResultsView />;
  }
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Analysis Results</CardTitle>
        <CardDescription>
          Visualization of interview analysis results
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
          <TabsList className="grid grid-cols-4 mb-6">
            <TabsTrigger value="themes">Themes</TabsTrigger>
            <TabsTrigger value="patterns">Patterns</TabsTrigger>
            <TabsTrigger value="sentiment">Sentiment</TabsTrigger>
            <TabsTrigger value="personas">Personas</TabsTrigger>
          </TabsList>
          
          <TabsContent value="themes">
            {dashboardData.themes && dashboardData.themes.length > 0 ? (
              <ThemeChart themes={dashboardData.themes} />
            ) : (
              <Alert>
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  No themes found in the analysis results.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
          
          <TabsContent value="patterns">
            {dashboardData.patterns && dashboardData.patterns.length > 0 ? (
              <PatternList patterns={dashboardData.patterns} />
            ) : (
              <Alert>
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  No patterns found in the analysis results.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
          
          <TabsContent value="sentiment">
            {dashboardData.sentimentStatements && 
             (Object.keys(dashboardData.sentimentStatements).length > 0 || 
              (dashboardData.sentimentStatements.positive && dashboardData.sentimentStatements.positive.length > 0) ||
              (dashboardData.sentimentStatements.negative && dashboardData.sentimentStatements.negative.length > 0) ||
              (dashboardData.sentimentStatements.neutral && dashboardData.sentimentStatements.neutral.length > 0)) ? (
              <SentimentGraph 
                data={dashboardData.sentimentOverview}
                supportingStatements={dashboardData.sentimentStatements}
              />
            ) : (
              <Alert>
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  No sentiment data found in the analysis results.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
          
          <TabsContent value="personas">
            {dashboardData.personas && dashboardData.personas.length > 0 ? (
              <PersonaList personas={dashboardData.personas} />
            ) : (
              <Alert>
                <FileText className="h-4 w-4" />
                <AlertDescription>
                  No personas found in the analysis results.
                </AlertDescription>
              </Alert>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default VisualizationTab;
