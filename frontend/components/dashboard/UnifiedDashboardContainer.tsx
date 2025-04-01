'use client';

import { DashboardAuthProvider } from './containers/DashboardAuthProvider';
// Removed imports for non-existent components
// import { DashboardDataProvider } from './containers/DashboardDataProvider';
// import { DashboardTabsContainer } from './containers/DashboardTabsContainer';
import DashboardTabs from './DashboardTabs'; // Corrected import path

/**
 * Main container component for the unified dashboard
 * This component now follows Single Responsibility Principle and orchestrates:
 * - Authentication via DashboardAuthProvider
 * - UI and tab management via DashboardTabsContainer (Reverted to DashboardTabs)
 */
const UnifiedDashboardContainer = (): JSX.Element => { 
  return (
    <DashboardAuthProvider>
      {/* Removed DashboardDataProvider wrapper */}
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Interview Analysis Dashboard</h1>
        {/* Render DashboardTabs directly, passing null for dashboardData */}
        <DashboardTabs dashboardData={null} /> 
      </div>
    </DashboardAuthProvider>
  );
};

export default UnifiedDashboardContainer;
