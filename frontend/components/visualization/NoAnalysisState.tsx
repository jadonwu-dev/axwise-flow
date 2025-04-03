'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileUp, ArrowRight } from 'lucide-react';
import { useRouter } from 'next/navigation';

/**
 * NoAnalysisState Component
 * 
 * Displays a helpful state when no analyses are available to visualize.
 * Guides the user to upload their first file.
 */
export function NoAnalysisState(): JSX.Element {
  const router = useRouter();
  
  const handleUploadClick = () => {
    router.push('/unified-dashboard/upload');
  };
  
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Welcome to the Analysis Dashboard</CardTitle>
        <CardDescription>
          Get started by uploading your first interview data file
        </CardDescription>
      </CardHeader>
      
      <CardContent className="flex flex-col items-center justify-center py-12">
        <div className="text-center max-w-md mx-auto">
          <div className="bg-muted rounded-full p-4 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <FileUp className="h-8 w-8 text-primary" />
          </div>
          
          <h3 className="text-xl font-semibold mb-2">No Analysis Results Yet</h3>
          
          <p className="text-muted-foreground mb-6">
            Upload your first interview data file to see insights, themes, patterns, and more.
            The dashboard will automatically display your most recent analysis results here.
          </p>
          
          <Button 
            onClick={handleUploadClick}
            className="gap-2"
          >
            Upload Your First File
            <ArrowRight className="h-4 w-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
