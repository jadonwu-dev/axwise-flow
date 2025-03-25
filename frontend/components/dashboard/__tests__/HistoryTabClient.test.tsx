import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import HistoryTabClient from '../HistoryTabClient';
import { DetailedAnalysisResult, SentimentData, SentimentOverview } from '@/types/api';
import { useRouter } from 'next/navigation';

// Mock Next.js navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn().mockReturnValue({
    push: vi.fn(),
    refresh: vi.fn()
  })
}));

// Mock toast provider
vi.mock('@/components/providers/toast-provider', () => ({
  useToast: () => ({
    showToast: vi.fn()
  })
}));

// Mock the analysis store
vi.mock('@/store/useAnalysisStore', () => ({
  useAnalysisStore: {
    setState: vi.fn(),
    getState: () => ({
      fetchAnalysisById: vi.fn()
    })
  }
}));

describe('HistoryTabClient', () => {
  const mockSentimentOverview: SentimentOverview = {
    positive: 30,
    negative: 20,
    neutral: 50
  };
  
  const mockAnalyses: DetailedAnalysisResult[] = [
    {
      id: '1',
      fileName: 'Test Analysis 1',
      createdAt: '2024-03-25T12:00:00Z',
      status: 'completed',
      themes: [],
      patterns: [],
      sentiment: [] as SentimentData[],
      sentimentOverview: mockSentimentOverview,
      personas: []
    },
    {
      id: '2',
      fileName: 'Test Analysis 2',
      createdAt: '2024-03-24T12:00:00Z',
      status: 'pending',
      themes: [],
      patterns: [],
      sentiment: [] as SentimentData[],
      sentimentOverview: mockSentimentOverview,
      personas: []
    },
  ];

  it('renders the history tab with analyses', () => {
    render(
      <HistoryTabClient
        initialAnalyses={mockAnalyses}
        sortBy="date"
        sortDirection="desc"
        filterStatus="all"
      />
    );

    // Check for the card title
    expect(screen.getByText('Analysis History')).toBeInTheDocument();
    
    // Check for both analyses
    expect(screen.getByText('Test Analysis 1')).toBeInTheDocument();
    expect(screen.getByText('Test Analysis 2')).toBeInTheDocument();
  });

  it('displays empty state when no analyses are available', () => {
    render(
      <HistoryTabClient
        initialAnalyses={[]}
        sortBy="date"
        sortDirection="desc"
        filterStatus="all"
      />
    );

    expect(screen.getByText('No analyses found')).toBeInTheDocument();
    expect(
      screen.getByText("You haven't performed any analyses yet or none match your current filters.")
    ).toBeInTheDocument();
  });

  it('navigates to visualization when clicking on an analysis', () => {
    const pushMock = vi.fn();
    (useRouter as jest.Mock).mockReturnValue({
      push: pushMock,
      refresh: vi.fn()
    });

    render(
      <HistoryTabClient
        initialAnalyses={mockAnalyses}
        sortBy="date"
        sortDirection="desc"
        filterStatus="all"
      />
    );

    // Find and click the View button on the first analysis
    const viewButton = screen.getAllByText('View')[0];
    fireEvent.click(viewButton);

    // Expect navigation to visualization page with the correct analysis ID
    expect(pushMock).toHaveBeenCalledWith(expect.stringContaining('/unified-dashboard/visualize?analysisId=1'));
  });
}); 