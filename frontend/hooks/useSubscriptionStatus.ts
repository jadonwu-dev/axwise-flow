'use client';

import { useState, useEffect } from 'react';
import { getSubscriptionInfo } from '@/lib/api/subscription';

export interface SubscriptionInfo {
  tier: string;
  status: string;
  current_period_end?: string;
  trial_end?: string;
  cancel_at_period_end?: boolean;
  limits?: {
    analysesPerMonth?: number;
    prdGenerationsPerMonth?: number;
  };
  currentUsage?: {
    analyses?: number;
    prdGenerations?: number;
  };
  canPerformAnalysis?: boolean;
  canGeneratePRD?: boolean;
}

export function useSubscriptionStatus() {
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSubscriptionInfo = async (isInitialLoad = false) => {
    try {
      // Only show loading spinner on initial load, not on background refreshes
      if (isInitialLoad) {
        setLoading(true);
      }
      setError(null);
      const info = await getSubscriptionInfo();
      setSubscription(info);
    } catch (error) {
      console.error('Error fetching subscription info:', error);
      setError(error instanceof Error ? error.message : 'Failed to fetch subscription info');
      setSubscription(null);
    } finally {
      if (isInitialLoad) {
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    fetchSubscriptionInfo(true); // Initial load with loading state

    // Set up periodic refresh every 30 seconds (reduced frequency to prevent blinking)
    const interval = setInterval(() => fetchSubscriptionInfo(false), 30000);

    return () => clearInterval(interval);
  }, []);

  return {
    subscription,
    loading,
    error,
    refetch: fetchSubscriptionInfo
  };
}

export default useSubscriptionStatus;
