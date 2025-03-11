'use client';

import React, { useMemo, useState } from 'react';
import { Pattern } from '@/types/api';
import { ChartLegend } from './common';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
  ReferenceLine,
  Legend,
  Treemap,
  ResponsiveContainer
} from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';

export interface PatternListProps {
  patterns: Pattern[];
  showEvidence?: boolean;
  className?: string;
  onPatternClick?: (pattern: Pattern) => void;
}

const SENTIMENT_COLORS = {
  positive: '#22c55e', // green-500
  neutral: '#64748b', // slate-500
  negative: '#ef4444', // red-500
};

export function PatternList({ patterns, showEvidence = true, className, onPatternClick }: PatternListProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedPattern, setSelectedPattern] = useState<Pattern | null>(null);

  // Filter patterns based on search term
  const filteredPatterns = patterns.filter(pattern => 
    (pattern.name?.toLowerCase().includes(searchTerm.toLowerCase())) ||
    (pattern.description && pattern.description.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Sort patterns by frequency
  const sortedPatterns = [...filteredPatterns].sort((a, b) => (b.frequency || 0) - (a.frequency || 0));

  // Group patterns by category (if available)
  const groupedPatterns = sortedPatterns.reduce((groups, pattern) => {
    const category = pattern.category || 'Uncategorized';
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(pattern);
    return groups;
  }, {} as Record<string, Pattern[]>);

  // Get all categories
  const categories = Object.keys(groupedPatterns).sort();

  // Process the data to handle missing fields
  const processedData = useMemo(() => {
    return patterns.map((pattern, index) => ({
      ...pattern,
      id: pattern.id || index,
      name: pattern.name || `Pattern ${index + 1}`,
      category: pattern.category || 'Uncategorized',
      description: pattern.description || '',
      frequency: typeof pattern.frequency === 'number' ? pattern.frequency : 0,
      sentiment: typeof pattern.sentiment === 'number' ? pattern.sentiment : 0,
      evidence: pattern.evidence || pattern.examples || [],
      examples: pattern.examples || pattern.evidence || []
    }));
  }, [patterns]);

  const getSentimentLabel = (sentiment: number | undefined) => {
    if (typeof sentiment !== 'number') return 'Neutral';
    if (sentiment >= 0.2) return 'Positive';
    if (sentiment <= -0.2) return 'Negative';
    return 'Neutral';
  };

  const getPatternColors = (sentiment: number | undefined) => {
    if (typeof sentiment !== 'number') {
      return { border: 'border-slate-300', bg: 'bg-slate-50' };
    }
    if (sentiment >= 0.2) {
      return { border: 'border-green-300', bg: 'bg-green-50' };
    }
    if (sentiment <= -0.2) {
      return { border: 'border-red-300', bg: 'bg-red-50' };
    }
    return { border: 'border-slate-300', bg: 'bg-slate-50' };
  };

  const handlePatternClick = (pattern: Pattern) => {
    if (onPatternClick) {
      onPatternClick(pattern);
    } else {
      setSelectedPattern(pattern === selectedPattern ? null : pattern);
    }
  };

  const legendItems = [
    { value: 'Positive Pattern', color: SENTIMENT_COLORS.positive, type: 'circle' as const },
    { value: 'Neutral Pattern', color: SENTIMENT_COLORS.neutral, type: 'circle' as const },
    { value: 'Negative Pattern', color: SENTIMENT_COLORS.negative, type: 'circle' as const },
  ];

  return (
    <div className={`w-full ${className}`}>
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between mb-4">
        <div className="w-full sm:w-64">
          <Input
            placeholder="Search patterns..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Identified Patterns</CardTitle>
          <CardDescription>
            {sortedPatterns.length} pattern{sortedPatterns.length !== 1 ? 's' : ''} found in the analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sortedPatterns.length > 0 ? (
            <div className="space-y-8">
              {sortedPatterns.map((pattern) => (
                <div key={pattern.id} id={`pattern-${pattern.id}`} className="border-b pb-6 last:border-0 last:pb-0">
                  <div className="w-full mb-4">
                    <h2 className="text-xl font-bold text-foreground">{pattern.name}</h2>
                  </div>
                  
                  {pattern.description && (
                    <div className="mb-5 p-1.5 relative">
                      <div className={`border ${getPatternColors(pattern.sentiment).border} ${getPatternColors(pattern.sentiment).bg} rounded-lg p-4 relative`}>
                        <Badge className="absolute top-1/2 right-3 -translate-y-1/2">
                          {Math.round((pattern.frequency || 0) * 100)}%
                        </Badge>
                        <div className="absolute -left-1 -top-1 text-4xl text-primary/20 font-serif">"</div>
                        <div className="absolute -right-1 -bottom-1 text-4xl text-primary/20 font-serif rotate-180">"</div>
                        <p className="text-base leading-relaxed text-foreground pr-16">
                          {pattern.description}
                        </p>
                      </div>
                    </div>
                  )}
                  
                  {pattern.examples && pattern.examples.length > 0 && (
                    <div className="mt-3">
                      <span className="text-xs font-semibold uppercase text-muted-foreground bg-muted px-2 py-1 rounded-sm inline-block mb-2">Supporting Statements</span>
                      <div className="pl-3 border-l-2 border-primary/20">
                        <ul className="space-y-3">
                          {pattern.examples.map((example, i) => (
                            <li key={i} className="relative bg-muted/30 p-3 rounded-md">
                              <div className="absolute top-0 left-0 h-full w-1 bg-primary/30 rounded-l-md"></div>
                              <p className="italic text-muted-foreground text-sm">"{example}"</p>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground text-center py-4">No patterns identified</p>
          )}
        </CardContent>
      </Card>

      <div className="mt-4">
        <ChartLegend items={legendItems} />
      </div>
    </div>
  );
}

export default PatternList;