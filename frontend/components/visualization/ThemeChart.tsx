'use client';

import React, { useState } from 'react';
import type {
  BarChart as BarChartType,
  CartesianGrid as CartesianGridType,
  XAxis as XAxisType,
  YAxis as YAxisType,
  Tooltip as TooltipType,
  Bar as BarType,
  Cell as CellType,
  ReferenceLine as ReferenceLineType,
  Legend as LegendType,
} from 'recharts';
import { Theme } from '@/types/api';
import {
  ResponsiveContainer,
  ChartTooltip,
  createCustomTooltip,
  ChartLegend,
  createLegendItems,
} from './common';
import {
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  Bar,
  Cell,
  ReferenceLine,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

export interface ThemeChartProps {
  themes: Theme[];
}

const SENTIMENT_COLORS = {
  positive: '#22c55e', // green-500
  neutral: '#64748b', // slate-500
  negative: '#ef4444', // red-500
};

export function ThemeChart({ themes }: ThemeChartProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null);
  const [viewMode, setViewMode] = useState<'sentiment' | 'frequency' | 'list'>('sentiment');

  // Filter themes based on search term
  const filteredThemes = themes.filter(theme => 
    theme.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (theme.keywords && theme.keywords.some(keyword => 
      keyword.toLowerCase().includes(searchTerm.toLowerCase())
    ))
  );

  // Group themes by sentiment
  const positiveThemes = filteredThemes.filter(theme => (theme.sentiment || 0) > 0.1);
  const neutralThemes = filteredThemes.filter(theme => (theme.sentiment || 0) >= -0.1 && (theme.sentiment || 0) <= 0.1);
  const negativeThemes = filteredThemes.filter(theme => (theme.sentiment || 0) < -0.1);

  // Sort themes by frequency for frequency view
  const sortedByFrequency = [...filteredThemes].sort((a, b) => (b.frequency || 0) - (a.frequency || 0));
  const topThemes = sortedByFrequency.slice(0, 10); // Top 10 themes

  // Get sentiment label
  const getSentimentLabel = (sentiment: number | undefined) => {
    if (typeof sentiment !== 'number') return 'Neutral';
    if (sentiment >= 0.1) return 'Positive';
    if (sentiment <= -0.1) return 'Negative';
    return 'Neutral';
  };

  // Theme card component
  const ThemeCard = ({ theme }: { theme: Theme }) => (
    <li key={theme.id} className="border-b pb-3 last:border-0">
      <div className="flex justify-between items-start">
        <h4 className="font-medium">{theme.name}</h4>
        <Badge 
          variant="outline" 
          className={`${(theme.sentiment || 0) > 0.1 
            ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300' 
            : (theme.sentiment || 0) < -0.1 
              ? 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300' 
              : 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'}`}
        >
          {Math.round((theme.frequency || 0) * 100)}%
        </Badge>
      </div>
      {theme.keywords && theme.keywords.length > 0 && (
        <div className="mt-1 flex flex-wrap gap-1">
          {theme.keywords.map((keyword, i) => (
            <Badge key={i} variant="secondary" className="text-xs">
              {keyword}
            </Badge>
          ))}
        </div>
      )}
      {theme.statements && theme.statements.length > 0 && (
        <div className="mt-2 text-sm text-muted-foreground">
          <p className="italic">"{theme.statements[0]}"</p>
        </div>
      )}
      <div className="mt-2">
        <Button 
          variant="ghost" 
          size="sm" 
          className="text-xs p-0 h-auto"
          onClick={() => setSelectedTheme(theme)}
        >
          View Details
        </Button>
      </div>
    </li>
  );

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="w-full sm:w-64">
          <Input
            placeholder="Search themes or keywords..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full"
          />
          {searchTerm && (
            <p className="text-xs text-muted-foreground mt-1">
              Showing {filteredThemes.length} of {themes.length} themes
            </p>
          )}
        </div>
        <Tabs value={viewMode} onValueChange={(value) => setViewMode(value as 'sentiment' | 'frequency' | 'list')}>
          <TabsList>
            <TabsTrigger value="sentiment">By Sentiment</TabsTrigger>
            <TabsTrigger value="frequency">By Frequency</TabsTrigger>
            <TabsTrigger value="list">List View</TabsTrigger>
          </TabsList>
        </Tabs>
      </div>

      {/* View by Sentiment */}
      {viewMode === 'sentiment' && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Positive Themes */}
          <Card>
            <CardHeader className="bg-green-50 dark:bg-green-900/20">
              <CardTitle className="text-green-700 dark:text-green-300">Positive Themes</CardTitle>
              <CardDescription>Themes with positive sentiment</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              {positiveThemes.length > 0 ? (
                <ul className="space-y-4">
                  {positiveThemes.map((theme) => (
                    <ThemeCard key={theme.id} theme={theme} />
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground text-center py-4">No positive themes found</p>
              )}
            </CardContent>
          </Card>

          {/* Neutral Themes */}
          <Card>
            <CardHeader className="bg-blue-50 dark:bg-blue-900/20">
              <CardTitle className="text-blue-700 dark:text-blue-300">Neutral Themes</CardTitle>
              <CardDescription>Themes with neutral sentiment</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              {neutralThemes.length > 0 ? (
                <ul className="space-y-4">
                  {neutralThemes.map((theme) => (
                    <ThemeCard key={theme.id} theme={theme} />
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground text-center py-4">No neutral themes found</p>
              )}
            </CardContent>
          </Card>

          {/* Negative Themes */}
          <Card>
            <CardHeader className="bg-red-50 dark:bg-red-900/20">
              <CardTitle className="text-red-700 dark:text-red-300">Negative Themes</CardTitle>
              <CardDescription>Themes with negative sentiment</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              {negativeThemes.length > 0 ? (
                <ul className="space-y-4">
                  {negativeThemes.map((theme) => (
                    <ThemeCard key={theme.id} theme={theme} />
                  ))}
                </ul>
              ) : (
                <p className="text-muted-foreground text-center py-4">No negative themes found</p>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* View by Frequency */}
      {viewMode === 'frequency' && (
        <Card>
          <CardHeader>
            <CardTitle>Top Themes by Frequency</CardTitle>
            <CardDescription>Most frequently mentioned themes in the interview</CardDescription>
          </CardHeader>
          <CardContent>
            {topThemes.length > 0 ? (
              <ul className="space-y-4">
                {topThemes.map((theme) => (
                  <ThemeCard key={theme.id} theme={theme} />
                ))}
              </ul>
            ) : (
              <p className="text-muted-foreground text-center py-4">No themes found</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* List View (similar to PatternList) */}
      {viewMode === 'list' && (
        <Card>
          <CardHeader>
            <CardTitle>Identified Themes</CardTitle>
            <CardDescription>
              {sortedByFrequency.length} theme{sortedByFrequency.length !== 1 ? 's' : ''} found in the analysis
            </CardDescription>
          </CardHeader>
          <CardContent>
            {sortedByFrequency.length > 0 ? (
              <Accordion type="multiple" className="w-full">
                {sortedByFrequency.map((theme) => (
                  <AccordionItem key={theme.id} value={`theme-${theme.id}`}>
                    <AccordionTrigger className="hover:no-underline">
                      <div className="flex items-center justify-between w-full pr-4">
                        <span className="font-medium text-left">{theme.name}</span>
                        <div className="flex items-center gap-2">
                          <Badge 
                            variant="outline" 
                            className={`${(theme.sentiment || 0) > 0.1 
                              ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300' 
                              : (theme.sentiment || 0) < -0.1 
                                ? 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300' 
                                : 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'}`}
                >
                  {getSentimentLabel(theme.sentiment)}
                          </Badge>
                          <Badge variant="outline">
                            {Math.round((theme.frequency || 0) * 100)}%
                          </Badge>
                        </div>
                      </div>
                    </AccordionTrigger>
                    <AccordionContent>
                      <div className="space-y-3 pt-2">
                        {theme.keywords && theme.keywords.length > 0 && (
                          <div className="space-y-1">
                            <h4 className="text-sm font-medium">Keywords:</h4>
                            <div className="flex flex-wrap gap-1">
                              {theme.keywords.map((keyword, i) => (
                                <Badge key={i} variant="secondary" className="text-xs">
                                  {keyword}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}
                        
                        {(theme.statements && theme.statements.length > 0) || (theme.examples && theme.examples.length > 0) ? (
                          <div className="space-y-2">
                            <h4 className="text-sm font-medium">Supporting Statements:</h4>
                            <ScrollArea className="h-40 rounded-md border p-4">
                              <ul className="space-y-2 text-sm">
                                {theme.statements && theme.statements.map((statement, i) => (
                                  <li key={i} className="bg-muted p-2 rounded-md">
                                    <p className="italic">"{statement}"</p>
                                  </li>
                                ))}
                                {!theme.statements && theme.examples && theme.examples.map((example, i) => (
                                  <li key={i} className="bg-muted p-2 rounded-md">
                                    <p className="italic">"{example}"</p>
                                  </li>
                                ))}
                              </ul>
                            </ScrollArea>
                          </div>
                        ) : (
                          <p className="text-sm text-muted-foreground">No supporting statements available.</p>
                        )}
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                ))}
              </Accordion>
            ) : (
              <p className="text-muted-foreground text-center py-4">No themes found</p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Theme Details Modal */}
      {selectedTheme && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedTheme(null)}>
          <div className="w-full max-w-3xl max-h-[90vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <Card>
              <CardHeader>
                <CardTitle>{selectedTheme.name}</CardTitle>
                <CardDescription>Theme details and supporting evidence</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center gap-2">
                  <Badge 
                    variant="outline" 
                    className={`${(selectedTheme.sentiment || 0) > 0.1 
                      ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300' 
                      : (selectedTheme.sentiment || 0) < -0.1 
                        ? 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300' 
                        : 'bg-blue-50 text-blue-700 dark:bg-blue-900/20 dark:text-blue-300'}`}
                  >
                    {(selectedTheme.sentiment || 0) > 0.1 
                      ? 'Positive' 
                      : (selectedTheme.sentiment || 0) < -0.1 
                        ? 'Negative' 
                        : 'Neutral'}
                  </Badge>
                  <Badge variant="outline">
                    Frequency: {Math.round((selectedTheme.frequency || 0) * 100)}%
                  </Badge>
                </div>
                
                {selectedTheme.keywords && selectedTheme.keywords.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">Keywords</h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedTheme.keywords.map((keyword, i) => (
                        <Badge key={i} variant="secondary">
                          {keyword}
                        </Badge>
                      ))}
              </div>
                  </div>
                )}
                
                <div>
                  <h4 className="text-sm font-medium mb-2">Supporting Statements</h4>
                  {selectedTheme.statements && selectedTheme.statements.length > 0 ? (
                    <ul className="space-y-2">
                      {selectedTheme.statements.map((statement, i) => (
                        <li key={i} className="text-sm bg-muted p-2 rounded-md">
                          <p className="italic">"{statement}"</p>
                        </li>
                      ))}
                    </ul>
                  ) : selectedTheme.examples && selectedTheme.examples.length > 0 ? (
                    <ul className="space-y-2">
                      {selectedTheme.examples.map((example, i) => (
                        <li key={i} className="text-sm bg-muted p-2 rounded-md">
                          <p className="italic">"{example}"</p>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-muted-foreground">No supporting statements available. This may be due to limited evidence in the interview data.</p>
                  )}
                </div>
                
                <div className="mt-4 flex justify-end">
                  <Button variant="outline" onClick={() => setSelectedTheme(null)}>
                    Close
                  </Button>
              </div>
              </CardContent>
            </Card>
            </div>
        </div>
      )}
    </div>
  );
}

export default ThemeChart;