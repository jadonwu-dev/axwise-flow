'use client';

import { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { FileText } from 'lucide-react';
import { DetailedAnalysisResult } from '@/types/api';
import { ThemeChart } from '@/components/visualization/ThemeChart';
import { PatternList } from '@/components/visualization/PatternList';
import { SentimentGraph } from '@/components/visualization/SentimentGraph';
import { PersonaList } from '@/components/visualization/PersonaList';
import NoResultsView from './NoResultsView';

interface VisualizationTabProps {
  results?: DetailedAnalysisResult | null;
}

/**
 * Tab for visualizing analysis results with multiple visualization options
 */
const VisualizationTab = ({ results }: VisualizationTabProps) => {
  // Visualization sub-tab state
  const [activeTab, setActiveTab] = useState<'themes' | 'patterns' | 'sentiment' | 'personas'>('themes');
  
  // Update URL when visualization tab changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const url = new URL(window.location.href);
      url.searchParams.set('visualizationTab', activeTab);
      window.history.pushState({}, '', url);
    }
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
  
  // Debug logging for sentiment visualization
  useEffect(() => {
    if (results && activeTab === 'sentiment') {
      console.log('Results object for sentiment visualization:', results);
      console.log('SentimentStatements in results:', results.sentimentStatements);
      console.log('Sentiment overview:', results.sentimentOverview);
    }
  }, [results, activeTab]);
  
  // If no results available, show placeholder
  if (!results) {
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
            {results.themes && results.themes.length > 0 ? (
              <ThemeChart themes={results.themes} />
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
            {results.patterns && results.patterns.length > 0 ? (
              <PatternList patterns={results.patterns} />
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
            {results.sentimentStatements && results.sentimentStatements.length > 0 ? (
              <SentimentGraph 
                sentimentStatements={results.sentimentStatements} 
                sentimentOverview={results.sentimentOverview} 
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
            {results.personas && results.personas.length > 0 ? (
              <PersonaList personas={results.personas} />
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
