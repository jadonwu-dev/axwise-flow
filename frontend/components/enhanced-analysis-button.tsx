"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui/tooltip';
import { Play, Lock, Zap, AlertTriangle } from 'lucide-react';
import { UpgradeModal } from './upgrade-modal';

interface EnhancedAnalysisButtonProps {
  onAnalyze: () => void;
  disabled?: boolean;
  loading?: boolean;
  canPerformAnalysis?: boolean;
  currentUsage?: {
    analyses: number;
    prdGenerations: number;
  };
  limits?: {
    analysesPerMonth: number;
    prdGenerationsPerMonth: number;
  };
  tier?: string;
  className?: string;
  size?: "default" | "sm" | "lg" | "icon";
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link";
}

export function EnhancedAnalysisButton({
  onAnalyze,
  disabled = false,
  loading = false,
  canPerformAnalysis = true,
  currentUsage,
  limits,
  tier = "free",
  className = "",
  size = "default",
  variant = "default"
}: EnhancedAnalysisButtonProps) {
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  // Calculate remaining analyses
  const remaining = limits && currentUsage 
    ? Math.max(0, limits.analysesPerMonth - currentUsage.analyses)
    : 0;

  const isLimitReached = !canPerformAnalysis && limits && currentUsage 
    ? currentUsage.analyses >= limits.analysesPerMonth
    : false;

  const isNearLimit = limits && currentUsage && limits.analysesPerMonth > 0
    ? (currentUsage.analyses / limits.analysesPerMonth) >= 0.8
    : false;

  // Determine button state and messaging
  const getButtonConfig = () => {
    if (loading) {
      return {
        disabled: true,
        icon: <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current" />,
        text: 'Analyzing...',
        tooltip: 'Analysis in progress...',
        showUpgradeOnClick: false
      };
    }

    if (disabled) {
      return {
        disabled: true,
        icon: <Play className="h-4 w-4" />,
        text: 'Run Analysis',
        tooltip: 'Please select data to analyze',
        showUpgradeOnClick: false
      };
    }

    if (isLimitReached) {
      return {
        disabled: true,
        icon: <Lock className="h-4 w-4" />,
        text: 'Limit Reached',
        tooltip: `You've used all ${limits?.analysesPerMonth} analyses this month. Upgrade to continue.`,
        showUpgradeOnClick: true,
        variant: 'outline' as const
      };
    }

    if (isNearLimit && remaining <= 1) {
      return {
        disabled: false,
        icon: <AlertTriangle className="h-4 w-4" />,
        text: `Run Analysis (${remaining} left)`,
        tooltip: `This is your last analysis this month. Consider upgrading for unlimited access.`,
        showUpgradeOnClick: false,
        variant: 'outline' as const
      };
    }

    if (isNearLimit) {
      return {
        disabled: false,
        icon: <Play className="h-4 w-4" />,
        text: `Run Analysis (${remaining} left)`,
        tooltip: `You have ${remaining} analyses remaining this month.`,
        showUpgradeOnClick: false
      };
    }

    return {
      disabled: false,
      icon: <Play className="h-4 w-4" />,
      text: 'Run Analysis',
      tooltip: 'Start analyzing your customer research data',
      showUpgradeOnClick: false
    };
  };

  const buttonConfig = getButtonConfig();

  const handleClick = () => {
    if (buttonConfig.showUpgradeOnClick) {
      setShowUpgradeModal(true);
    } else if (!buttonConfig.disabled) {
      onAnalyze();
    }
  };

  const ButtonComponent = (
    <Button
      onClick={handleClick}
      disabled={buttonConfig.disabled && !buttonConfig.showUpgradeOnClick}
      size={size}
      variant={buttonConfig.variant || variant}
      className={`${className} ${isLimitReached ? 'cursor-pointer' : ''}`}
    >
      {buttonConfig.icon}
      <span className="ml-2">{buttonConfig.text}</span>
      {buttonConfig.showUpgradeOnClick && (
        <Zap className="h-3 w-3 ml-1" />
      )}
    </Button>
  );

  return (
    <>
      <TooltipProvider>
        <Tooltip>
          <TooltipTrigger asChild>
            {ButtonComponent}
          </TooltipTrigger>
          <TooltipContent>
            <p>{buttonConfig.tooltip}</p>
            {buttonConfig.showUpgradeOnClick && (
              <p className="text-xs mt-1 text-muted-foreground">
                Click to view upgrade options
              </p>
            )}
          </TooltipContent>
        </Tooltip>
      </TooltipProvider>

      <UpgradeModal
        isOpen={showUpgradeModal}
        onClose={() => setShowUpgradeModal(false)}
        currentUsage={currentUsage}
        currentLimits={limits}
        trigger="limit_reached"
      />
    </>
  );
}

export default EnhancedAnalysisButton;
