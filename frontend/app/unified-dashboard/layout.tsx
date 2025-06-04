/**
 * UnifiedDashboard Layout Component
 *
 * ARCHITECTURAL NOTE: This layout component removes Zustand dependencies by using
 * URL parameters for tab navigation instead of client-side state.
 *
 * Updated to make the main dashboard the visualization hub that shows the latest analysis.
 */

'use client';

import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { UsageWarning } from '@/components/usage-warning';
import { useSubscriptionStatus } from '@/hooks/useSubscriptionStatus';

import type { ReactNode } from 'react';

export default function UnifiedDashboardLayout({
  children,
}: {
  children: ReactNode;
}): JSX.Element {
  // Get the current path to determine active tab
  const pathname = usePathname();

  // Get subscription status for usage warnings
  const { subscription, loading: subscriptionLoading } = useSubscriptionStatus();

  // Determine active tab based on pathname
  let activeTab = 'dashboard';
  if (pathname?.includes('/upload')) {
    activeTab = 'upload';
  } else if (pathname?.includes('/history')) {
    activeTab = 'history';
  } else if (pathname?.includes('/documentation')) {
    activeTab = 'documentation';
  }

  return (
    <div className="w-full mb-8">
      <Tabs value={activeTab} className="w-full mb-8">
        <TabsList className="w-full grid grid-cols-4">
          <TabsTrigger value="dashboard" asChild>
            <Link href="/unified-dashboard">
              Dashboard
            </Link>
          </TabsTrigger>

          <TabsTrigger value="upload" asChild>
            <Link href="/unified-dashboard/upload">
              Upload
            </Link>
          </TabsTrigger>

          <TabsTrigger value="history" asChild>
            <Link href="/unified-dashboard/history">
              History
            </Link>
          </TabsTrigger>

          <TabsTrigger value="documentation" asChild>
            <Link href="/unified-dashboard/documentation">
              Documentation
            </Link>
          </TabsTrigger>
        </TabsList>

        {/* Usage Warning - Show when subscription data is available */}
        {!subscriptionLoading && subscription && subscription.limits && subscription.currentUsage && (
          <div className="mt-4">
            <UsageWarning
              currentUsage={{
                analyses: subscription.currentUsage.analyses || 0,
                prdGenerations: subscription.currentUsage.prdGenerations || 0
              }}
              limits={{
                analysesPerMonth: subscription.limits.analysesPerMonth || 0,
                prdGenerationsPerMonth: subscription.limits.prdGenerationsPerMonth || 0
              }}
              tier={subscription.tier}
            />
          </div>
        )}

        <div className="mt-6">
          {children}
        </div>
      </Tabs>


    </div>
  );
}
