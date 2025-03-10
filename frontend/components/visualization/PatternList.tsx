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
  const [viewMode, setViewMode] = useState<'all' | 'grouped'>('all');
  const [selectedPattern, setSelectedPattern] = useState<Pattern | null>(null);
  const [activeIndex, setActiveIndex] = useState<number | null>(null);
  const [displayMode, setDisplayMode] = useState<'treemap' | 'bar'>('treemap');

  // Filter patterns based on search term
  const filteredPatterns = patterns.filter(pattern => 
    pattern.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
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

  const { chartData, treemapData } = useMemo(() => {
    const grouped: Record<string, Pattern[]> = {};
    const transformed: any[] = [];
    const treeData: any[] = [];
    
    const sortedData = [...processedData].sort((a, b) => {
      const freqA = typeof a.frequency === 'number' ? a.frequency : 0;
      const freqB = typeof b.frequency === 'number' ? b.frequency : 0;
      return freqB - freqA;
    });
    
    sortedData.forEach((pattern, index) => {
      const category = pattern.category || 'Uncategorized';
      const frequencyValue = typeof pattern.frequency === 'number' 
        ? pattern.frequency 
        : (typeof pattern.frequency === 'string' 
          ? parseFloat(pattern.frequency) || 0 
          : 0);
      
      // For the bar chart
      transformed.push({
        id: pattern.id || index,
        name: pattern.name,
        frequency: frequencyValue,
        sentiment: pattern.sentiment || 0,
        originalData: pattern,
      });
      
      // For the treemap
      treeData.push({
        name: pattern.name,
        size: frequencyValue * 100,
        sentiment: pattern.sentiment || 0,
        category,
        originalData: pattern,
      });
      
      // For the categorized list
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(pattern);
    });
    
    return { 
      chartData: transformed, 
      treemapData: [{ name: 'Patterns', children: treeData }]
    };
  }, [processedData]);

  const getBarColor = (sentiment: number) => {
    if (sentiment >= 0.2) return SENTIMENT_COLORS.positive;
    if (sentiment <= -0.2) return SENTIMENT_COLORS.negative;
    return SENTIMENT_COLORS.neutral;
  };

  const getSentimentLabel = (sentiment: number | undefined) => {
    if (typeof sentiment !== 'number') return 'Neutral';
    if (sentiment >= 0.2) return 'Positive';
    if (sentiment <= -0.2) return 'Negative';
    return 'Neutral';
  };

  const handlePatternClick = (pattern: Pattern) => {
    if (onPatternClick) {
      onPatternClick(pattern);
    } else {
      setSelectedPattern(pattern === selectedPattern ? null : pattern);
    }
  };

  // Custom tooltip component that shows pattern details on hover
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-white shadow-lg rounded-md p-4 border border-gray-200">
          <h3 className="font-semibold text-gray-900">{data.name}</h3>
          <p className="text-sm text-gray-600">
            Frequency: {typeof data.frequency === 'number' ? `${(data.frequency * 100).toFixed(0)}%` : data.frequency}
          </p>
          <p className="text-sm" style={{ color: getBarColor(data.sentiment) }}>
            Sentiment: {getSentimentLabel(data.sentiment)}
          </p>
          {data.originalData.description && (
            <p className="text-sm text-gray-700 mt-2">{data.originalData.description}</p>
          )}
        </div>
      );
    }
    return null;
  };

  const legendItems = [
    { value: 'Positive Pattern', color: SENTIMENT_COLORS.positive, type: 'circle' as const },
    { value: 'Neutral Pattern', color: SENTIMENT_COLORS.neutral, type: 'circle' as const },
    { value: 'Negative Pattern', color: SENTIMENT_COLORS.negative, type: 'circle' as const },
  ];

  return (
    <div className={`w-full ${className}`}>
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="w-full sm:w-64">
          <Input
            placeholder="Search patterns..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
        </div>
        <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as 'all' | 'grouped')}>
          <TabsList>
            <TabsTrigger value="all">All Patterns</TabsTrigger>
            <TabsTrigger value="grouped">Grouped</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* All Patterns View */}
      {viewMode === 'all' && (
        <Card>
          <CardHeader>
            <CardTitle>Identified Patterns</CardTitle>
            <CardDescription>
              {sortedPatterns.length} pattern{sortedPatterns.length !== 1 ? 's' : ''} found in the analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            {sortedPatterns.length > 0 ? (
              <Accordion type="multiple" className="w-full">
                {sortedPatterns.map((pattern) => (
                  <AccordionItem key={pattern.id} value={`pattern-${pattern.id}`}>
                    <AccordionTrigger className="hover:no-underline">
                      <div className="flex items-center justify-between w-full pr-4">
                        <span className="font-medium text-left">{pattern.name}</span>
                        <Badge variant="outline" className="ml-2">
                          {Math.round((pattern.frequency || 0) * 100)}%
                        </Badge>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-3 pt-2">
                        {pattern.description && (
                          <p className="text-sm text-muted-foreground">{pattern.description}</p>
                        )}
                        
                        {pattern.examples && pattern.examples.length > 0 && (
                          <div className="space-y-2">
                            <h4 className="text-sm font-medium">Examples:</h4>
                            <ScrollArea className="h-40 rounded-md border p-4">
                              <ul className="space-y-2 text-sm">
                                {pattern.examples.map((example, i) => (
                                  <li key={i} className="bg-muted p-2 rounded-md">
                                    <p className="italic">"{example}"</p>
                                  </li>
                                ))}
                              </ul>
                            </ScrollArea>
                          </div>
                        )}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            ) : (
              <p className="text-muted-foreground text-center py-4">No patterns identified</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Grouped Patterns View */}
      {viewMode === 'grouped' && (
        <div className="space-y-6">
          {categories.map((category) => (
            <Card key={category}>
              <CardHeader>
                <CardTitle>{category}</CardTitle>
                <CardDescription>
                  {groupedPatterns[category].length} pattern{groupedPatterns[category].length !== 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Accordion type="multiple" className="w-full">
                  {groupedPatterns[category].map((pattern) => (
                    <AccordionItem key={pattern.id} value={`pattern-${pattern.id}`}>
                      <AccordionTrigger className="hover:no-underline">
                        <div className="flex items-center justify-between w-full pr-4">
                          <span className="font-medium text-left">{pattern.name}</span>
                          <Badge variant="outline" className="ml-2">
                            {Math.round((pattern.frequency || 0) * 100)}%
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <div className="space-y-3 pt-2">
                          {pattern.description && (
                            <p className="text-sm text-muted-foreground">{pattern.description}</p>
                          )}
                          
                          {pattern.examples && pattern.examples.length > 0 && (
                            <div className="space-y-2">
                              <h4 className="text-sm font-medium">Examples:</h4>
                              <ScrollArea className="h-40 rounded-md border p-4">
                                <ul className="space-y-2 text-sm">
                                  {pattern.examples.map((example, i) => (
                                    <li key={i} className="bg-muted p-2 rounded-md">
                                      <p className="italic">"{example}"</p>
                                    </li>
                                  ))}
                                </ul>
                              </ScrollArea>
                            </div>
                          )}
                        </div>
                      </AccordionContent>
                    </AccordionItem>
                  ))}
                </Accordion>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="mt-4">
        <ChartLegend items={legendItems} />
      </div>

      {selectedPattern && (
        <div className="mt-6 p-4 border border-gray-200 rounded-md bg-gray-50">
          <h3 className="text-lg font-semibold text-gray-800">{selectedPattern.name}</h3>
          {selectedPattern.description && (
            <p className="mt-2 text-gray-700">{selectedPattern.description}</p>
          )}
          {showEvidence && (selectedPattern.evidence || selectedPattern.examples) && (
            (selectedPattern.evidence?.length || selectedPattern.examples?.length) ? (
              <div className="mt-3">
                <h4 className="font-semibold text-gray-700">Supporting Evidence:</h4>
                <ul className="mt-2 list-disc pl-5 space-y-2">
                  {(selectedPattern.evidence || selectedPattern.examples || []).map((example, idx) => (
                    <li key={idx} className="text-gray-600">{example}</li>
                  ))}
                </ul>
              </div>
            ) : null
          )}
        </div>
      )}
    </div>
  );
}

export default PatternList;