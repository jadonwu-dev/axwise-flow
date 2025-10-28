'use client';

import { useState, useEffect } from 'react';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { getSubscriptionInfo, resetSubscription } from '@/lib/api/subscription';
import { useToast } from '@/components/providers/toast-provider';
import { RefreshCw } from 'lucide-react';

interface SubscriptionInfo {
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

export function SubscriptionStatus() {
  const [subscription, setSubscription] = useState<SubscriptionInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [resetting, setResetting] = useState(false);
  const { showToast } = useToast();
  // OSS mode: no Clerk user available
  // Check if we're in development mode to show debug tools
  const isDevelopment = typeof window !== 'undefined' && window.location.hostname === 'localhost';
  const showDebugTools = isDevelopment;

  const fetchSubscriptionInfo = async () => {
    try {
      setLoading(true);
      const info = await getSubscriptionInfo();
      setSubscription(info);
    } catch (error) {
      console.error('Error fetching subscription info:', error);
      setSubscription(null);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    try {
      setResetting(true);
      await resetSubscription();
      showToast('Subscription reset successfully', { variant: 'success' });
      await fetchSubscriptionInfo(); // Refresh the info
    } catch (error) {
      console.error('Error resetting subscription:', error);
      showToast('Failed to reset subscription', { variant: 'error' });
    } finally {
      setResetting(false);
    }
  };

  useEffect(() => {
    fetchSubscriptionInfo();

    // Set up periodic refresh every 10 seconds to catch subscription updates
    const interval = setInterval(fetchSubscriptionInfo, 10000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center gap-2">
        <Badge variant="outline" className="animate-pulse">
          Loading...
        </Badge>
      </div>
    );
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500 text-white';
      case 'trialing':
        return 'bg-blue-500 text-white';
      case 'canceled':
        return 'bg-red-500 text-white';
      case 'past_due':
        return 'bg-yellow-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'pro':
        return 'bg-purple-500 text-white';
      case 'starter':
        return 'bg-blue-500 text-white';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  // Helper function to format usage display for analyses (used/total)
  const formatAnalysesUsage = (used: number, limit: number) => {
    return `${used}/${limit} analyses`;
  };

  return (
    <div className="flex items-center gap-2">
      {subscription && subscription.tier && subscription.status ? (
        <>
          <Badge className={getTierColor(subscription.status === 'trialing' ? 'pro' : subscription.tier)}>
            {subscription.status === 'trialing' ? 'Pro' : subscription.tier.charAt(0).toUpperCase() + subscription.tier.slice(1)}
          </Badge>
          <Badge className={getStatusColor(subscription.status)}>
            {subscription.status === 'trialing' ? 'Trial' : subscription.status}
          </Badge>

          {/* Usage counter - only show analyses */}
          {subscription.limits && subscription.currentUsage && (
            <div className="hidden lg:flex items-center gap-2 text-xs text-muted-foreground">
              <span>
                {formatAnalysesUsage(
                  subscription.currentUsage.analyses || 0,
                  subscription.limits.analysesPerMonth || 0
                )}
              </span>
            </div>
          )}

          {subscription.trialEnd && (
            <span className="text-xs text-muted-foreground hidden md:block">
              Trial ends: {new Date(subscription.trialEnd * 1000).toLocaleDateString()}
            </span>
          )}
        </>
      ) : (
        <Badge variant="outline">
          Free
        </Badge>
      )}

      {/* Admin debug tools */}
      {showDebugTools && (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="sm"
            onClick={fetchSubscriptionInfo}
            disabled={loading}
            className="text-xs px-2 py-1 h-6"
            title="Refresh subscription status"
          >
            <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={handleReset}
            disabled={resetting}
            className="text-xs px-2 py-1 h-6"
            title="Reset subscription (Admin only)"
          >
            {resetting ? 'Resetting...' : 'Reset'}
          </Button>
        </div>
      )}
    </div>
  );
}
