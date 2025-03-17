'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Upload } from 'lucide-react';
import { useToast } from '@/components/providers/toast-provider';
import { apiClient } from '@/lib/apiClient';
import AnalysisProgress from '@/components/AnalysisProgress';
import AnalysisOptions from './AnalysisOptions';
import { FileUpload } from '@/components/FileUpload';
import { UploadResponse, AnalysisResponse } from '@/types/api';

/**
 * Upload tab component for handling file uploads and analysis triggering
 */
const UploadTab = () => {
  const { showToast } = useToast();
  
  // Upload and analysis state
  const [file, setFile] = useState<File | null>(null);
  const [isTextFile, setIsTextFile] = useState<boolean>(false);
  const [uploadResponse, setUploadResponse] = useState<UploadResponse | null>(null);
  const [analysisResponse, setAnalysisResponse] = useState<AnalysisResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [authToken] = useState<string>('testuser123');
  const [llmProvider, setLlmProvider] = useState<'openai' | 'gemini'>('gemini');
  
  // Handle file selection from the FileUpload component
  const handleFileChange = (selectedFile: File, isText: boolean) => {
    setFile(selectedFile);
    setIsTextFile(isText);
    console.log(`Selected file: ${selectedFile.name}, isTextFile: ${isText}`);
  };

  // Handle file upload
  const handleUpload = async () => {
    if (!file) {
      showToast('Please select a file to upload', { variant: 'error' });
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Set auth token
      apiClient.setAuthToken(authToken);
      
      // Upload the file, passing the isTextFile flag
      const response = await apiClient.uploadData(file, isTextFile);
      setUploadResponse(response);
      showToast('File uploaded successfully', { variant: 'success' });
      
      // Clear previous analysis data
      setAnalysisResponse(null);
    } catch (err) {
      setError(`Upload failed: ${err instanceof Error ? err.message : String(err)}`);
      showToast(`Upload failed: ${err instanceof Error ? err.message : String(err)}`, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  // Handle starting analysis
  const handleStartAnalysis = async () => {
    if (!uploadResponse) {
      showToast('Please upload a file first', { variant: 'error' });
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      // Set auth token
      apiClient.setAuthToken(authToken);
      
      // Start analysis with the selected LLM provider
      const response = await apiClient.analyzeData(uploadResponse.data_id, llmProvider);
      setAnalysisResponse(response);
      showToast('Analysis started', { variant: 'success' });
    } catch (err) {
      setError(`Analysis failed: ${err instanceof Error ? err.message : String(err)}`);
      showToast(`Analysis failed: ${err instanceof Error ? err.message : String(err)}`, { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Upload Interview Data</CardTitle>
        <CardDescription>
          Upload interview data in JSON or text format for analysis
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          <FileUpload 
            onFileChange={handleFileChange} 
            file={file}
            showCard={false}
            title="Interview Data File"
            description="Select a JSON file with interview data or a text file with interview transcripts"
            showFileDetails={true}
            autoUpload={false}
          />
          
          <AnalysisOptions 
            provider={llmProvider} 
            onProviderChange={setLlmProvider} 
          />
          
          <div className="flex flex-col space-y-4 sm:flex-row sm:space-y-0 sm:space-x-4">
            <Button
              onClick={handleUpload}
              disabled={!file || loading}
              className="flex-1"
            >
              {loading && !uploadResponse ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload File
                </>
              )}
            </Button>
            
            <Button
              onClick={handleStartAnalysis}
              disabled={!uploadResponse || loading}
              variant="secondary"
              className="flex-1"
            >
              {loading && uploadResponse ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Starting Analysis...
                </>
              ) : (
                'Start Analysis'
              )}
            </Button>
          </div>
          
          {analysisResponse && (
            <AnalysisProgress analysisId={analysisResponse.result_id.toString()} />
          )}
          
          {error && (
            <div className="mt-4 p-4 border border-red-200 bg-red-50 text-red-600 rounded-md">
              {error}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};

export default UploadTab;
