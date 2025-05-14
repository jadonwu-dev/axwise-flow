/**
 * File upload methods for the API client
 */

import { apiCore } from './core';
import { UploadResponse } from './types';

/**
 * Upload data to the API
 * 
 * @param file The file to upload
 * @param isTextFile Whether the file is a text file (default: false)
 * @returns A promise that resolves to the upload response
 */
export async function uploadData(file: File, isTextFile: boolean = false): Promise<UploadResponse> {
  try {
    // Log the request data for debugging
    console.log('Uploading file:', {
      filename: file.name,
      type: file.type,
      size: file.size,
      isTextFile
    });

    const formData = new FormData();
    formData.append('file', file);

    // Convert boolean to string representation expected by the backend
    formData.append('is_free_text', String(isTextFile));

    // Add additional data that might be required by the backend
    formData.append('filename', file.name);
    formData.append('content_type', file.type);

    const response = await apiCore.getClient().post<UploadResponse>('/api/data', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Accept': 'application/json',
      },
      // Increase timeout significantly for potentially large files and initial processing
      timeout: 180000, // 180 seconds (increased from 60)
    });

    console.log('Upload response:', response.data);
    return response.data;
  } catch (error: any) {
    console.error('Error uploading data:', error);

    // Enhanced error debugging
    if (error?.response?.data?.detail) {
      console.error('Server error details:', error.response.data.detail);
    }

    // Handle different error types safely
    if (error && error.response) {
      // Handle 401 separately as it's typically an auth issue
      if (error.response.status === 401) {
        throw new Error('Authentication required. Please log in.');
      }

      // Handle 422 errors specifically for better feedback
      if (error.response.status === 422) {
        const errorDetail = error.response.data?.detail;
        if (Array.isArray(errorDetail) && errorDetail.length > 0) {
          // Handle FastAPI validation error format
          const validationErrors = errorDetail.map((err: any) =>
            `${err.loc.join('.')}: ${err.msg}`
          ).join(', ');
          throw new Error(`Validation error: ${validationErrors}`);
        } else if (typeof errorDetail === 'string') {
          throw new Error(`Validation error: ${errorDetail}`);
        } else {
          throw new Error('The server could not process your request. Please check your file format.');
        }
      }

      // Use the server error message if available
      const errorResponse = error.response.data as { detail?: string };
      if (errorResponse?.detail) {
        throw new Error(errorResponse.detail);
      }
    }

    // Generic error with a safe message access
    const errorMessage = error && typeof error.message === 'string'
      ? error.message
      : 'Unknown error';
    throw new Error(`Upload failed: ${errorMessage}`);
  }
}
