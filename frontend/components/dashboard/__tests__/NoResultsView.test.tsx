'use client';

import { render, screen, fireEvent } from '@testing-library/react';
import NoResultsView from '../NoResultsView'; // Changed to default import
import { useRouter } from 'next/navigation';
import { vi } from 'vitest';

// Import type for router mock
import type { AppRouterInstance } from 'next/dist/shared/lib/app-router-context.shared-runtime';

// Mock Next.js navigation
const mockPush = vi.fn();
const mockReplace = vi.fn(); // Add mock
const mockRefresh = vi.fn(); // Add mock
const mockBack = vi.fn(); // Add mock
const mockForward = vi.fn(); // Add mock
const mockPrefetch = vi.fn(); // Add mock
const mockUseRouter = vi.fn((): AppRouterInstance => ({ // Return full AppRouterInstance
  push: mockPush,
  replace: mockReplace, // Add method
  refresh: mockRefresh, // Add method
  back: mockBack,       // Add method
  forward: mockForward, // Add method
  prefetch: mockPrefetch, // Add method
}));
vi.mock('next/navigation', () => ({
 useRouter: mockUseRouter }));

describe('NoResultsView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset router mock return value( if needed (already done globally)
    // vi.mocked(useRouter).mockReturnValue({ ... }) ;
  });

  it('renders the no results message', () => {
    render(<NoResultsView />);
    
    // Check that the component renders the expected message
    expect(screen.getByText(/no analysis results/i)).toBeInTheDocument();
    expect(screen.getByText(/you haven't analyzed any interview data yet/i)).toBeInTheDocument();
  });
  
  it('renders the FileQuestion icon', () => {
    render(<NoResultsView />);
    
    // Check that the component renders an icon (FileQuestion from Lucide)
    const icon = screen.getByText('', { selector: '.lucide-filequestion' });
    expect(icon).toBeInTheDocument();
  });

  it('navigates to upload tab when button is clicked', () => {
    // No need to mock router here as it's done globally and correctly typed now
    
    render(<NoResultsView />);
    
    // Click the Go to Upload button
    fireEvent.click(screen.getByRole('button', { name: /go to upload/i }));
    
    // Check that the router was called to navigate to upload tab
    expect(mockPush).toHaveBeenCalledWith('/unified-dashboard?tab=upload'); // Use the globally defined mockPush
  });
});
