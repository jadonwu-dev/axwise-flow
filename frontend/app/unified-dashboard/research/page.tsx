'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import {
  MessageSquare,
  ArrowRight,
  Clock,
  Upload,
  Loader2,
  Download
} from 'lucide-react';
import { createSimulation, SimulationConfig, QuestionsData, BusinessContext, SimulationResponse } from '@/lib/api/simulation';

export default function ResearchDashboardPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const [completedSimulations, setCompletedSimulations] = useState<any[]>([]);
  const [lastSimulationResult, setLastSimulationResult] = useState<any>(null);

  // Load completed simulations on component mount
  useEffect(() => {
    loadCompletedSimulations();
  }, []);

  const loadCompletedSimulations = async () => {
    try {
      const response = await fetch('/api/research/simulation-bridge/completed');
      if (response.ok) {
        const data = await response.json();
        setCompletedSimulations(Object.values(data.simulations));
      }
    } catch (error) {
      console.error('Failed to load completed simulations:', error);
    }
  };

  const downloadInterviewsFromData = (result: any) => {
    try {
      // Generate clean interview TXT content
      const content = result.interviews.map((interview: any, index: number) => {
        const persona = result.personas?.find((p: any) => p.id === interview.persona_id);

        return `INTERVIEW ${index + 1}
================

Persona: ${persona?.name || 'Unknown'}
Stakeholder Type: ${interview.stakeholder_type}

RESPONSES:
----------

${interview.responses.map((response: any, i: number) => `Q${i + 1}: ${response.question}

A${i + 1}: ${response.response}
`).join('\n---\n')}

================
`;
      }).join('\n\n');

      // Download immediately
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `interviews_${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download interviews:', error);
    }
  };

  const downloadInterviewsDirectly = async (simulationId: string) => {
    try {
      const response = await fetch(`/api/research/simulation-bridge/completed/${simulationId}`);
      if (response.ok) {
        const result = await response.json();

        // Generate clean interview TXT content
        const content = result.interviews.map((interview: any, index: number) => {
          const persona = result.personas?.find((p: any) => p.id === interview.persona_id);

          return `INTERVIEW ${index + 1}
================

Persona: ${persona?.name || 'Unknown'}
Stakeholder Type: ${interview.stakeholder_type}

RESPONSES:
----------

${interview.responses.map((response: any, i: number) => `Q${i + 1}: ${response.question}

A${i + 1}: ${response.response}
`).join('\n---\n')}

================
`;
        }).join('\n\n');

        // Download immediately
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `interviews_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }
    } catch (error) {
      console.error('Failed to download interviews:', error);
    }
  };

  const handleFileUploadAndSimulate = async (file: File) => {
    const content = await file.text();

    // Send raw content directly to simulation bridge - it has PydanticAI to parse it
    const config: SimulationConfig = {
      depth: 'detailed',
      personas_per_stakeholder: 5,
      response_style: 'realistic',
      include_insights: true,
      temperature: 0.7
    };

    console.log('🚀 Sending raw questionnaire to simulation bridge');

    const result = await createSimulation(
      { raw_questionnaire_content: content }, // Send raw content
      { business_idea: '', target_customer: '', problem: '', industry: 'general' }, // Placeholder - bridge will parse
      config
    );

    return result;
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.type === 'text/plain') {
      setSelectedFile(file);
      setError(null);
      setSuccess(null);

      try {
        setIsProcessing(true);

        // Send file directly to simulation bridge - it will parse with PydanticAI
        try {
          const result = await handleFileUploadAndSimulate(file);

          if (result.success) {
            setLastSimulationResult(result);
            setSuccess(`Simulation completed! Generated ${result.interviews?.length || 0} interviews.`);
            console.log('Simulation result:', result);

            // Auto-download interviews immediately from the result data
            if (result.interviews && result.interviews.length > 0) {
              downloadInterviewsFromData(result);
            }

            // Refresh completed simulations list
            await loadCompletedSimulations();
          } else {
            setError(result.message || 'Simulation failed');
          }
        } catch (error: any) {
          if (error.message.includes('fetch')) {
            // Likely a timeout - simulation might still be running
            setSuccess('Simulation started! It may take a few minutes to complete. Check the "Completed Simulations" section below.');
            // Refresh completed simulations list
            await loadCompletedSimulations();
          } else {
            setError(error.message || 'Simulation failed');
          }
        }
      } catch (err) {
        console.error('Simulation error:', err);
        setError(err instanceof Error ? err.message : 'Failed to process file and start simulation');
      } finally {
        setIsProcessing(false);
      }
    } else {
      setError('Please select a valid TXT file');
    }
  };

  const handleStartSimulation = async (sessionId?: string) => {
    try {
      setIsProcessing(true);
      setError(null);
      setSuccess(null);

      // TODO: Load session data and start simulation
      console.log('Starting simulation with session:', sessionId);

      // For now, show a placeholder message
      setSuccess('Session simulation feature coming soon!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start simulation');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Interview Simulation</h1>
        <p className="text-muted-foreground">
          Generate AI persona interviews from your research sessions
        </p>
      </div>

      {/* Simplified Simulation Bridge Interface */}
      <div className="max-w-4xl mx-auto space-y-6">

        {/* Upload Questionnaire Section */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2">
              <Upload className="h-6 w-6" />
              Option 1: Upload Questionnaire File
            </CardTitle>
            <CardDescription>
              Have a questionnaire file ready? Upload it to start AI persona interviews immediately
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="border-2 border-dashed border-muted-foreground/25 rounded-lg p-8 text-center">
              <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="text-lg font-medium mb-2">Upload Questionnaire File</h3>
              <p className="text-sm text-muted-foreground mb-4">
                Upload your TXT questionnaire file to automatically start simulation
              </p>
              <input
                type="file"
                accept=".txt"
                onChange={handleFileUpload}
                className="hidden"
                id="questionnaire-upload"
              />
              <label htmlFor="questionnaire-upload">
                <Button className="mb-2" disabled={isProcessing} asChild>
                  <span>
                    {isProcessing ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>
                        <Upload className="mr-2 h-4 w-4" />
                        Select TXT File
                      </>
                    )}
                  </span>
                </Button>
              </label>

              {selectedFile && !isProcessing && (
                <p className="text-sm text-green-600 mt-2">
                  Selected: {selectedFile.name}
                </p>
              )}

              {error && (
                <div className="mt-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-600">{error}</p>
                </div>
              )}

              {success && (
                <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-sm text-green-600">{success}</p>
                  {lastSimulationResult && (
                    <Button
                      onClick={() => downloadInterviewsFromData(lastSimulationResult)}
                      variant="outline"
                      size="sm"
                      className="mt-2"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download Interviews
                    </Button>
                  )}
                </div>
              )}

              <p className="text-xs text-muted-foreground">
                Supports TXT files with stakeholder questions
              </p>
            </div>
          </CardContent>
        </Card>

        {/* OR Divider */}
        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t" />
          </div>
          <div className="relative flex justify-center text-xs uppercase">
            <span className="bg-background px-2 text-muted-foreground">Or</span>
          </div>
        </div>

        {/* Recent Sessions Section */}
        <Card>
          <CardHeader>
            <CardTitle className="text-xl flex items-center gap-2">
              <Clock className="h-6 w-6" />
              Option 2: Use Recent Research Session
            </CardTitle>
            <CardDescription>
              Select from questionnaires you've already created in Research Chat
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 cursor-pointer">
                <div className="flex-1">
                  <h4 className="font-medium">API service for legacy source systems</h4>
                  <p className="text-sm text-muted-foreground">
                    Account managers • 34 questions • 5 stakeholders
                  </p>
                  <p className="text-xs text-muted-foreground">Generated today at 4:17 PM</p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={isProcessing}
                  onClick={() => handleStartSimulation('session-1')}
                >
                  {isProcessing ? (
                    <>
                      <Loader2 className="h-4 w-4 mr-1 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <ArrowRight className="h-4 w-4 mr-1" />
                      Start Simulation
                    </>
                  )}
                </Button>
              </div>

              <div className="text-center py-4">
                <Button variant="ghost" size="sm">
                  <Clock className="mr-2 h-4 w-4" />
                  View All Sessions
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Need to Create Questions?</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-3">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => window.location.href = '/customer-research'}
              >
                <MessageSquare className="mr-2 h-4 w-4" />
                Start Research Chat
              </Button>
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => window.location.href = '/research-dashboard'}
              >
                <Clock className="mr-2 h-4 w-4" />
                View All Sessions
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Completed Simulations */}
        {completedSimulations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Completed Simulations</CardTitle>
              <CardDescription>
                Previous simulation results available for download
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {completedSimulations.map((sim: any) => (
                  <div key={sim.simulation_id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium">
                        {sim.total_personas} personas, {sim.total_interviews} interviews
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {sim.created_at ? new Date(sim.created_at).toLocaleString() : 'Recently completed'}
                      </div>
                    </div>
                    <Button
                      onClick={() => downloadInterviewsDirectly(sim.simulation_id)}
                      variant="outline"
                      size="sm"
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Download Interviews
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>


    </div>
  );
}
