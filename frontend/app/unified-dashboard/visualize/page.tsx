import { redirect } from 'next/navigation';

// Force dynamic rendering to ensure fresh data
export const dynamic = 'force-dynamic';

interface VisualizePageProps {
  searchParams: {
    analysisId?: string;
    visualizationTab?: string;
  };
}

/**
 * VisualizePage Component
 *
 * This page now redirects to the main dashboard with the analysisId parameter.
 * The main dashboard now serves as the visualization hub.
 */
export default function VisualizePage({ searchParams }: VisualizePageProps): never {
  const analysisId = searchParams.analysisId || '';
  const visualizationTab = searchParams.visualizationTab || 'themes';

  // Redirect to the main dashboard with the analysisId parameter
  const timestamp = Date.now();
  // Make sure we always have a visualization tab
  const tab = visualizationTab || 'themes';
  const redirectUrl = `/unified-dashboard?analysisId=${analysisId}&visualizationTab=${tab}&timestamp=${timestamp}`;

  return redirect(redirectUrl);
}