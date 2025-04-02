// File: frontend/components/upload/EmergencyUploadPanel.tsx
'use client';

import React, { useRef, useState, useCallback, useEffect } from 'react'; // Ensure useRef is imported
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import { useToast } from '@/components/ui/use-toast';
import { AlertCircle, FileUp, FileText, FilePen, X } from 'lucide-react';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Alert, AlertDescription } from '@/components/ui/alert';
import type { UploadResponse, DetailedAnalysisResult } from '@/types/api';
import { uploadAction, analyzeAction, getRedirectUrl } from '@/app/actions';
import { apiClient } from '@/lib/apiClient';
import { useRouter } from 'next/navigation';
import { setCookie } from 'cookies-next';

export default function EmergencyUploadPanel() {
  const router = useRouter();
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const isMounted = useRef(true); // Moved useRef to top level

  // Local state
  const [file, setFile] = useState<File | null>(null);
  const [fileName, setFileName] = useState<string>('');
  const [fileSize, setFileSize] = useState<number>(0);
  const [isTextFile, setIsTextFile] = useState<boolean>(false);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false); // Tracks if analysis *or* polling is active
  const [uploadError, setUploadError] = useState<Error | null>(null);
  const [analysisError, setAnalysisError] = useState<Error | null>(null);
  const [resultId, setResultId] = useState<string | null>(null);
  const [analysisProgress, setAnalysisProgress] = useState<number>(0);
  const [pollingActive, setPollingActive] = useState<boolean>(false);
  const [pollAttempts, setPollAttempts] = useState(0);
  const MAX_POLL_ATTEMPTS = 20;
  const POLLING_INTERVAL = 3000;
  const [llmProvider, setLlmProvider] = useState<'openai' | 'gemini'>('gemini');

  // Effect to track mount status
  useEffect(() => {
    isMounted.current = true;
    // Cleanup function to set isMounted to false when component unmounts
    return () => {
      isMounted.current = false;
    };
  }, []); // Empty dependency array ensures this runs only on mount and unmount


  // Effect to get and set auth token in cookie
  useEffect(() => {
    const storeAuthToken = async () => {
      try {
        const token = await apiClient.getAuthToken();
        if (token) {
          document.cookie = `auth_token=${token}; path=/; max-age=3600; SameSite=Strict`;
          console.log('Auth token stored in cookie for server actions');
        } else {
          console.warn('No auth token available to store in cookie');
        }
      } catch (error) {
        console.error('Error storing auth token:', error);
      }
    };
    storeAuthToken();
  }, []);

  // Effect to poll for analysis completion
  useEffect(() => {
    let pollTimeoutId: NodeJS.Timeout | null = null;

    const stopPolling = () => {
      if (pollTimeoutId) {
        clearTimeout(pollTimeoutId);
        pollTimeoutId = null;
        console.log("[Polling] Polling timer cleared.");
      }
    };

    const pollStatus = async () => {
      // Stop conditions
      if (!resultId || !pollingActive || pollAttempts >= MAX_POLL_ATTEMPTS || !isMounted.current) {
        if (pollAttempts >= MAX_POLL_ATTEMPTS && pollingActive) { // Check pollingActive to avoid duplicate toasts
          console.error(`Polling timed out after ${MAX_POLL_ATTEMPTS} attempts for result ID: ${resultId}.`);
          setAnalysisError(new Error('Analysis took too long to complete. Please check history later.'));
          setPollingActive(false);
          setIsAnalyzing(false); // Stop overall analyzing state
          setAnalysisProgress(0); // Reset progress on timeout
          toast({
            title: "Analysis Timeout",
            description: "Analysis is taking longer than expected. Please check the history tab later.",
            variant: "destructive",
          });
        }
        stopPolling(); // Ensure timer is cleared if conditions not met
        return;
      }

      // Increment attempts immediately before the API call
      const currentAttempt = pollAttempts + 1;
      setPollAttempts(currentAttempt); // Update state for next potential run

      try {
        console.log(`[Polling Attempt ${currentAttempt}/${MAX_POLL_ATTEMPTS}] Checking analysis ID: ${resultId}`);
        // Poll the full results endpoint
        const analysisResult: DetailedAnalysisResult | null = await apiClient.getAnalysisById(resultId);

        // Check if polling should continue (component might have unmounted or polling stopped)
        if (!pollingActive || !isMounted.current) {
             console.log("[Polling] Polling stopped or component unmounted during fetch.");
             stopPolling();
             return;
        }

        if (analysisResult) {
          console.log(`[Polling] Received status: ${analysisResult.status}`);
          // Check for completion AND presence of essential data
          const isDataReady = analysisResult.themes && analysisResult.themes.length > 0;

          if (analysisResult.status === 'completed' && isDataReady) {
            console.log(`[Polling] Analysis ${resultId} completed and data is ready.`);
            stopPolling(); // Stop polling on success
            setPollingActive(false);
            setIsAnalyzing(false); // Stop overall analyzing state
            setAnalysisProgress(100);
            toast({
              title: "Analysis completed",
              description: "Redirecting to visualization...",
              variant: "default",
            });
            setTimeout(async () => {
              // Check again if component is still mounted before routing
              if (isMounted.current) {
                  const redirectUrl = await getRedirectUrl(resultId);
                  router.push(redirectUrl);
              }
            }, 800);
          } else if (analysisResult.status === 'failed') {
            console.error(`[Polling] Analysis ${resultId} failed.`);
            stopPolling(); // Stop polling on failure
            setPollingActive(false);
            setIsAnalyzing(false); // Stop overall analyzing state
            setAnalysisProgress(0);
            setAnalysisError(new Error(analysisResult.error || 'Analysis failed during processing'));
            toast({
              title: "Analysis failed",
              description: analysisResult.error || "Analysis failed during processing",
              variant: "destructive",
            });
          } else {
            // Still processing or data not ready, update progress visually
            setAnalysisProgress(prev => Math.min(prev + 5, 95)); // Increment progress visually
            // Schedule next poll only if still active
            if (pollingActive && isMounted.current) {
                pollTimeoutId = setTimeout(pollStatus, POLLING_INTERVAL);
            } else {
                stopPolling();
            }
          }
        } else {
           // Result was null, likely still processing or temporary error
           console.warn(`[Polling] getAnalysisById returned null for ${resultId}. Continuing poll.`);
           // Schedule next poll only if still active
           if (pollingActive && isMounted.current) {
               pollTimeoutId = setTimeout(pollStatus, POLLING_INTERVAL);
           } else {
               stopPolling();
           }
        }
      } catch (error) {
        console.error(`[Polling] Error polling status for ${resultId}:`, error);
        // Optional: Implement retry logic for polling errors or stop polling
        // For now, continue polling up to max attempts
        if (currentAttempt < MAX_POLL_ATTEMPTS && pollingActive && isMounted.current) { // Use currentAttempt for check
            pollTimeoutId = setTimeout(pollStatus, POLLING_INTERVAL);
        } else if (pollingActive) { // Only show error if polling was still supposed to be active
            // Handle final polling error after max attempts
            stopPolling(); // Stop polling on final error
            setAnalysisError(new Error('Failed to get analysis status after multiple attempts.'));
            setPollingActive(false);
            setIsAnalyzing(false); // Stop overall analyzing state
            toast({
                title: "Status Check Failed",
                description: "Could not confirm analysis status. Please check history.",
                variant: "destructive",
            });
        } else {
            stopPolling(); // Ensure stopped if pollingActive became false during error handling
        }
      }
    };

    if (pollingActive && resultId) {
      // Reset attempts only when polling becomes active for a *new* ID or explicitly restarted
      // This check prevents resetting attempts on every render while polling is active
      if (pollAttempts === 0) {
          console.log("[Polling] Starting polling sequence...");
          pollStatus(); // Start the first poll
      }
    } else {
        stopPolling(); // Ensure polling stops if pollingActive becomes false or resultId is null
    }

    // Cleanup function for this useEffect
    return () => {
      stopPolling(); // Clear timeout on effect cleanup
    };
  }, [pollingActive, resultId, router, toast, pollAttempts]); // Keep pollAttempts dependency

  // Handle file selection
  const handleFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFile(file);
      setFileName(file.name);
      setFileSize(file.size);
      setIsTextFile(file.type.includes('text') || file.name.endsWith('.txt'));
      setUploadProgress(0);
      setResultId(null);
      setUploadError(null);
      setAnalysisError(null);
      setPollingActive(false);
      setPollAttempts(0);
      setIsAnalyzing(false);
      setAnalysisProgress(0);
    }
  }, []);

  // Handle file upload and analysis trigger
  const handleUploadAndAnalyze = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) {
      setUploadError(new Error('Please select a file to upload'));
      toast({ title: "Upload failed", description: "Please select a file to upload", variant: "destructive" });
      return;
    }
    setIsUploading(true);
    setIsAnalyzing(true); // Set analyzing state immediately for combined action
    setUploadError(null);
    setAnalysisError(null);
    setPollingActive(false);
    setPollAttempts(0);
    setAnalysisProgress(0); // Reset progress
    setUploadProgress(10);
    setResultId(null); // Clear previous result ID

    let currentDataId: number | null = null; // To track which phase the error occurred in

    try {
      // 1. Upload
      console.log("Starting upload...");
      const authToken = await apiClient.getAuthToken();
      if (authToken) setCookie('auth-token', authToken);
      const formData = new FormData();
      formData.append('file', file);
      formData.append('isTextFile', String(isTextFile));
      const uploadResult = await uploadAction(formData);

      if (!uploadResult.success) {
        // Use type guard to access error property safely
        const errorMessage = 'error' in uploadResult ? uploadResult.error : 'Upload failed';
        throw new Error(errorMessage); // Throw error to be caught below
      }

      setUploadProgress(100);
      currentDataId = uploadResult.uploadResponse.data_id; // Store dataId after successful upload
      toast({ title: "Upload successful", description: `File ${fileName} uploaded. Starting analysis...`, variant: "default" });
      setIsUploading(false); // Upload finished

      // 2. Analyze (immediately after successful upload)
      console.log(`Starting analysis for data ID: ${currentDataId}...`);
      setAnalysisProgress(10); // Show analysis starting progress
      const analysisActionResult = await analyzeAction(currentDataId, isTextFile, llmProvider);

      if (!analysisActionResult.success) {
         // Use type guard
         const errorMessage = 'error' in analysisActionResult ? analysisActionResult.error : 'Analysis initiation failed';
         throw new Error(errorMessage); // Throw error to be caught below
      }

      const analysisId = analysisActionResult.analysisResponse.result_id.toString();
      setResultId(analysisId);
      setPollAttempts(0); // Reset poll attempts for the new analysis
      setPollingActive(true); // Start polling
      setAnalysisProgress(30); // Show initial analysis progress
      toast({
        title: "Analysis started",
        description: "Analysis processing initiated. This may take a few moments...",
        variant: "default",
      });
      // isAnalyzing remains true while polling

    } catch (error) {
      console.error('Upload & Analyze error:', error);
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      // Determine if error happened during upload or analysis phase
      if (currentDataId === null) { // Error happened during upload
          setUploadError(new Error(errorMessage));
          toast({ title: "Upload Failed", description: errorMessage, variant: "destructive" });
      } else { // Error happened during analysis trigger
          setAnalysisError(new Error(errorMessage));
          toast({ title: "Analysis Failed", description: errorMessage, variant: "destructive" });
      }
      setIsUploading(false);
      setIsAnalyzing(false); // Ensure analyzing state is reset on any error
      setPollingActive(false);
      setAnalysisProgress(0);
    }
  }, [file, isTextFile, toast, apiClient, fileName, llmProvider, router]); // Added dependencies


  // Trigger file input click
  const handleSelectFileClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // Handle clear file
  const handleClearFile = useCallback(() => {
    setFile(null);
    setFileName('');
    setFileSize(0);
    setUploadProgress(0);
    setResultId(null);
    setUploadError(null);
    setAnalysisError(null);
    setIsUploading(false);
    setIsAnalyzing(false);
    setPollingActive(false);
    setPollAttempts(0);
    setAnalysisProgress(0);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  // Toggle text file setting
  const handleToggleTextFile = useCallback((value: string) => {
    setIsTextFile(value === 'text');
  }, []);

  // Format file size for display
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Upload Data for Analysis</CardTitle>
        <CardDescription>
          Upload a file to analyze with design thinking frameworks. Select the LLM provider below.
        </CardDescription>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleUploadAndAnalyze} className="space-y-4"> {/* Use form onSubmit */}
          {/* LLM Provider Selection */}
           <div className="mb-4">
             <Label htmlFor="llm-provider" className="mb-2 block">LLM Provider</Label>
             <RadioGroup
               defaultValue={llmProvider}
               onValueChange={(value: 'openai' | 'gemini') => setLlmProvider(value)}
               className="flex space-x-4"
               id="llm-provider"
             >
               <div className="flex items-center space-x-2">
                 <RadioGroupItem value="gemini" id="gemini" />
                 <Label htmlFor="gemini">Gemini</Label>
               </div>
               <div className="flex items-center space-x-2">
                 <RadioGroupItem value="openai" id="openai" />
                 <Label htmlFor="openai">OpenAI</Label>
               </div>
             </RadioGroup>
           </div>

          {/* File Type Selection */}
          <div className="mb-4">
             <Label htmlFor="data-type" className="mb-2 block">Data Type</Label>
             <RadioGroup
               defaultValue={isTextFile ? 'text' : 'structured'}
               onValueChange={handleToggleTextFile}
               className="flex space-x-4"
               id="data-type"
             >
               <div className="flex items-center space-x-2">
                 <RadioGroupItem value="structured" id="structured" />
                 <Label htmlFor="structured">Structured Data (CSV, Excel)</Label>
               </div>
               <div className="flex items-center space-x-2">
                 <RadioGroupItem value="text" id="text" />
                 <Label htmlFor="text">Free Text</Label>
               </div>
             </RadioGroup>
           </div>

          {/* File Upload Area */}
          <div
            className="border-2 border-dashed rounded-lg p-6 text-center hover:bg-gray-50 cursor-pointer transition-colors"
            onClick={handleSelectFileClick}
          >
             <input
               ref={fileInputRef}
               type="file"
               data-testid="file-input"
               className="hidden"
               onChange={handleFileChange}
               accept={isTextFile ? ".txt,.md,.doc,.docx" : ".csv,.xlsx,.xls,.json"}
             />
             {!fileName ? (
               <div className="flex flex-col items-center justify-center text-muted-foreground">
                 <FileUp className="h-10 w-10 mb-2" />
                 <p className="text-sm mb-1">Click to upload or drag and drop</p>
                 <p className="text-xs">
                   {isTextFile ? "TXT, DOC, DOCX or MD files" : "CSV, XLSX or JSON files"}
                 </p>
               </div>
             ) : (
               <div className="flex items-center justify-between">
                 <div className="flex items-center">
                   {isTextFile ? <FileText className="h-8 w-8 mr-2" /> : <FilePen className="h-8 w-8 mr-2" />}
                   <div className="text-left">
                     <p className="text-sm font-medium text-foreground">{fileName}</p>
                     <p className="text-xs text-muted-foreground">{formatFileSize(fileSize)}</p>
                   </div>
                 </div>
                 <Button type="button" variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); handleClearFile(); }}>
                   <X className="h-4 w-4" />
                 </Button>
               </div>
             )}
          </div>

          {/* Error messages */}
          {uploadError && ( <Alert variant="destructive" className="mt-4"><AlertCircle className="h-4 w-4" /><AlertDescription>{uploadError.message}</AlertDescription></Alert> )}
          {analysisError && ( <Alert variant="destructive" className="mt-4"><AlertCircle className="h-4 w-4" /><AlertDescription>{analysisError.message}</AlertDescription></Alert> )}

          {/* Upload progress */}
          {isUploading && (
             <div className="mt-4 space-y-2">
               <div className="flex justify-between text-xs">
                 <span>Uploading...</span>
                 <span>Please wait</span>
               </div>
               <Progress value={uploadProgress} className="h-2" />
             </div>
           )}

          {/* Analysis progress */}
          {isAnalyzing && !isUploading && ( // Show only after upload completes or if analysis started separately
            <div className="mt-4 space-y-2">
              <div className="flex justify-between text-xs">
                <span>{pollingActive ? `Polling Status (Attempt ${pollAttempts}/${MAX_POLL_ATTEMPTS})...` : 'Analyzing...'}</span>
                <span>{analysisProgress < 100 ? 'This may take a moment' : 'Redirecting...'}</span>
              </div>
              <Progress value={analysisProgress} className="h-2" />
              <div className="text-right text-xs text-muted-foreground">
                {analysisProgress}%
              </div>
            </div>
          )}

           {/* Footer Buttons within the form */}
           <CardFooter className="flex justify-between p-0 pt-4">
             <Button
               type="button" // Prevent form submission
               variant="outline"
               onClick={handleClearFile}
               disabled={isUploading || isAnalyzing || !fileName}
             >
               Clear
             </Button>
             <Button
               type="submit" // Submit the form
               disabled={isUploading || isAnalyzing || !fileName}
             >
               {isUploading ? 'Uploading...' : (isAnalyzing ? 'Analyzing...' : 'Upload & Analyze')}
             </Button>
           </CardFooter>
        </form> {/* Close form */}
      </CardContent>
      {/* Footer moved inside the form */}
    </Card>
  );
}
