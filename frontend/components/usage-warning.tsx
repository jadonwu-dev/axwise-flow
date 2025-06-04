"use client";

import React, { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { AlertTriangle, X, Zap } from 'lucide-react';
import { UpgradeModal } from './upgrade-modal';

interface UsageWarningProps {
  currentUsage: {
    analyses: number;
    prdGenerations: number;
  };
  limits: {
    analysesPerMonth: number;
    prdGenerationsPerMonth: number;
  };
  tier: string;
  className?: string;
}

export function UsageWarning({ 
  currentUsage, 
  limits, 
  tier,
  className = "" 
}: UsageWarningProps) {
  const [isDismissed, setIsDismissed] = useState(false);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  // Calculate usage percentages
  const analysesUsed = currentUsage.analyses;
  const analysesLimit = limits.analysesPerMonth;
  const remaining = Math.max(0, analysesLimit - analysesUsed);
  const usagePercentage = analysesLimit > 0 ? (analysesUsed / analysesLimit) * 100 : 0;

  // Determine warning level
  const isExhausted = remaining === 0;
  const isNearLimit = usagePercentage >= 80 && !isExhausted; // 80% threshold
  const isAtLimit = usagePercentage >= 90 && !isExhausted; // 90% threshold

  // Reset dismissal when usage changes significantly
  useEffect(() => {
    setIsDismissed(false);
  }, [isExhausted, isAtLimit, isNearLimit]);

  // Don't show warning if dismissed or if user has unlimited (Pro+ tiers)
  if (isDismissed || analysesLimit === 0 || (!isNearLimit && !isAtLimit && !isExhausted)) {
    return null;
  }

  const getWarningConfig = () => {
    if (isExhausted) {
      return {
        variant: 'destructive' as const,
        icon: <X className="h-4 w-4" />,
        title: 'Analysis limit reached',
        message: `You've used all ${analysesLimit} analyses this month. Upgrade to continue analyzing your customer research.`,
        actionText: 'Upgrade Now',
        showDismiss: false
      };
    }
    
    if (isAtLimit) {
      return {
        variant: 'destructive' as const,
        icon: <AlertTriangle className="h-4 w-4" />,
        title: 'Almost at your limit',
        message: `Only ${remaining} analysis${remaining === 1 ? '' : 'es'} remaining this month. Consider upgrading to avoid interruptions.`,
        actionText: 'Upgrade',
        showDismiss: true
      };
    }
    
    if (isNearLimit) {
      return {
        variant: 'default' as const,
        icon: <AlertTriangle className="h-4 w-4" />,
        title: 'Approaching your limit',
        message: `You have ${remaining} analysis${remaining === 1 ? '' : 'es'} remaining this month. Upgrade for unlimited access.`,
        actionText: 'View Plans',
        showDismiss: true
      };
    }

    return null;
  };

  const warningConfig = getWarningConfig();
  if (!warningConfig) return null;

  return (
    <>
      <Alert 
        variant={warningConfig.variant}
        className={`${className} ${isExhausted ? 'border-red-500 bg-red-50 dark:bg-red-950/20' : ''}`}
      >
        <div className="flex items-start justify-between w-full">
          <div className="flex items-start gap-3 flex-1">
            {warningConfig.icon}
            <div className="flex-1">
              <div className="font-semibold text-sm">
                {warningConfig.title}
              </div>
              <AlertDescription className="mt-1">
                {warningConfig.message}
              </AlertDescription>
            </div>
          </div>
          
          <div className="flex items-center gap-2 ml-4">
            <Button
              size="sm"
              variant={isExhausted ? "default" : "outline"}
              onClick={() => setShowUpgradeModal(true)}
              className="whitespace-nowrap"
            >
              <Zap className="h-3 w-3 mr-1" />
              {warningConfig.actionText}
            </Button>
            
            {warningConfig.showDismiss && (
              <Button
                size="sm"
                variant="ghost"
                onClick={() => setIsDismissed(true)}
                className="p-1 h-auto"
              >
                <X className="h-4 w-4" />
              </Button>
            )}
          </div>
        </div>
      </Alert>

      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        currentUsage={currentUsage}
        currentLimits={limits}
        trigger={isExhausted ? 'limit_reached' : 'warning'}
      />
    </>
  );
}

export default UsageWarning;
