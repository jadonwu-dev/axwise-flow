'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';
import { Tooltip } from 'react-tooltip';

// Define types for Persona data structure
type PersonaTrait = {
  value: string;
  confidence: number;
  evidence: string[];
};

export type Persona = {
  name: string;
  description: string;
  role_context: PersonaTrait;
  key_responsibilities: PersonaTrait;
  tools_used: PersonaTrait;
  collaboration_style: PersonaTrait;
  analysis_approach: PersonaTrait;
  pain_points: PersonaTrait;
  patterns: string[];
  confidence: number;
  evidence: string[];
  metadata?: {
    sample_size?: number;
    timestamp?: string;
    validation_metrics?: {
      pattern_confidence?: number;
      evidence_count?: number;
      attribute_coverage?: Record<string, number>;
    };
  };
};

type PersonaListProps = {
  data?: Persona[];
  className?: string;
  personas?: Persona[];
};

export function PersonaList({ data = [], className, personas }: PersonaListProps) {
  // Use personas prop if provided, otherwise fall back to data prop
  const personaData = personas || data;
  
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(
    personaData.length > 0 ? personaData[0] : null
  );
  
  // State for managing evidence visibility
  const [evidenceVisibility, setEvidenceVisibility] = useState<Record<string, boolean>>({});

  // Toggle evidence visibility for a specific trait
  const toggleEvidence = (trait: string) => {
    setEvidenceVisibility(prev => ({
      ...prev,
      [trait]: !prev[trait]
    }));
  };

  // If no data, show empty state
  if (personaData.length === 0) {
    return (
      <Card className={cn("w-full", className)}>
        <CardHeader>
          <CardTitle>Personas</CardTitle>
          <CardDescription>
            No personas have been generated from the analysis yet.
          </CardDescription>
        </CardHeader>
      </Card>
    );
  }

  // Get initials for avatar
  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };

  // Get color based on confidence
  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800 dark:bg-green-800 dark:text-green-100';
    if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-800 dark:text-yellow-100';
    return 'bg-red-100 text-red-800 dark:bg-red-800 dark:text-red-100';
  };

  const getConfidenceTooltip = (confidence: number) => {
    if (confidence >= 0.9) return 'High confidence: Based on direct statements from the interview';
    if (confidence >= 0.7) return 'Good confidence: Based on strong evidence across multiple mentions';
    if (confidence >= 0.5) return 'Moderate confidence: Based on contextual clues';
    return 'Limited confidence: Based on inferences with minimal evidence';
  };

  return (
    <Card className={cn("w-full", className)}>
      <CardHeader>
        <CardTitle>Personas</CardTitle>
        <CardDescription>
          {personaData.length} persona{personaData.length !== 1 ? 's' : ''} generated from analysis
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Persona List Sidebar */}
          <div className="md:col-span-1 border rounded-lg p-2">
            <h3 className="text-sm font-medium mb-2">Personas</h3>
            <ScrollArea className="h-[400px]">
              <div className="space-y-2">
                {personaData.map((persona, index) => (
                  <Button
                    key={index}
                    variant={selectedPersona?.name === persona.name ? "secondary" : "ghost"}
                    className="w-full justify-start text-left h-auto py-2"
                    onClick={() => setSelectedPersona(persona)}
                  >
                    <Avatar className="h-6 w-6 mr-2 flex-shrink-0">
                      <AvatarFallback className="text-xs">
                        {getInitials(persona.name)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="overflow-hidden">
                      <div className="w-full break-words">
                        {persona.name}
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            </ScrollArea>
          </div>
          
          {/* Persona Details */}
          {selectedPersona && (
            <div className="md:col-span-3">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold">{selectedPersona.name}</h2>
                  <p className="text-muted-foreground">{selectedPersona.description}</p>
                </div>
                <Badge className={getConfidenceColor(selectedPersona.confidence)}>
                  {Math.round(selectedPersona.confidence * 100)}% Confidence
                  <Tooltip>{getConfidenceTooltip(selectedPersona.confidence)}</Tooltip>
                </Badge>
              </div>
              
              <Tabs defaultValue="overview">
                <TabsList className="mb-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="evidence">Evidence</TabsTrigger>
                </TabsList>
                
                <TabsContent value="overview" className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {/* Confidence Guide Panel */}
                    <Card className="col-span-1 md:col-span-2 bg-blue-50 dark:bg-blue-900/20">
                      <CardHeader className="p-4">
                        <CardTitle className="text-base">Confidence Score Guide</CardTitle>
                      </CardHeader>
                      <CardContent className="p-4 pt-0">
                        <div className="text-sm">
                          <p className="mb-2">Our confidence scores reflect the strength of evidence:</p>
                          <ul className="space-y-1 list-disc list-inside">
                            <li><strong>90-100%:</strong> Direct statements from interview</li>
                            <li><strong>70-80%:</strong> Strong evidence across multiple mentions</li>
                            <li><strong>50-60%:</strong> Contextual clues and moderate evidence</li>
                            <li><strong>&lt;50%:</strong> Limited evidence based on inferences</li>
                          </ul>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-base">Role Context</CardTitle>
                          <Badge variant="outline" className={getConfidenceColor(selectedPersona.role_context.confidence)} id="role-context-badge">
                            {Math.round(selectedPersona.role_context.confidence * 100)}%
                            <Tooltip anchorId="role-context-badge" place="top">
                              {getConfidenceTooltip(selectedPersona.role_context.confidence)}
                            </Tooltip>
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <p>{selectedPersona.role_context.value}</p>
                        
                        {selectedPersona.role_context.evidence.length > 0 && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-medium">Evidence:</h4>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => toggleEvidence('role_context')}
                                className="h-6 text-xs"
                              >
                                {evidenceVisibility['role_context'] ? 'Hide evidence' : 'Show evidence'}
                              </Button>
                            </div>
                            
                            {evidenceVisibility['role_context'] && (
                              <ul className="list-disc pl-5 mt-1 text-sm text-muted-foreground">
                                {selectedPersona.role_context.evidence.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-base">Key Responsibilities</CardTitle>
                          <Badge variant="outline" className={getConfidenceColor(selectedPersona.key_responsibilities.confidence)} id="key-responsibilities-badge">
                            {Math.round(selectedPersona.key_responsibilities.confidence * 100)}%
                            <Tooltip anchorId="key-responsibilities-badge" place="top">
                              {getConfidenceTooltip(selectedPersona.key_responsibilities.confidence)}
                            </Tooltip>
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <ul className="list-disc pl-5">
                          {selectedPersona.key_responsibilities.value.split('. ').filter(item => item.trim().length > 0).map((item, i) => (
                            <li key={i}>{item.trim()}</li>
                          ))}
                        </ul>
                        
                        {selectedPersona.key_responsibilities.evidence.length > 0 && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-medium">Evidence:</h4>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => toggleEvidence('key_responsibilities')}
                                className="h-6 text-xs"
                              >
                                {evidenceVisibility['key_responsibilities'] ? 'Hide evidence' : 'Show evidence'}
                              </Button>
                            </div>
                            
                            {evidenceVisibility['key_responsibilities'] && (
                              <ul className="list-disc pl-5 mt-1 text-sm text-muted-foreground">
                                {selectedPersona.key_responsibilities.evidence.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-base">Tools Used</CardTitle>
                          <Badge variant="outline" className={getConfidenceColor(selectedPersona.tools_used.confidence)} id="tools-used-badge">
                            {Math.round(selectedPersona.tools_used.confidence * 100)}%
                            <Tooltip anchorId="tools-used-badge" place="top">
                              {getConfidenceTooltip(selectedPersona.tools_used.confidence)}
                            </Tooltip>
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <ul className="list-disc pl-5">
                          {selectedPersona.tools_used.value.split(', ').filter(item => item.trim().length > 0).map((item, i) => (
                            <li key={i}>{item.trim()}</li>
                          ))}
                        </ul>
                        
                        {selectedPersona.tools_used.evidence.length > 0 && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-medium">Evidence:</h4>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => toggleEvidence('tools_used')}
                                className="h-6 text-xs"
                              >
                                {evidenceVisibility['tools_used'] ? 'Hide evidence' : 'Show evidence'}
                              </Button>
                            </div>
                            
                            {evidenceVisibility['tools_used'] && (
                              <ul className="list-disc pl-5 mt-1 text-sm text-muted-foreground">
                                {selectedPersona.tools_used.evidence.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-base">Pain Points</CardTitle>
                          <Badge variant="outline" className={getConfidenceColor(selectedPersona.pain_points.confidence)} id="pain-points-badge">
                            {Math.round(selectedPersona.pain_points.confidence * 100)}%
                            <Tooltip anchorId="pain-points-badge" place="top">
                              {getConfidenceTooltip(selectedPersona.pain_points.confidence)}
                            </Tooltip>
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <ul className="list-disc pl-5">
                          {selectedPersona.pain_points.value.split('. ').filter(item => item.trim().length > 0).map((item, i) => (
                            <li key={i}>{item.trim()}</li>
                          ))}
                        </ul>
                        
                        {selectedPersona.pain_points.evidence.length > 0 && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-medium">Evidence:</h4>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => toggleEvidence('pain_points')}
                                className="h-6 text-xs"
                              >
                                {evidenceVisibility['pain_points'] ? 'Hide evidence' : 'Show evidence'}
                              </Button>
                            </div>
                            
                            {evidenceVisibility['pain_points'] && (
                              <ul className="list-disc pl-5 mt-1 text-sm text-muted-foreground">
                                {selectedPersona.pain_points.evidence.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-base">Collaboration Style</CardTitle>
                          <Badge variant="outline" className={getConfidenceColor(selectedPersona.collaboration_style.confidence)} id="collaboration-style-badge">
                            {Math.round(selectedPersona.collaboration_style.confidence * 100)}%
                            <Tooltip anchorId="collaboration-style-badge" place="top">
                              {getConfidenceTooltip(selectedPersona.collaboration_style.confidence)}
                            </Tooltip>
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <ul className="list-disc pl-5">
                          {selectedPersona.collaboration_style.value.split('. ').filter(item => item.trim().length > 0).map((item, i) => (
                            <li key={i}>{item.trim()}</li>
                          ))}
                        </ul>
                        
                        {selectedPersona.collaboration_style.evidence.length > 0 && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-medium">Evidence:</h4>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => toggleEvidence('collaboration_style')}
                                className="h-6 text-xs"
                              >
                                {evidenceVisibility['collaboration_style'] ? 'Hide evidence' : 'Show evidence'}
                              </Button>
                            </div>
                            
                            {evidenceVisibility['collaboration_style'] && (
                              <ul className="list-disc pl-5 mt-1 text-sm text-muted-foreground">
                                {selectedPersona.collaboration_style.evidence.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <div className="flex justify-between items-center">
                          <CardTitle className="text-base">Analysis Approach</CardTitle>
                          <Badge variant="outline" className={getConfidenceColor(selectedPersona.analysis_approach.confidence)} id="analysis-approach-badge">
                            {Math.round(selectedPersona.analysis_approach.confidence * 100)}%
                            <Tooltip anchorId="analysis-approach-badge" place="top">
                              {getConfidenceTooltip(selectedPersona.analysis_approach.confidence)}
                            </Tooltip>
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <ul className="list-disc pl-5">
                          {selectedPersona.analysis_approach.value.split('. ').filter(item => item.trim().length > 0).map((item, i) => (
                            <li key={i}>{item.trim()}</li>
                          ))}
                        </ul>
                        
                        {selectedPersona.analysis_approach.evidence.length > 0 && (
                          <div className="mt-2">
                            <div className="flex items-center justify-between">
                              <h4 className="text-sm font-medium">Evidence:</h4>
                              <Button 
                                variant="ghost" 
                                size="sm" 
                                onClick={() => toggleEvidence('analysis_approach')}
                                className="h-6 text-xs"
                              >
                                {evidenceVisibility['analysis_approach'] ? 'Hide evidence' : 'Show evidence'}
                              </Button>
                            </div>
                            
                            {evidenceVisibility['analysis_approach'] && (
                              <ul className="list-disc pl-5 mt-1 text-sm text-muted-foreground">
                                {selectedPersona.analysis_approach.evidence.map((item, i) => (
                                  <li key={i}>{item}</li>
                                ))}
                              </ul>
                            )}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium mb-2">Common Patterns</h3>
                    {selectedPersona.patterns && selectedPersona.patterns.length > 0 ? (
                      <div className="flex flex-wrap gap-2">
                        {selectedPersona.patterns.map((pattern, index) => (
                          <Badge key={index} variant="outline">{pattern}</Badge>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No common patterns identified for this persona.</p>
                    )}
                  </div>
                </TabsContent>
                
                <TabsContent value="evidence">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-sm font-medium mb-2">Supporting Evidence</h3>
                      <ul className="list-disc pl-5 space-y-2">
                        {selectedPersona.evidence.map((item, index) => (
                          <li key={index}>{item}</li>
                        ))}
                      </ul>
                    </div>
                    
                    {selectedPersona.metadata && (
                      <div>
                        <h3 className="text-sm font-medium mb-2">Metadata</h3>
                        <div className="bg-muted p-3 rounded text-sm">
                          <p>Sample Size: {selectedPersona.metadata.sample_size || 'N/A'}</p>
                          {selectedPersona.metadata.timestamp && (
                            <p>Generated: {new Date(selectedPersona.metadata.timestamp).toLocaleString()}</p>
                          )}
                          {selectedPersona.metadata.validation_metrics && (
                            <>
                              <p>Pattern Confidence: {Math.round((selectedPersona.metadata.validation_metrics.pattern_confidence || 0) * 100)}%</p>
                              <p>Evidence Count: {selectedPersona.metadata.validation_metrics.evidence_count || 0}</p>
                            </>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </TabsContent>
              </Tabs>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default PersonaList; 