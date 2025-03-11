'use client';

import React, { useState } from 'react';
import { Theme } from '@/types/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

export interface ThemeChartProps {
  themes: Theme[];
}

export function ThemeChart({ themes }: ThemeChartProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTheme, setSelectedTheme] = useState<Theme | null>(null);

  // Filter themes based on search term
  const filteredThemes = themes.filter(theme => 
    theme.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (theme.keywords && theme.keywords.some(keyword => 
      keyword.toLowerCase().includes(searchTerm.toLowerCase())
    ))
  );

  // Sort themes by frequency for list view
  const sortedThemes = [...filteredThemes].sort((a, b) => (b.frequency || 0) - (a.frequency || 0));

  // Get sentiment label
  const getSentimentLabel = (sentiment: number | undefined) => {
    if (typeof sentiment !== 'number') return 'Neutral';
    if (sentiment >= 0.1) return 'Positive';
    if (sentiment <= -0.1) return 'Negative';
    return 'Neutral';
  };

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
      </div>

      {/* List View of Themes */}
      <Card>
        <CardHeader>
          <CardTitle>Identified Themes</CardTitle>
          <CardDescription>
            {sortedThemes.length} theme{sortedThemes.length !== 1 ? 's' : ''} found in the analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          {sortedThemes.length > 0 ? (
            <Accordion type="multiple" className="w-full">
              {sortedThemes.map((theme) => (
                <AccordionItem key={theme.id} value={`theme-${theme.id}`}>
                  <AccordionTrigger className="hover:no-underline">
                    <div className="flex items-center justify-between w-full pr-4">
                      <span className="font-medium text-left flex items-center">
                        {theme.name}
                        {theme.process === 'enhanced' && (
                          <Badge variant="outline" className="ml-2 bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300 text-xs">
                            Enhanced
                          </Badge>
                        )}
                      </span>
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
                      {theme.definition && (
                        <div className="space-y-1">
                          <h4 className="text-sm font-medium">Definition:</h4>
                          <p className="text-sm p-2 bg-muted rounded-md">{theme.definition}</p>
                        </div>
                      )}
                    
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
                      
                      {theme.codes && theme.codes.length > 0 && (
                        <div className="space-y-1">
                          <h4 className="text-sm font-medium">Associated Codes:</h4>
                          <div className="flex flex-wrap gap-1">
                            {theme.codes.map((code, i) => (
                              <Badge key={i} variant="outline" className="text-xs bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300">
                                {code}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      )}
                      
                      {theme.reliability !== undefined && (
                        <div className="space-y-1">
                          <h4 className="text-sm font-medium">Reliability Score:</h4>
                          <div className="flex items-center">
                            <span className={`text-sm ${
                              theme.reliability >= 0.7 ? 'text-green-600' : 
                              theme.reliability >= 0.5 ? 'text-amber-600' : 
                              'text-red-600'
                            }`}>
                              {(theme.reliability * 100).toFixed(0)}%
                            </span>
                            <span className="text-xs text-muted-foreground ml-2">
                              ({theme.reliability >= 0.7 ? 'High' : theme.reliability >= 0.5 ? 'Moderate' : 'Low'} agreement between raters)
                            </span>
                          </div>
                        </div>
                      )}
                      
                      {(theme.statements && theme.statements.length > 0) || (theme.examples && theme.examples.length > 0) ? (
                        <div>
                          <span className="text-xs font-semibold uppercase text-muted-foreground bg-muted px-2 py-1 rounded-sm inline-block mb-2">Supporting Statements</span>
                          <div className="rounded-md border p-4">
                            <ul className="space-y-2 text-sm">
                              {theme.statements && theme.statements.map((statement, i) => (
                                <li key={i} className="relative bg-muted/30 p-3 rounded-md">
                                  <div className="absolute top-0 left-0 h-full w-1 bg-primary/30 rounded-l-md"></div>
                                  <p className="italic text-muted-foreground text-sm">"{statement}"</p>
                                </li>
                              ))}
                              {!theme.statements && theme.examples && theme.examples.map((example, i) => (
                                <li key={i} className="relative bg-muted/30 p-3 rounded-md">
                                  <div className="absolute top-0 left-0 h-full w-1 bg-primary/30 rounded-l-md"></div>
                                  <p className="italic text-muted-foreground text-sm">"{example}"</p>
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>
                      ) : (
                        <p className="text-muted-foreground">No supporting statements available.</p>
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

      {/* Theme Details Modal */}
      {selectedTheme && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setSelectedTheme(null)}>
          <div className="w-full max-w-3xl max-h-[90vh] overflow-auto" onClick={(e) => e.stopPropagation()}>
            <Card>
              <CardHeader>
                <div className="flex justify-between items-center">
                  <div>
                    <CardTitle className="flex items-center">
                      {selectedTheme.name}
                      {selectedTheme.process === 'enhanced' && (
                        <Badge variant="outline" className="ml-2 bg-purple-50 text-purple-700 dark:bg-purple-900/20 dark:text-purple-300">
                          Enhanced Analysis
                        </Badge>
                      )}
                    </CardTitle>
                    <CardDescription>Theme details and supporting evidence</CardDescription>
                  </div>
                </div>
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
                  {selectedTheme.reliability !== undefined && (
                    <Badge 
                      variant="outline"
                      className={selectedTheme.reliability >= 0.7 
                        ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-300' 
                        : selectedTheme.reliability >= 0.5 
                          ? 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300' 
                          : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300'}
                    >
                      Reliability: {(selectedTheme.reliability * 100).toFixed(0)}%
                    </Badge>
                  )}
                </div>
                
                {selectedTheme.definition && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">Definition</h4>
                    <p className="text-sm p-2 bg-muted rounded-md">{selectedTheme.definition}</p>
                  </div>
                )}
                
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
                
                {selectedTheme.codes && selectedTheme.codes.length > 0 && (
                  <div>
                    <h4 className="text-sm font-medium mb-2">Associated Codes</h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedTheme.codes.map((code, i) => (
                        <Badge key={i} variant="outline" className="bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300">
                          {code}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {(selectedTheme.statements && selectedTheme.statements.length > 0) || (selectedTheme.examples && selectedTheme.examples.length > 0) ? (
                  <div>
                    <span className="text-xs font-semibold uppercase text-muted-foreground bg-muted px-2 py-1 rounded-sm inline-block mb-2">Supporting Statements</span>
                    <div className="rounded-md border p-4">
                      <ul className="space-y-2">
                        {selectedTheme.statements && selectedTheme.statements.map((statement, i) => (
                          <li key={i} className="relative bg-muted/30 p-3 rounded-md">
                            <div className="absolute top-0 left-0 h-full w-1 bg-primary/30 rounded-l-md"></div>
                            <p className="italic text-muted-foreground text-sm">"{statement}"</p>
                          </li>
                        ))}
                        {!selectedTheme.statements && selectedTheme.examples && selectedTheme.examples.map((example, i) => (
                          <li key={i} className="relative bg-muted/30 p-3 rounded-md">
                            <div className="absolute top-0 left-0 h-full w-1 bg-primary/30 rounded-l-md"></div>
                            <p className="italic text-muted-foreground text-sm">"{example}"</p>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">No supporting statements available.</p>
                )}
                
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