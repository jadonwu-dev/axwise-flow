'use client';

import { useRef, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { FileUp } from 'lucide-react';

interface FileUploadFormProps {
  file: File | null;
  onFileChange: (file: File, isText: boolean) => void;
}

/**
 * Component for handling file selection
 */
const FileUploadForm = ({ file, onFileChange }: FileUploadFormProps) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  // Handle file selection
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const selectedFile = e.target.files[0];
      
      // Check if it's a text file by MIME type or extension
      const isText = selectedFile.type === 'text/plain' || 
                     selectedFile.name.endsWith('.txt') ||
                     selectedFile.name.endsWith('.text');
      
      onFileChange(selectedFile, isText);
    }
  };

  // Handle button click to trigger file input
  const handleButtonClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex flex-col space-y-2">
        <Label htmlFor="file-upload">Interview Data File</Label>
        <p className="text-sm text-muted-foreground">
          Select a JSON file with interview data or a text file with interview transcripts
        </p>
      </div>
      
      <div className="flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-md">
        <input
          id="file-upload"
          type="file"
          accept=".json,.txt,.text"
          className="hidden"
          onChange={handleFileChange}
          ref={fileInputRef}
        />
        
        <div className="flex flex-col items-center text-center">
          <FileUp className="h-10 w-10 text-muted-foreground mb-2" />
          <p className="mb-2 text-sm font-semibold">
            {file ? file.name : 'Click to upload or drag and drop'}
          </p>
          <p className="text-xs text-muted-foreground">
            JSON or TXT files only (max 10MB)
          </p>
        </div>
        
        <Button 
          onClick={handleButtonClick}
          variant="outline"
          className="mt-4"
        >
          Select File
        </Button>
      </div>
      
      {file && (
        <div className="text-sm flex items-center justify-between mt-2">
          <span>Selected file: <strong>{file.name}</strong></span>
          <span className="text-muted-foreground">
            {(file.size / 1024).toFixed(1)} KB
          </span>
        </div>
      )}
    </div>
  );
};

export default FileUploadForm;
