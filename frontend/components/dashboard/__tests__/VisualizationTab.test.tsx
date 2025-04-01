'use client';

import { render, screen, fireEvent } from '@testing-library/react';
import VisualizationTabs from '../../visualization/VisualizationTabs'; // Corrected import path and name
import { useRouter, useSearchParams } from 'next/navigation';
import { DetailedAnalysisResult, AnalyzedTheme, Pattern, SentimentData, Persona } from '@/types/api'; // Import specific types
import { vi } from 'vitest';
import type { ReadonlyURLSearchParams } from 'next/navigation'; // Import type for mock
import type { AppRouterInstance } from 'next/dist/shared/lib/app-router-context.shared-runtime'; // Import type for mock


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

const mockGet = vi.fn();
const mockUseSearchParams = vi.fn((): Partial<ReadonlyURLSearchParams> => ({ // Return Partial<ReadonlyURLSearchParams>
  get: mockGet,
}));

vi.mock('next/navigation', () => ({
  useRouter: mockUseRouter,
  useSearchParams: mockUseSearchParams,
}));


// Mock the visualization components (These are children of VisualizationTabs)
vi.mock('@/components/visualization/ThemeChart', () => ({
  ThemeChart: ({ themes }: { themes: AnalyzedTheme[] }) => ( // Use AnalyzedTheme[]
    <div data-testid="theme-chart">
      {themes.length} themes found
    </div>
  )
}));

vi.mock('@/components/visualization/PatternList', () => ({
  PatternList: ({ patterns }: { patterns: Pattern[] }) => ( // Use Pattern[]
    <div data-testid="pattern-list">
      {patterns.length} patterns found
    </div>
  )
}));

vi.mock('@/components/visualization/SentimentGraph', () => ({
  // SentimentGraph expects 'data' (SentimentOverview) and 'supportingStatements'
  SentimentGraph: ({ data }: { data: any }) => ( // Keep any for now, adjust if SentimentOverview is simple
    <div data-testid="sentiment-graph">
      {data?.positive || 0} positive points
    </div>
  )
}));

vi.mock('@/components/visualization/PersonaCards', () => ({
  PersonaCards: ({ personas }: { personas: Persona[] }) => ( // Use Persona[]
    <div data-testid="persona-cards">
      {personas.length} personas identified
    </div>
  )
}));

// Mock sample analysis data - Corrected structure
const mockAnalysis: DetailedAnalysisResult = {
  id: '123', // Corrected from result_id
  status: 'completed',
  createdAt: '2023-01-01T00:00:00Z', // Corrected from created_at
  fileName: 'test-interview.txt', // Moved from metadata
  fileSize: 1024, // Moved from metadata
  themes: [{ id: 1, name: 'Theme 1', frequency: 0.5, keywords: [], sentiment: 0.5 }], // Use Theme type structure
  patterns: [{ id: 'p1', name: 'Pattern 1', count: 2, frequency: 0.4 }], // Use Pattern type structure
  sentiment: [{ timestamp: '2023-01-01T00:01:00Z', score: 0.7, text: 'Positive' }], // Use SentimentData[]
  sentimentOverview: { positive: 0.7, neutral: 0.2, negative: 0.1 }, // Added
  personas: [{ name: 'Persona 1', description: 'Desc 1', role_context: { value: '', confidence: 0, evidence: [] }, key_responsibilities: { value: '', confidence: 0, evidence: [] }, tools_used: { value: '', confidence: 0, evidence: [] }, collaboration_style: { value: '', confidence: 0, evidence: [] }, analysis_approach: { value: '', confidence: 0, evidence: [] }, pain_points: { value: '', confidence: 0, evidence: [] }, patterns: [], confidence: 0.8, evidence: [] }], // Use Persona[] structure
  // Removed updated_at, summary, metadata, sentiments, user_personas
};


describe('VisualizationTabs', () => { // Updated describe block name
  // Reset mocks before each test
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset router mock return value if needed
    // vi.mocked(useRouter).mockReturnValue({ ... }); 
    // Set default search param mock for 'vizTab'
    vi.mocked(mockGet).mockImplementation((key: string) => key === 'vizTab' ? 'themes' : null);
  });

  it('renders visualization options when analysis is provided', () => {
    // Pass required props to VisualizationTabs
    render(<VisualizationTabs analysisId={mockAnalysis.id} analysisData={mockAnalysis} />); 
    
    // Check that visualization options are rendered
    expect(screen.getByRole('tab', { name: /themes/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /patterns/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /sentiment/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /personas/i })).toBeInTheDocument();
    expect(screen.getByRole('tab', { name: /summary/i })).toBeInTheDocument();
  });

  it('sets the active visualization tab based on URL parameter', () => {
    render(<VisualizationTabs analysisId={mockAnalysis.id} analysisData={mockAnalysis} />);
    
    // The 'themes' tab should be active based on our mock URL params
    const themesTab = screen.getByRole('tab', { name: /themes/i });
    expect(themesTab).toHaveAttribute('data-state', 'active');
    
    // Theme chart should be visible
    expect(screen.getByTestId('theme-chart')).toBeInTheDocument();
    expect(screen.getByText('1 themes found')).toBeInTheDocument(); // Adjusted based on mock data
  });

  it('changes visualization tab when clicked', () => {
    // No need to mock router here as it's done globally
    render(<VisualizationTabs analysisId={mockAnalysis.id} analysisData={mockAnalysis} />);
    
    // Click the Patterns tab
    fireEvent.click(screen.getByRole('tab', { name: /patterns/i }));
    
    // Check that the router was called to update the URL
    // Note: The component updates URL via router.push, check the mock
    expect(mockPush).toHaveBeenCalledWith('?vizTab=patterns'); 
  });

  it('displays theme chart when themes tab is active', () => {
    vi.mocked(mockGet).mockImplementation((key: string) => key === 'vizTab' ? 'themes' : null);
    
    render(<VisualizationTabs analysisId={mockAnalysis.id} analysisData={mockAnalysis} />);
    
    expect(screen.getByTestId('theme-chart')).toBeInTheDocument();
  });

  it('displays pattern list when patterns tab is active', () => {
    vi.mocked(mockGet).mockImplementation((key: string) => key === 'vizTab' ? 'patterns' : null);
    
    render(<VisualizationTabs analysisId={mockAnalysis.id} analysisData={mockAnalysis} />);
    
    expect(screen.getByTestId('pattern-list')).toBeInTheDocument();
  });

  it('displays sentiment graph when sentiment tab is active', () => {
    vi.mocked(mockGet).mockImplementation((key: string) => key === 'vizTab' ? 'sentiment' : null);
    
    render(<VisualizationTabs analysisId={mockAnalysis.id} analysisData={mockAnalysis} />);
    
    expect(screen.getByTestId('sentiment-graph')).toBeInTheDocument();
  });

  it('displays persona cards when personas tab is active', () => {
    vi.mocked(mockGet).mockImplementation((key: string) => key === 'vizTab' ? 'personas' : null);
    
    render(<VisualizationTabs analysisId={mockAnalysis.id} analysisData={mockAnalysis} />);
    
    expect(screen.getByTestId('persona-cards')).toBeInTheDocument();
  });

  it('displays summary when summary tab is active', () => {
    vi.mocked(mockGet).mockImplementation((key: string) => key === 'vizTab' ? 'summary' : null);
    
    render(<VisualizationTabs analysisId={mockAnalysis.id} analysisData={mockAnalysis} />);
    
    // Assuming the summary is rendered directly or within a specific element
    // expect(screen.getByText('Test summary of the analysis')).toBeInTheDocument(); // Summary removed from mock
    // Check for a generic summary container or text if applicable
    expect(screen.getByRole('tabpanel', { name: /summary/i })).toBeInTheDocument(); 
  });
});
