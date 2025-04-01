'use client';

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import UploadTab from '../UploadTab';
import { apiClient } from '@/lib/apiClient';
import { vi } from 'vitest';
import type { UploadResponse, AnalysisResponse } from '@/types/api'; // Import response types

// Mock the toast provider
vi.mock('@/components/providers/toast-provider', () => ({
  useToast: () => ({
    showToast: vi.fn()
  })
}));

// Mock the API client
vi.mock('@/lib/apiClient', () => ({
  apiClient: {
    setAuthToken: vi.fn(),
    uploadData: vi.fn(),
    analyzeData: vi.fn()
  }
}));

// Mock the FileUpload component
vi.mock('@/components/FileUpload', () => ({
  FileUpload: ({ onFileChange }: { onFileChange: (file: File, isText: boolean) => void }) => (
    <div data-testid="file-upload">
      <button 
        onClick={() => onFileChange(new File(['test'], 'test.txt', { type: 'text/plain' }), true)}
        data-testid="select-file-btn"
      >
        Select File
      </button>
    </div>
  )
}));

// Mock AnalysisOptions component
vi.mock('../AnalysisOptions', () => ({
  __esModule: true,
  default: ({ onProviderChange }: { onProviderChange: (provider: 'openai' | 'gemini') => void }) => (
    <div data-testid="analysis-options">
      <button 
        onClick={() => onProviderChange('openai')}
        data-testid="select-openai-btn"
      >
        Select OpenAI
      </button>
    </div>
  )
}));

// Mock AnalysisProgress component
vi.mock('@/components/AnalysisProgress', () => ({
  __esModule: true,
  default: ({ analysisId }: { analysisId: string }) => (
    <div data-testid="analysis-progress">Analysis ID: {analysisId}</div>
  )
}));

describe('UploadTab', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('renders the upload form', () => {
    render(<UploadTab />);
    
    expect(screen.getByText(/upload interview data/i)).toBeInTheDocument();
    expect(screen.getByTestId('file-upload')).toBeInTheDocument();
    expect(screen.getByTestId('analysis-options')).toBeInTheDocument();
  });
  
  it('updates state when a file is selected', () => {
    render(<UploadTab />);
    
    // The upload button should be disabled initially (no file selected)
    const uploadButton = screen.getByRole('button', { name: /upload/i });
    expect(uploadButton).toBeDisabled();
    
    // Select a file
    fireEvent.click(screen.getByTestId('select-file-btn'));
    
    // Now the upload button should be enabled
    expect(uploadButton).toBeEnabled(); // Use toBeEnabled()
  });
  
  it('calls the API client when uploading a file', async () => {
    // Mock successful upload response
    vi.mocked(apiClient.uploadData).mockResolvedValue({ 
// Use vi.mocked and ensure type matches UploadResponse
      data_id: 123,
      filename: 'test.txt',
      status: 'success', // Correct status
      upload_date: new Date().toISOString() // Add missing property
    });
    
    render(<UploadTab />);
    
    // Select a file
    fireEvent.click(screen.getByTestId('select-file-btn'));
    
    // Click upload
    fireEvent.click(screen.getByRole('button', { name: /upload/i }));
    
    // Check that the API was called
    await waitFor(() => {
      expect(apiClient.uploadData).toHaveBeenCalled();
    });
  });
  
  it('enables start analysis button after successful upload', async () => {
    // Mock successful upload response
    vi.mocked(apiClient.uploadData).mockResolvedValue({ 
// Use vi.mocked and ensure type matches UploadResponse
      data_id: 123,
      filename: 'test.txt',
      status: 'success', // Correct status
      upload_date: new Date().toISOString() // Add missing property
    });
    
    render(<UploadTab />);
    
    // Select a file
    fireEvent.click(screen.getByTestId('select-file-btn'));
    
    // Upload button should be enabled, start analysis should be disabled
    expect(screen.getByRole('button', { name: /upload/i })).toBeEnabled(); // Use toBeEnabled()
    expect(screen.getByRole('button', { name: /start analysis/i })).toBeDisabled();
    
    // Click upload
    fireEvent.click(screen.getByRole('button', { name: /upload/i }));
    
    // After upload, start analysis should be enabled
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /start analysis/i })).toBeEnabled(); // Use toBeEnabled()
    });
  });
  
  it('shows progress when analysis is started', async () => {
    // Mock successful upload response
    vi.mocked(apiClient.uploadData).mockResolvedValue({ 
// Use vi.mocked and ensure type matches UploadResponse
      data_id: 123,
      filename: 'test.txt',
      status: 'success', // Correct status
      upload_date: new Date().toISOString() // Add missing property
    });
    
    // Mock successful analysis response
    vi.mocked(apiClient.analyzeData).mockResolvedValue({ 
// Use vi.mocked and ensure type matches AnalysisResponse
      result_id: 456, // Correct type (number)
      status: 'started', // Correct status
      message: 'Analysis started' // Add missing property
    });
    
    render(<UploadTab />);
    
    // Select a file and upload it
    fireEvent.click(screen.getByTestId('select-file-btn'));
    fireEvent.click(screen.getByRole('button', { name: /upload/i }));
    
    // Wait for upload to complete
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /start analysis/i })).toBeEnabled(); // Use toBeEnabled()
    });
    
    // Start analysis
    fireEvent.click(screen.getByRole('button', { name: /start analysis/i }));
    
    // Check that progress is shown
    await waitFor(() => {
      // Wait for progress element
      expect(screen.getByTestId('analysis-progress')).toBeInTheDocument();
 
    });
    // Assert text content outside waitFor
    expect(screen.getByText(/analysis id: 456/i)).toBeInTheDocument();
  });
});
