/**
 * UnifiedDashboard Component (Refactored)
 * 
 * ARCHITECTURAL NOTE: This is the standardized implementation of the dashboard, using
 * the VisualizationTabs component for analysis visualization. This implementation
 * follows the current architectural decision to use specialized visualization components
 * directly through VisualizationTabs, rather than wrapping them with UnifiedVisualization.
 * 
 * This file replaces the older page.tsx implementation and should be used as the
 * reference for future development.
 */

'use client';

import React, { useState, useEffect } from 'react';
import { useRouter, usePathname, useSearchParams } from 'next/navigation';
import { LoadingSpinner } from '@/components/loading-spinner';
import { useToast } from '@/components/providers/toast-provider';
import { useAuth } from '@clerk/nextjs';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { FileText, Clock, Database } from 'lucide-react';
import Link from 'next/link';
import { Card } from '@/components/ui/card';

// Import our refactored components
import EmergencyUploadPanel from '@/components/upload/EmergencyUploadPanel';
import VisualizationTabs from '@/components/visualization/VisualizationTabs';

// Import stores
import { useAnalysisStore } from '@/store/useAnalysisStore';
import { useUploadStore } from '@/store/useUploadStore';

/**
 * Main dashboard component
 * Uses the new component structure and state management
 */
export default function UnifiedDashboard() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { showToast } = useToast();
  const { userId, isLoaded } = useAuth();
  
  // State for active tab
  const [activeTab, setActiveTab] = useState<'upload' | 'visualize' | 'history' | 'documentation'>('upload');
  
  // Get analysis state
  const currentAnalysis = useAnalysisStore(state => state.currentAnalysis);
  const analysisHistory = useAnalysisStore(state => state.analysisHistory);
  
  // Get upload state
  const uploadResponse = useUploadStore(state => state.uploadResponse);
  const analysisResponse = useUploadStore(state => state.analysisResponse);
  
  // Handle authentication redirection
  useEffect(() => {
    if (isLoaded && !userId) {
      router.push('/sign-in');
    }
  }, [isLoaded, userId, router]);
  
  // Get tab from URL query parameter
  useEffect(() => {
    const tabParam = searchParams?.get('tab');
    
    if (tabParam) {
      // Set the active tab based on URL parameter
      if (tabParam === 'history' || tabParam === 'documentation' || 
          tabParam === 'visualize' || tabParam === 'upload') {
        setActiveTab(tabParam as 'upload' | 'visualize' | 'history' | 'documentation');
      }
    }
    
    // Check for analysisId in URL and load it if needed
    const analysisId = searchParams?.get('analysisId');
    if (analysisId && tabParam === 'visualize') {
      // Load the analysis if it's not already loaded
      const currentId = currentAnalysis?.id;
      if (!currentId || currentId !== analysisId) {
        // Get analysis store and fetch the analysis by ID
        const analysisStore = useAnalysisStore.getState();
        analysisStore.fetchAnalysisById(analysisId);
      }
    }
  }, [searchParams, currentAnalysis]);
  
  // Handle simple tab changes (only for upload, visualize, documentation)
  const handleTabChange = (tab: string) => {
    if (tab === 'history') {
      // History tab is handled through the Link component directly
      return;
    }
    
    setActiveTab(tab as any);
    
    // Update the URL to reflect the tab change
    const params = new URLSearchParams(searchParams?.toString());
    params.set('tab', tab);
    router.push(`/unified-dashboard?${params.toString()}`);
  };
  
  // Handle auto-tab switching for analyses
  useEffect(() => {
    // Auto-switch to visualization tab when analysis is loaded
    if (currentAnalysis && activeTab !== 'visualize') {
      handleTabChange('visualize');
      showToast('Analysis loaded successfully', { variant: 'success' });
    }
  }, [currentAnalysis, activeTab, showToast]);
  
  // If still loading auth state, show spinner
  if (!isLoaded) {
    return <LoadingSpinner />;
  }
  
  return (
    <div className="w-full">
      <Tabs value={activeTab} onValueChange={handleTabChange} className="w-full">
        <TabsContent value="upload" className="mt-6">
          <EmergencyUploadPanel />
        </TabsContent>
        
        <TabsContent value="visualize" className="mt-6">
          {currentAnalysis ? (
            <VisualizationTabs />
          ) : analysisResponse ? (
            <VisualizationTabs analysisId={analysisResponse.result_id.toString()} />
          ) : (
            <Alert>
              <AlertTitle>No Analysis Selected</AlertTitle>
              <AlertDescription>
                Please upload a file and run an analysis, or select an analysis from your history.
              </AlertDescription>
            </Alert>
          )}
        </TabsContent>
        
        <TabsContent value="history" className="mt-6">
          <Card className="p-4">
            <div className="text-center py-4">
              <Database className="h-8 w-8 mx-auto text-primary mb-2" />
              <h3 className="text-lg font-medium mb-2">Analysis History</h3>
              <p className="text-muted-foreground mb-4">
                View and manage your analysis history
              </p>
              <Link href="/unified-dashboard/history" className="inline-flex items-center justify-center rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2">
                Go to Analysis History
              </Link>
            </div>
          </Card>
        </TabsContent>
        
        <TabsContent value="documentation" className="mt-6">
          <DocumentationPanel />
        </TabsContent>
      </Tabs>
    </div>
  );
}

/**
 * Simple documentation panel component
 * This could be extracted to its own file in the future
 */
function DocumentationPanel() {
  return (
    <div className="prose prose-sm max-w-none dark:prose-invert">
      <h2>Interview Insight Analyst Documentation</h2>
      
      <h3>Getting Started</h3>
      <p>
        Upload an interview transcript to analyze themes, patterns, and sentiment.
        The system works best with conversation-style interviews, either in plain text
        format or in a structured JSON format.
      </p>
      
      <h3>File Formats</h3>
      <ul>
        <li>
          <strong>Plain Text (.txt)</strong> - Simple text file with the interview transcript.
          The system will attempt to identify speakers and segments automatically.
        </li>
        <li>
          <strong>JSON Format</strong> - Structured interview data with the following format:
          <pre>
            {`{
  "metadata": {
    "title": "Interview Title",
    "date": "2024-03-10",
    "participants": ["Interviewer", "Subject"]
  },
  "transcript": [
    {
      "speaker": "Interviewer",
      "text": "Tell me about your experience with...",
      "timestamp": "00:01:24"
    },
    {
      "speaker": "Subject",
      "text": "Well, I've been working with this technology for...",
      "timestamp": "00:01:32"
    }
  ]
}`}
          </pre>
        </li>
      </ul>
      
      <h3>Analysis Process</h3>
      <ol>
        <li>Upload your interview file using the Upload tab.</li>
        <li>Select your preferred LLM provider (OpenAI or Gemini).</li>
        <li>Click "Start Analysis" to begin processing.</li>
        <li>Once complete, view the results in the Visualization tab.</li>
      </ol>
      
      <h3>Understanding the Results</h3>
      <ul>
        <li>
          <strong>Themes</strong> - Key topics and concepts mentioned in the interview,
          with frequency and representative quotes.
        </li>
        <li>
          <strong>Patterns</strong> - Recurring behaviors, attitudes, or expressions
          identified in the interview.
        </li>
        <li>
          <strong>Sentiment</strong> - Emotional tone throughout the interview,
          shown as a timeline and with supporting statements.
        </li>
        <li>
          <strong>Personas</strong> - AI-generated profiles based on the interview content,
          identifying roles, responsibilities, and characteristics.
        </li>
      </ul>
    </div>
  );
} 