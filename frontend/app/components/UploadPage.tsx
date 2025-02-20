'use client'

import React from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { FileUpload } from '@/components/FileUpload'

export default function UploadPage() {
  const handleUploadComplete = (dataId: number) => {
    // Handle successful upload (e.g., navigate to analysis page)
    console.log(`Upload completed. Data ID: ${dataId}`);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Upload Interview Data</CardTitle>
          <CardDescription>
            Upload your interview data in JSON format to begin analysis.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <FileUpload onUploadComplete={handleUploadComplete} />
        </CardContent>
      </Card>
    </div>
  )
}