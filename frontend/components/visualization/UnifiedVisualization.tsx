'use client';

// Note on type handling:
// This component handles multiple visualization types ('themes', 'patterns', 'sentiment', 'personas')
// We use explicit type guards with separate if statements rather than ternary operators
// to avoid TypeScript "no overlap" errors when comparing string literal types.

import React, { useMemo } from 'react';
import { Theme, Pattern, SentimentData, SentimentStatements, Persona } from '@/types/api';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ThemeChart } from './ThemeChart';
import { PatternList } from './PatternList';
import { PersonaList } from './PersonaList';

interface UnifiedVisualizationProps {
  type: 'themes' | 'patterns' | 'sentiment' | 'personas';
  themesData?: Theme[];
  patternsData?: Pattern[];
  personasData?: Persona[];
  sentimentData?: {
    overview: { positive: number; neutral: number; negative: number };
    details?: SentimentData[];
    statements?: SentimentStatements;
  };
  className?: string;
}

const UnifiedVisualization: React.FC<UnifiedVisualizationProps> = ({
  type,
  themesData = [],
  patternsData = [],
  personasData = [],
  sentimentData = { overview: { positive: 0.33, neutral: 0.34, negative: 0.33 } },
  className,
}) => {
  // Prepare sentiment data for SentimentGraph component
  const sentimentGraphData = useMemo(() => {
    return {
      data: sentimentData.overview,
      detailedData: sentimentData.details || [],
      supportingStatements: sentimentData.statements || { positive: [], neutral: [], negative: [] }
    };
  }, [sentimentData]);

  // Generate key insights based on visualization type
  const getKeyInsights = () => {
    const insights = [];
    
    if (type === 'themes' && themesData.length > 0) {
      // Prepare theme insights
      const sortedThemes = [...themesData].sort((a, b) => b.frequency - a.frequency);
      const topThemes = sortedThemes.slice(0, 3);
      
      insights.push(`Top themes: ${topThemes.map(t => t.name).join(', ')}`);
      
      // Add sentiment distribution of themes
      const posThemes = themesData.filter(t => typeof t.sentiment === 'string' && t.sentiment === 'positive').length;
      const neuThemes = themesData.filter(t => typeof t.sentiment === 'string' && t.sentiment === 'neutral').length;
      const negThemes = themesData.filter(t => typeof t.sentiment === 'string' && t.sentiment === 'negative').length;
      
      if (posThemes > 0) {
        insights.push(`${posThemes} positive themes identified`);
      }
      if (neuThemes > 0) {
        insights.push(`${neuThemes} neutral themes identified`);
      }
      if (negThemes > 0) {
        insights.push(`${negThemes} negative themes identified`);
      }
    }
    
    if (type === 'patterns' && patternsData.length > 0) {
      // Prepare pattern insights
      const sortedPatterns = [...patternsData].sort((a, b) => b.frequency - a.frequency);
      const topPatterns = sortedPatterns.slice(0, 3);
      
      insights.push(`Top patterns: ${topPatterns.map(p => p.description).join(', ')}`);
      
      // Add sentiment distribution of patterns - fixing type checking
      const posPatterns = patternsData.filter(p => typeof p.sentiment === 'string' && p.sentiment === 'positive').length;
      const neuPatterns = patternsData.filter(p => typeof p.sentiment === 'string' && p.sentiment === 'neutral').length;
      const negPatterns = patternsData.filter(p => typeof p.sentiment === 'string' && p.sentiment === 'negative').length;
      
      if (posPatterns > 0) {
        insights.push(`${posPatterns} positive patterns identified`);
      }
      if (neuPatterns > 0) {
        insights.push(`${neuPatterns} neutral patterns identified`);
      }
      if (negPatterns > 0) {
        insights.push(`${negPatterns} negative patterns identified`);
      }
    }
    
    if (type === 'sentiment') {
      // Prepare sentiment insights
      const { positive, neutral, negative } = sentimentData.overview;
      const dominantSentiment = Math.max(positive, neutral, negative);
      
      if (dominantSentiment === positive) {
        insights.push('Overall positive sentiment in the interview');
      } else if (dominantSentiment === negative) {
        insights.push('Overall negative sentiment in the interview');
      } else {
        insights.push('Overall neutral sentiment in the interview');
      }
      
      insights.push(`${Math.round(positive * 100)}% positive expressions`);
      insights.push(`${Math.round(neutral * 100)}% neutral expressions`);
      insights.push(`${Math.round(negative * 100)}% negative expressions`);
      
      if (sentimentData.statements) {
        const { positive: posStmts, neutral: neuStmts, negative: negStmts } = sentimentData.statements;
        insights.push(`${posStmts.length} positive statements, ${neuStmts.length} neutral statements, ${negStmts.length} negative statements`);
      }
    }
    
    if (type === 'personas' && personasData.length > 0) {
      // Prepare persona insights
      insights.push(`${personasData.length} distinct personas identified`);
      
      // Add info about top responsibilities and pain points
      const allResponsibilities = personasData.flatMap(p => 
        p.key_responsibilities?.value ? [p.key_responsibilities.value] : []
      );
      
      const allPainPoints = personasData.flatMap(p => 
        p.pain_points?.value ? [p.pain_points.value] : []
      );
      
      if (allResponsibilities.length > 0) {
        insights.push(`Key responsibilities include: ${allResponsibilities[0]}`);
      }
      
      if (allPainPoints.length > 0) {
        insights.push(`Main pain points: ${allPainPoints[0]}`);
      }
    }
    
    return insights.length > 0 ? insights : ['No key insights available for this analysis'];
  };

  // Render the Key Insights component
  const KeyFindings = () => {
    const insights = getKeyInsights();
    
    // For patterns, we want to format top patterns differently
    if (type === 'patterns' && patternsData.length > 0) {
      const sortedPatterns = [...patternsData].sort((a, b) => (b.frequency || 0) - (a.frequency || 0));
      const topPatterns = sortedPatterns.slice(0, 3);
      const otherInsights = insights.filter(insight => !insight.startsWith('Top patterns:'));

      return (
        <div className="space-y-4">
          <div className="mb-2">
            <h3 className="text-sm font-medium mb-2">Top Patterns</h3>
            <div className="space-y-3">
              {topPatterns.map((pattern, idx) => (
                <div key={idx} className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary/10 flex items-center justify-center text-xs font-medium">
                    {idx + 1}
                  </div>
                  <div className="flex-1">
                    <a 
                      href={`#pattern-${pattern.id || idx}`}
                      className="block hover:no-underline"
                      onClick={(e) => {
                        e.preventDefault();
                        const targetId = `pattern-${pattern.id || idx}`;
                        const targetElement = document.getElementById(targetId);
                        
                        if (targetElement) {
                          // Scroll to element with smooth behavior
                          targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                          });
                          
                          // Add highlight effect
                          targetElement.classList.add('bg-amber-50');
                          setTimeout(() => {
                            targetElement.classList.remove('bg-amber-50');
                          }, 2000);
                        }
                      }}
                    >
                      <div className={`p-2 rounded-md ${
                        (pattern.sentiment !== undefined && pattern.sentiment >= 0.2) ? 'bg-green-50 border border-green-100 hover:bg-green-100 hover:shadow-sm' : 
                        (pattern.sentiment !== undefined && pattern.sentiment <= -0.2) ? 'bg-red-50 border border-red-100 hover:bg-red-100 hover:shadow-sm' :
                        'bg-slate-50 border border-slate-100 hover:bg-slate-100 hover:shadow-sm'
                      } transition-all duration-150`}>
                        <div className="text-sm font-medium flex items-center">
                          {pattern.name}
                          <svg 
                            xmlns="http://www.w3.org/2000/svg" 
                            width="16" 
                            height="16" 
                            viewBox="0 0 24 24" 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="2" 
                            strokeLinecap="round" 
                            strokeLinejoin="round" 
                            className="ml-1 h-3 w-3 opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                            <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                          </svg>
                        </div>
                        {pattern.description && (
                          <p className="text-xs text-muted-foreground mt-1">{pattern.description}</p>
                        )}
                      </div>
                    </a>
                  </div>
                  <div className="flex-shrink-0">
                    <Badge variant="outline" className="text-xs">
                      {Math.round((pattern.frequency || 0) * 100)}%
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {otherInsights.length > 0 && (
            <div>
              <h3 className="text-sm font-medium mb-2">Additional Insights</h3>
              <ul className="space-y-2 list-disc pl-5">
                {otherInsights.map((insight, idx) => (
                  <li key={idx} className="text-sm">{insight}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      );
    }
    
    // For other visualization types, keep the existing format
    return (
      <ul className="space-y-2 list-disc pl-5">
        {insights.map((insight, idx) => (
          <li key={idx} className="text-sm">{insight}</li>
        ))}
      </ul>
    );
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header section with visualization type */}
      <div className="flex flex-col space-y-2">
        <h2 className="text-2xl font-bold tracking-tight">
          {type === 'themes' 
            ? 'Theme Analysis' 
            : type === 'patterns' 
              ? 'Pattern Analysis' 
              : type === 'sentiment' 
                ? 'Sentiment Analysis' 
                : 'Persona Analysis'}
        </h2>
        <p className="text-muted-foreground">
          {type === 'themes' 
            ? 'Key themes and insights from the interview' 
            : type === 'patterns' 
              ? 'Recurring patterns in user responses' 
              : type === 'sentiment' 
                ? 'Sentiment analysis of interview responses' 
                : 'User personas derived from the interview'}
        </p>
      </div>

      {/* Key Insights Card at the top */}
      <Card className="w-full">
        <CardHeader className="pb-2">
          <CardTitle className="text-base font-medium">Key Insights</CardTitle>
          <CardDescription>
            Significant findings from the {
              type === 'themes' ? 'theme' : 
              type === 'patterns' ? 'pattern' : 
              type === 'sentiment' ? 'sentiment' : 'persona'
            } analysis
          </CardDescription>
        </CardHeader>
        <CardContent>
          <KeyFindings />
        </CardContent>
      </Card>

      {/* Visualization Content Below */}
      <div className="w-full">
        {/* Render the appropriate visualization based on type */}
        {type === 'themes' ? (
          <ThemeChart themes={themesData} />
        ) : type === 'patterns' ? (
          <PatternList patterns={patternsData} />
        ) : type === 'sentiment' ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base font-medium">Positive Sentiment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center text-2xl font-bold text-green-500">
                  {Math.round(sentimentGraphData.data.positive * 100)}%
                </div>
                {sentimentGraphData.supportingStatements.positive.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium">Supporting Statements:</h4>
                    <ul className="space-y-2 list-disc pl-5 mt-2">
                      {sentimentGraphData.supportingStatements.positive.slice(0, 3).map((stmt, idx) => (
                        <li key={idx} className="text-sm">{stmt}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base font-medium">Neutral Sentiment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center text-2xl font-bold text-slate-500">
                  {Math.round(sentimentGraphData.data.neutral * 100)}%
                </div>
                {sentimentGraphData.supportingStatements.neutral.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium">Supporting Statements:</h4>
                    <ul className="space-y-2 list-disc pl-5 mt-2">
                      {sentimentGraphData.supportingStatements.neutral.slice(0, 3).map((stmt, idx) => (
                        <li key={idx} className="text-sm">{stmt}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-base font-medium">Negative Sentiment</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center text-2xl font-bold text-red-500">
                  {Math.round(sentimentGraphData.data.negative * 100)}%
                </div>
                {sentimentGraphData.supportingStatements.negative.length > 0 && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium">Supporting Statements:</h4>
                    <ul className="space-y-2 list-disc pl-5 mt-2">
                      {sentimentGraphData.supportingStatements.negative.slice(0, 3).map((stmt, idx) => (
                        <li key={idx} className="text-sm">{stmt}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        ) : (
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-base font-medium">User Personas</CardTitle>
              <CardDescription>Detailed user profiles generated from interview data</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <PersonaList personas={personasData} />
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
};

export default UnifiedVisualization;