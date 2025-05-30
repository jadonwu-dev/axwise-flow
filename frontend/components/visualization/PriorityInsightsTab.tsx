'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AlertCircle, AlertTriangle, CheckCircle, RefreshCw } from 'lucide-react';
import { apiClient } from '@/lib/apiClient';
import { LoadingSpinner } from '@/components/loading-spinner';
import type { PriorityInsightsResponse, PrioritizedInsight } from '@/types/api';

interface PriorityInsightsTabProps {
  analysisId: string | null;
}

interface PatternOriginal {
  evidence?: string[];
  [key: string]: any;
}

interface ThemeOriginal {
  statements?: string[];
  [key: string]: any;
}

type PrioritizedInsightWithOriginal = PrioritizedInsight & {
  original: PatternOriginal | ThemeOriginal;
};

export function PriorityInsightsTab({ analysisId }: PriorityInsightsTabProps) {
  console.log('[PriorityInsightsTab] Component rendered with analysisId:', analysisId);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [priorityData, setPriorityData] = useState<PriorityInsightsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  useEffect(() => {
    console.log('[PriorityInsightsTab] useEffect triggered with analysisId:', analysisId);

    if (!analysisId) {
      console.log('[PriorityInsightsTab] No analysisId provided, setting error');
      setLoading(false);
      setError('No analysis ID provided');
      return;
    }

    const fetchPriorityData = async () => {
      try {
        console.log('[PriorityInsightsTab] Starting fetchPriorityData');
        setLoading(true);
        setError(null);

        console.log(`[PriorityInsightsTab] Fetching priority insights for analysis ID: ${analysisId}`);
        const data = await apiClient.getPriorityInsights(analysisId);

        console.log(`[PriorityInsightsTab] Success: ${data.insights.length} insights found`);
        setPriorityData(data);
      } catch (err) {
        console.error('[PriorityInsightsTab] Error fetching priority insights:', err);
        setError(err instanceof Error ? err.message : 'Failed to load priority insights');
      } finally {
        console.log('[PriorityInsightsTab] fetchPriorityData completed');
        setLoading(false);
      }
    };

    fetchPriorityData();
  }, [analysisId]);

  // Filter insights based on active tab
  const filteredInsights = (priorityData?.insights || []).filter(insight => {
    if (activeTab === 'all') return true;
    return insight.urgency === activeTab;
  });

  // Get urgency icon based on level
  const getUrgencyIcon = (urgency: string) => {
    switch (urgency) {
      case 'high':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'medium':
        return <AlertTriangle className="h-4 w-4 text-amber-500" />;
      case 'low':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      default:
        return null;
    }
  };

  // Get urgency color class
  const getUrgencyColorClass = (urgency: string) => {
    switch (urgency) {
      case 'high':
        return 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800';
      case 'medium':
        return 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-900/20 dark:text-amber-300 dark:border-amber-800';
      case 'low':
        return 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200 dark:bg-slate-800/50 dark:text-slate-300 dark:border-slate-700';
    }
  };

  // Get type badge
  const getTypeBadge = (type: 'theme' | 'pattern') => {
    return (
      <Badge
        variant="outline"
        className={type === 'theme'
          ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800'
          : 'bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300 dark:border-purple-800'}
      >
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </Badge>
    );
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <LoadingSpinner label="Loading priority insights..." />
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Priority Insights</CardTitle>
          <CardDescription>Unable to load insights</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="p-4 border border-red-200 dark:border-red-800 rounded-md bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300">
            <div className="flex items-center gap-2 mb-2">
              <AlertCircle className="h-5 w-5" />
              <span className="font-semibold">Error</span>
            </div>
            <p>{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!priorityData || !priorityData.insights.length) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No priority insights available for this analysis.
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Priority Insights</CardTitle>
        <CardDescription>
          Actionable insights prioritized by sentiment impact
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as 'all' | 'high' | 'medium' | 'low')}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">
              All ({priorityData?.insights?.length || 0})
            </TabsTrigger>
            <TabsTrigger value="high">
              High Priority ({priorityData?.metrics?.high_urgency_count || 0})
            </TabsTrigger>
            <TabsTrigger value="medium">
              Medium ({priorityData?.metrics?.medium_urgency_count || 0})
            </TabsTrigger>
            <TabsTrigger value="low">
              Low ({priorityData?.metrics?.low_urgency_count || 0})
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="mt-4">
            {filteredInsights.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No {activeTab !== 'all' ? activeTab + ' priority' : ''} insights found
              </div>
            ) : (
              <div className="space-y-4">
                {filteredInsights.map((insight: PrioritizedInsightWithOriginal, index) => (
                  <div
                    key={`${insight.type}-${insight.name}-${index}`}
                    className={`border rounded-lg p-4 ${getUrgencyColorClass(insight.urgency)}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        {getUrgencyIcon(insight.urgency)}
                        <span className="font-medium capitalize">{insight.urgency} Priority</span>
                        {getTypeBadge(insight.type)}
                        {insight.category && (
                          <Badge variant="outline" className="bg-white dark:bg-slate-800 dark:border-slate-700">
                            {insight.category}
                          </Badge>
                        )}
                      </div>
                      <Badge variant="outline" className="bg-white dark:bg-slate-800 dark:border-slate-700">
                        Score: {insight.priority_score}
                      </Badge>
                    </div>

                    <h3 className="text-base font-semibold mb-1">
                      {/* Use description for pattern name if it starts with "Unnamed Pattern" */}
                      {insight.type === 'pattern' && insight.name.startsWith('Unnamed Pattern')
                        ? insight.description
                        : insight.name}
                    </h3>

                    {/* Show description only if it's different from the displayed name */}
                    {!(insight.type === 'pattern' && insight.name.startsWith('Unnamed Pattern')) && (
                      <p className="text-sm text-muted-foreground mb-3">{insight.description}</p>
                    )}

                    {/* Display supporting statements (evidence for patterns, statements for themes) */}
                    {insight.type === 'pattern' && (insight.original as PatternOriginal).evidence && (insight.original as PatternOriginal).evidence!.length > 0 && (
                      <div className="mt-2 mb-3 pl-3 border-l-2 border-gray-200 dark:border-gray-700">
                        <div className="space-y-2">
                          {(insight.original as PatternOriginal).evidence!.map((evidence: string, i: number) => (
                            <div key={i} className="relative bg-muted/30 dark:bg-slate-800/50 p-3 rounded-md">
                              <div className="absolute top-0 left-0 h-full w-1 bg-primary/30 dark:bg-primary/40 rounded-l-md"></div>
                              <p className="text-sm text-muted-foreground italic">{evidence}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                    {insight.type === 'theme' && (insight.original as ThemeOriginal).statements && (insight.original as ThemeOriginal).statements!.length > 0 && (
                      <div className="mt-2 mb-3 pl-3 border-l-2 border-gray-200 dark:border-gray-700">
                        <div className="space-y-2">
                          {(insight.original as ThemeOriginal).statements!.map((statement: string, i: number) => (
                            <div key={i} className="relative bg-muted/30 dark:bg-slate-800/50 p-3 rounded-md">
                              <div className="absolute top-0 left-0 h-full w-1 bg-primary/30 dark:bg-primary/40 rounded-l-md"></div>
                              <p className="text-sm text-muted-foreground italic">{statement}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex items-center gap-3 text-xs">
                      <span className="flex items-center gap-1">
                        <span className="font-medium">Sentiment:</span>
                        <Badge variant="outline" className={
                          insight.sentiment > 0
                            ? 'bg-green-50 dark:bg-green-900/20 dark:text-green-300 dark:border-green-800'
                            : (insight.sentiment < 0
                                ? 'bg-red-50 dark:bg-red-900/20 dark:text-red-300 dark:border-red-800'
                                : 'bg-blue-50 dark:bg-blue-900/20 dark:text-blue-300 dark:border-blue-800')
                        }>
                          {insight.sentiment > 0 ? 'Positive' : (insight.sentiment < 0 ? 'Negative' : 'Neutral')}
                        </Badge>
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="font-medium">Frequency:</span>
                        <Badge variant="outline" className="bg-white dark:bg-slate-800 dark:border-slate-700">
                          {Math.round(insight.frequency * 100)}%
                        </Badge>
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}

export default PriorityInsightsTab;
