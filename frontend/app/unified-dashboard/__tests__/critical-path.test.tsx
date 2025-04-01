import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import EmergencyUploadPanel from '@/components/upload/EmergencyUploadPanel'; // Import the correct component

// Mock all dependencies
vi.mock('@/lib/apiClient', () => ({
  apiClient: {
    uploadData: vi.fn(),
    getAnalysisById: vi.fn(),
    setAuthToken: vi.fn()
  }
}));

vi.mock('@/components/FileUpload', () => ({
  FileUpload: () => (
    <div data-testid="file-upload">File Upload Component</div>
  )
}));

vi.mock('@/components/loading-spinner', () => ({
  LoadingSpinner: () => <div data-testid="loading-spinner">Loading...</div>
}));

vi.mock('@/components/providers/toast-provider', () => ({
  useToast: () => ({
    toast: vi.fn()
  })
}));

vi.mock('@/components/visualization/UnifiedVisualization', () => ({
  __esModule: true,
  default: () => <div data-testid="visualization">Visualization Component</div>
}));

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn()
  })
}));

describe('Unified Dashboard - Smoke Test', () => {
  it('renders the dashboard with upload step', () => {
    render(<EmergencyUploadPanel />); // Render the component with the UI
    
    // Check for file input using a more reliable method
    // Use getByTestId for the hidden input
    expect(screen.getByTestId('file-input')).toBeInTheDocument();
 
    
    // Check for the upload button
    expect(screen.getByRole('button', { name: 'Upload' })).toBeInTheDocument();
  });
}); 