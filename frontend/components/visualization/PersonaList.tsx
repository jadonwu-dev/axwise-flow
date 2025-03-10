'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cn } from '@/lib/utils';

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
                    className="w-full justify-start"
                    onClick={() => setSelectedPersona(persona)}
                  >
                    <Avatar className="h-6 w-6 mr-2">
                      <AvatarFallback className="text-xs">
                        {getInitials(persona.name)}
                      </AvatarFallback>
                    </Avatar>
                    <div className="truncate text-left">
                      {persona.name}
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
                </Badge>
              </div>
              
              <Tabs defaultValue="overview">
                <TabsList className="mb-4">
                  <TabsTrigger value="overview">Overview</TabsTrigger>
                  <TabsTrigger value="attributes">Attributes</TabsTrigger>
                  <TabsTrigger value="evidence">Evidence</TabsTrigger>
                </TabsList>
                
                <TabsContent value="overview" className="space-y-4">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader className="py-3">
                        <CardTitle className="text-base">Role Context</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p>{selectedPersona.role_context.value}</p>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader className="py-3">
                        <CardTitle className="text-base">Key Responsibilities</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p>{selectedPersona.key_responsibilities.value}</p>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader className="py-3">
                        <CardTitle className="text-base">Tools Used</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p>{selectedPersona.tools_used.value}</p>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader className="py-3">
                        <CardTitle className="text-base">Pain Points</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p>{selectedPersona.pain_points.value}</p>
                      </CardContent>
                    </Card>
                  </div>
                  
                  <div>
                    <h3 className="text-sm font-medium mb-2">Common Patterns</h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedPersona.patterns.map((pattern, index) => (
                        <Badge key={index} variant="outline">{pattern}</Badge>
                      ))}
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="attributes">
                  <Accordion type="single" collapsible className="w-full">
                    <AccordionItem value="role">
                      <AccordionTrigger>
                        <div className="flex justify-between w-full pr-4">
                          <span>Role Context</span>
                          <Badge className={getConfidenceColor(selectedPersona.role_context.confidence)}>
                            {Math.round(selectedPersona.role_context.confidence * 100)}%
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <p className="mb-2">{selectedPersona.role_context.value}</p>
                        <h4 className="text-sm font-medium mb-1">Evidence:</h4>
                        <ul className="list-disc pl-5 text-sm text-muted-foreground">
                          {selectedPersona.role_context.evidence.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </AccordionContent>
                    </AccordionItem>
                    
                    <AccordionItem value="responsibilities">
                      <AccordionTrigger>
                        <div className="flex justify-between w-full pr-4">
                          <span>Key Responsibilities</span>
                          <Badge className={getConfidenceColor(selectedPersona.key_responsibilities.confidence)}>
                            {Math.round(selectedPersona.key_responsibilities.confidence * 100)}%
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <p className="mb-2">{selectedPersona.key_responsibilities.value}</p>
                        <h4 className="text-sm font-medium mb-1">Evidence:</h4>
                        <ul className="list-disc pl-5 text-sm text-muted-foreground">
                          {selectedPersona.key_responsibilities.evidence.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </AccordionContent>
                    </AccordionItem>
                    
                    <AccordionItem value="tools">
                      <AccordionTrigger>
                        <div className="flex justify-between w-full pr-4">
                          <span>Tools Used</span>
                          <Badge className={getConfidenceColor(selectedPersona.tools_used.confidence)}>
                            {Math.round(selectedPersona.tools_used.confidence * 100)}%
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <p className="mb-2">{selectedPersona.tools_used.value}</p>
                        <h4 className="text-sm font-medium mb-1">Evidence:</h4>
                        <ul className="list-disc pl-5 text-sm text-muted-foreground">
                          {selectedPersona.tools_used.evidence.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </AccordionContent>
                    </AccordionItem>
                    
                    <AccordionItem value="collaboration">
                      <AccordionTrigger>
                        <div className="flex justify-between w-full pr-4">
                          <span>Collaboration Style</span>
                          <Badge className={getConfidenceColor(selectedPersona.collaboration_style.confidence)}>
                            {Math.round(selectedPersona.collaboration_style.confidence * 100)}%
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <p className="mb-2">{selectedPersona.collaboration_style.value}</p>
                        <h4 className="text-sm font-medium mb-1">Evidence:</h4>
                        <ul className="list-disc pl-5 text-sm text-muted-foreground">
                          {selectedPersona.collaboration_style.evidence.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </AccordionContent>
                    </AccordionItem>
                    
                    <AccordionItem value="analysis">
                      <AccordionTrigger>
                        <div className="flex justify-between w-full pr-4">
                          <span>Analysis Approach</span>
                          <Badge className={getConfidenceColor(selectedPersona.analysis_approach.confidence)}>
                            {Math.round(selectedPersona.analysis_approach.confidence * 100)}%
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <p className="mb-2">{selectedPersona.analysis_approach.value}</p>
                        <h4 className="text-sm font-medium mb-1">Evidence:</h4>
                        <ul className="list-disc pl-5 text-sm text-muted-foreground">
                          {selectedPersona.analysis_approach.evidence.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </AccordionContent>
                    </AccordionItem>
                    
                    <AccordionItem value="pain">
                      <AccordionTrigger>
                        <div className="flex justify-between w-full pr-4">
                          <span>Pain Points</span>
                          <Badge className={getConfidenceColor(selectedPersona.pain_points.confidence)}>
                            {Math.round(selectedPersona.pain_points.confidence * 100)}%
                          </Badge>
                        </div>
                      </AccordionTrigger>
                      <AccordionContent>
                        <p className="mb-2">{selectedPersona.pain_points.value}</p>
                        <h4 className="text-sm font-medium mb-1">Evidence:</h4>
                        <ul className="list-disc pl-5 text-sm text-muted-foreground">
                          {selectedPersona.pain_points.evidence.map((item, i) => (
                            <li key={i}>{item}</li>
                          ))}
                        </ul>
                      </AccordionContent>
                    </AccordionItem>
                  </Accordion>
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