/**
 * UnifiedDashboard Component (Server Component)
 *
 * ARCHITECTURAL NOTE: This is the server component implementation of the dashboard.
 * It now serves as the main visualization hub, showing the most recent analysis by default.
 * If an analysisId is provided, it shows that specific analysis instead.
 */

import { redirect } from 'next/navigation';
import { Suspense } from 'react';
import VisualizationTabs from '@/components/visualization/VisualizationTabs';
import Loading from './visualize/loading';
import { getServerSideAnalysis, getLatestCompletedAnalysis } from '@/app/actions';
import { NoAnalysisState } from '@/components/visualization/NoAnalysisState';

// Force dynamic rendering to ensure fresh data
export const dynamic = 'force-dynamic';

interface PageProps {
  searchParams?: {
    tab?: string;
    analysisId?: string;
    visualizationTab?: string;
  };
}

export default async function UnifiedDashboard({ searchParams }: PageProps): Promise<JSX.Element> {
  // Get the requested tab from URL parameters
  const tab = searchParams?.tab || null;
  const analysisId = searchParams?.analysisId || null;

  // If a specific tab is requested, redirect to that tab
  if (tab === 'upload') {
    redirect('/unified-dashboard/upload');
  } else if (tab === 'history') {
    redirect('/unified-dashboard/history');
  } else if (tab === 'documentation') {
    redirect('/unified-dashboard/documentation');
  }

  // If we reach here, we're either showing the main dashboard or a specific analysis

  // If an analysisId is provided, fetch that specific analysis
  if (analysisId) {
    const analysisData = await getServerSideAnalysis(analysisId);
    const visualizationTab = searchParams?.visualizationTab || null;

    return (
      <Suspense fallback={<Loading />}>
        <VisualizationTabs
          analysisId={analysisId}
          analysisData={analysisData}
          initialTab={visualizationTab}
        />
      </Suspense>
    );
  }

  // Otherwise, fetch the most recent completed analysis
  const latestAnalysis = await getLatestCompletedAnalysis();

  if (latestAnalysis) {
    // If we have a latest analysis, show it
    const visualizationTab = searchParams?.visualizationTab || null;

    return (
      <Suspense fallback={<Loading />}>
        <VisualizationTabs
          analysisId={latestAnalysis.id}
          analysisData={latestAnalysis}
          initialTab={visualizationTab}
        />
      </Suspense>
    );
  } else {
    // If no analyses are available, show a helpful state
    return <NoAnalysisState />;
  }
}