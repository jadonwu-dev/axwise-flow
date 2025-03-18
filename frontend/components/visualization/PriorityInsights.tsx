'use client';

import React, { useState, useEffect } from 'react';
import { PrioritizedInsight, PriorityInsightsResponse } from '@/types/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { apiClient } from '@/lib/apiClient';
import { AlertCircle, AlertTriangle, CheckCircle } from 'lucide-react';

// Simple skeleton component for loading state
const Skeleton = ({ className }: { className: string }) => (
  <div className={`animate-pulse bg-slate-200 rounded ${className}`}></div>
);

export interface PriorityInsightsProps {
  analysisId: string;
}

export function PriorityInsights({ analysisId }: PriorityInsightsProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [priorityData, setPriorityData] = useState<PriorityInsightsResponse | null>(null);
  const [activeTab, setActiveTab] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  useEffect(() => {
    const fetchPriorityData = async () => {
      try {
        setLoading(true);
        const data = await apiClient.getPriorityInsights(analysisId);
        setPriorityData(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching priority data:', err);
        setError('Failed to load priority insights');
      } finally {
        setLoading(false);
      }
    };

    if (analysisId) {
      fetchPriorityData();
    }
  }, [analysisId]);

  // Filter insights based on active tab
  const filteredInsights = priorityData?.insights.filter(insight => {
    if (activeTab === 'all') return true;
    return insight.urgency === activeTab;
  }) || [];

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
        return 'bg-red-50 text-red-700 border-red-200';
      case 'medium':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'low':
        return 'bg-green-50 text-green-700 border-green-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  // Get type badge
  const getTypeBadge = (type: 'theme' | 'pattern') => {
    return (
      <Badge
        variant="outline"
        className={type === 'theme' ? 'bg-blue-50 text-blue-700' : 'bg-purple-50 text-purple-700'}
      >
        {type.charAt(0).toUpperCase() + type.slice(1)}
      </Badge>
    );
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-4 w-48" />
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-24 w-full" />
            <Skeleton className="h-24 w-full" />
          </div>
        </CardContent>
      </Card>
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
          <div className="p-4 border border-red-200 rounded-md bg-red-50 text-red-700">
            {error}
          </div>
        </CardContent>
      </Card>
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
        <Tabs value={activeTab} onValueChange={(value) => setActiveTab(value as any)}>
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="all">
              All ({priorityData?.insights.length || 0})
            </TabsTrigger>
            <TabsTrigger value="high">
              High Priority ({priorityData?.metrics.high_urgency_count || 0})
            </TabsTrigger>
            <TabsTrigger value="medium">
              Medium ({priorityData?.metrics.medium_urgency_count || 0})
            </TabsTrigger>
            <TabsTrigger value="low">
              Low ({priorityData?.metrics.low_urgency_count || 0})
            </TabsTrigger>
          </TabsList>

          <TabsContent value={activeTab} className="mt-4">
            {filteredInsights.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                No {activeTab !== 'all' ? activeTab + ' priority' : ''} insights found
              </div>
            ) : (
              <div className="space-y-4">
                {filteredInsights.map((insight, index) => (
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
                          <Badge variant="outline" className="bg-white">
                            {insight.category}
                          </Badge>
                        )}
                      </div>
                      <Badge variant="outline" className="bg-white">
                        Score: {insight.priority_score}
                      </Badge>
                    </div>
                    
                    <h3 className="text-base font-semibold mb-1">{insight.name}</h3>
                    <p className="text-sm text-muted-foreground mb-3">{insight.description}</p>
                    
                    <div className="flex items-center gap-3 text-xs">
                      <span className="flex items-center gap-1">
                        <span className="font-medium">Sentiment:</span>
                        <Badge variant="outline" className={insight.sentiment > 0 ? 'bg-green-50' : (insight.sentiment < 0 ? 'bg-red-50' : 'bg-blue-50')}>
                          {insight.sentiment > 0 ? 'Positive' : (insight.sentiment < 0 ? 'Negative' : 'Neutral')}
                        </Badge>
                      </span>
                      <span className="flex items-center gap-1">
                        <span className="font-medium">Frequency:</span>
                        <Badge variant="outline" className="bg-white">
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

export default PriorityInsights; 