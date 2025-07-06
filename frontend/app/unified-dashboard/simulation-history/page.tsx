'use client';

import React, { useEffect, useState, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Loader2, FlaskConical, Download } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { useRouter } from 'next/navigation';
import { useToast } from '@/components/providers/toast-provider';

interface SimulationResult {
  id: string;
  displayName: string;
  createdAt: string;
  status: string;
  totalPersonas: number;
  totalInterviews: number;
}

export default function SimulationHistoryPage(): JSX.Element {
  const router = useRouter();
  const { showToast } = useToast();

  const [simulationHistory, setSimulationHistory] = useState<SimulationResult[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  // Fetch simulation history
  const fetchSimulationHistory = useCallback(async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/research/simulation-bridge/completed');

      if (response.ok) {
        const data = await response.json();

        // Convert simulation data to history format
        const simulations = Object.values(data.simulations || {}).map((sim: any) => ({
          id: sim.simulation_id,
          displayName: `Simulation ${sim.simulation_id.slice(0, 8)}`,
          createdAt: sim.created_at || new Date().toISOString(),
          status: sim.success ? 'completed' : 'failed',
          totalPersonas: sim.total_personas || 0,
          totalInterviews: sim.total_interviews || 0,
        }));

        // Sort by creation date (newest first)
        simulations.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime());

        setSimulationHistory(simulations);
      } else {
        const errorText = await response.text();
        setError(new Error(`Failed to load simulation history: ${errorText}`));
      }
    } catch (err) {
      console.error('Error fetching simulation history:', err);
      setError(err instanceof Error ? err : new Error('Failed to load simulation history'));
      showToast('Failed to load simulation history', { variant: 'error' });
    } finally {
      setIsLoading(false);
    }
  }, [showToast]);

  useEffect(() => {
    fetchSimulationHistory();
  }, [fetchSimulationHistory]);

  // Handle download for simulations
  const handleDownload = async (simulationId: string) => {
    try {
      const response = await fetch(`/api/research/simulation-bridge/completed/${simulationId}`);

      if (!response.ok) {
        throw new Error(`Download failed: ${response.statusText}`);
      }

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
      a.download = `simulation_interviews_${simulationId.slice(0, 8)}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      showToast('Interviews downloaded successfully', { variant: 'success' });
    } catch (error) {
      console.error('Download failed:', error);
      showToast('Failed to download interviews', { variant: 'error' });
    }
  };

  // Get status badge
  const getStatusBadge = (status: string): JSX.Element => {
    switch (status) {
      case 'completed':
        return <Badge variant="secondary">Completed</Badge>;
      case 'pending':
        return <Badge variant="outline">Pending</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <Card className="w-full">
        <CardContent className="flex justify-center items-center py-12">
          <div className="flex flex-col items-center space-y-4">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
            <p className="text-muted-foreground">Loading simulation history...</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Error state
  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>Error Loading Simulation History</AlertTitle>
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FlaskConical className="h-5 w-5" />
          Interview Simulation History
        </CardTitle>
        <CardDescription>
          View and download your AI persona interview simulations
        </CardDescription>
      </CardHeader>

      <CardContent>
        {simulationHistory.length > 0 ? (
          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Simulation</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead className="hidden md:table-cell">Status</TableHead>
                  <TableHead className="hidden md:table-cell">Personas</TableHead>
                  <TableHead className="hidden md:table-cell">Interviews</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {simulationHistory.map((simulation) => (
                  <TableRow key={simulation.id}>
                    <TableCell className="font-medium">
                      <div className="flex items-center gap-2">
                        <FlaskConical className="h-4 w-4 text-muted-foreground" />
                        {simulation.displayName}
                      </div>
                    </TableCell>
                    <TableCell>
                      {new Date(simulation.createdAt).toLocaleDateString()}
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                      {getStatusBadge(simulation.status)}
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                      <Badge variant="outline">{simulation.totalPersonas}</Badge>
                    </TableCell>
                    <TableCell className="hidden md:table-cell">
                      <Badge variant="outline">{simulation.totalInterviews}</Badge>
                    </TableCell>
                    <TableCell className="text-right">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleDownload(simulation.id)}
                        disabled={simulation.status !== 'completed'}
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        ) : (
          <div className="text-center py-8 border rounded-md">
            <FlaskConical className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <p className="text-muted-foreground">No simulations found.</p>
            <p className="text-sm text-muted-foreground mt-1">
              Upload questionnaire files to run AI persona interview simulations.
            </p>
            <Button
              className="mt-4"
              onClick={() => router.push('/unified-dashboard/research')}
            >
              Start Simulation
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
