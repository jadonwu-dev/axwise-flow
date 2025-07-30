'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, Play, Eye } from 'lucide-react';

export default function FindApiSessionPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [simulations, setSimulations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = () => {
    try {
      setLoading(true);
      setError(null);

      // Load all sessions
      const sessionsData = JSON.parse(localStorage.getItem('axwise_research_sessions') || '{}');
      const sessionsList = Object.values(sessionsData);

      // Load all simulations
      const simulationsData = JSON.parse(localStorage.getItem('simulation_results') || '[]');

      setSessions(sessionsList);
      setSimulations(simulationsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const runSimulationForSession = async (sessionId: string) => {
    try {
      const session = sessions.find((s: any) => s.session_id === sessionId);
      if (!session) {
        alert('Session not found');
        return;
      }

      // Check if session has questionnaire
      const questionnaireMessage = session.messages?.find((msg: any) =>
        msg.metadata?.comprehensiveQuestions
      );

      if (!questionnaireMessage) {
        alert('No questionnaire data found in this session');
        return;
      }

      const questionnaire = questionnaireMessage.metadata.comprehensiveQuestions;

      // Transform data for API (same as our working test)
      const transformStakeholder = (stakeholder: any, index: number) => ({
        id: stakeholder.id || `stakeholder_${index}`,
        name: stakeholder.name || stakeholder.title || `Stakeholder ${index + 1}`,
        description: stakeholder.description || stakeholder.role || '',
        questions: [
          ...(stakeholder.questions?.problemDiscovery || []),
          ...(stakeholder.questions?.solutionValidation || []),
          ...(stakeholder.questions?.followUp || [])
        ]
      });

      // Handle timeEstimate properly
      let timeEstimate = null;
      if (questionnaire.timeEstimate) {
        if (typeof questionnaire.timeEstimate === 'object') {
          timeEstimate = questionnaire.timeEstimate;
        } else if (typeof questionnaire.timeEstimate === 'string') {
          timeEstimate = {
            estimatedTime: questionnaire.timeEstimate,
            totalQuestions: 0
          };
        }
      }

      const questionnaireData = {
        stakeholders: {
          primary: (questionnaire.primaryStakeholders || []).map(transformStakeholder),
          secondary: (questionnaire.secondaryStakeholders || []).map(transformStakeholder)
        },
        timeEstimate: timeEstimate
      };

      const businessContext = {
        business_idea: session.business_idea || '',
        target_customer: session.target_customer || '',
        problem: session.problem || '',
        industry: 'general'
      };

      const config = {
        depth: "detailed",
        people_per_stakeholder: 5,
        response_style: "realistic",
        include_insights: false,
        temperature: 0.7
      };

      console.log('🚀 Starting simulation for session:', sessionId);
      console.log('📊 Business Context:', businessContext);

      const response = await fetch('/api/research/simulation-bridge/simulate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          questions_data: questionnaireData,
          business_context: businessContext,
          config: config
        })
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Simulation successful:', result);

        // Save to localStorage
        const existingResults = JSON.parse(localStorage.getItem('simulation_results') || '[]');
        const newSimulationEntry = {
          simulation_id: result.simulation_id,
          timestamp: new Date().toISOString(),
          results: result,
          source: 'debug_api_session_finder'
        };
        existingResults.push(newSimulationEntry);
        localStorage.setItem('simulation_results', JSON.stringify(existingResults));

        alert(`✅ Simulation Successful!\nSimulation ID: ${result.simulation_id}\nBusiness Idea: ${businessContext.business_idea}\nInterviews: ${(result.interviews || result.data?.interviews || []).length}\n\nCheck the simulation history page!`);

        // Refresh data to show new simulation
        loadData();
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Simulation failed:', errorData);
        alert(`❌ Simulation failed (${response.status}): ${JSON.stringify(errorData, null, 2)}`);
      }

    } catch (error) {
      console.error('❌ Error:', error);
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Loading session data...
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <Card>
            <CardContent className="p-6">
              <div className="text-red-600">
                <h3 className="font-semibold mb-2">Error Loading Data</h3>
                <p>{error}</p>
                <Button onClick={loadData} className="mt-4">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Retry
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  // Find API service sessions
  const apiServiceSessions = sessions.filter((session: any) => 
    session.business_idea && (
      session.business_idea.toLowerCase().includes('api') ||
      session.business_idea.toLowerCase().includes('legacy') ||
      session.business_idea.toLowerCase().includes('sales order')
    )
  );

  // Find API service simulations
  const apiServiceSimulations = simulations.filter((sim: any) => {
    const businessIdea = sim.results?.business_context?.business_idea || 
                        sim.results?.data?.business_context?.business_idea || '';
    return businessIdea.toLowerCase().includes('api') ||
           businessIdea.toLowerCase().includes('legacy') ||
           businessIdea.toLowerCase().includes('sales order');
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">🔍 Find API Service Session</CardTitle>
            <div className="text-sm text-muted-foreground">
              <p>Searching for sessions and simulations related to "API service to pull legacy sales order data"</p>
            </div>
          </CardHeader>
        </Card>

        {/* API Service Sessions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              📋 API Service Sessions ({apiServiceSessions.length} found)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {apiServiceSessions.length > 0 ? (
              <div className="space-y-4">
                {apiServiceSessions.map((session: any, index: number) => {
                  const hasQuestionnaire = session.messages?.some((msg: any) =>
                    msg.metadata?.comprehensiveQuestions
                  );

                  return (
                    <div key={session.session_id} className="p-4 border rounded-lg bg-green-50 border-green-200">
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <h4 className="font-semibold text-green-800 mb-2">
                            🎯 API Service Session {index + 1}
                          </h4>
                          <div className="space-y-1 text-sm">
                            <p><strong>Session ID:</strong> {session.session_id}</p>
                            <p><strong>Business Idea:</strong> {session.business_idea}</p>
                            <p><strong>Target Customer:</strong> {session.target_customer || 'None'}</p>
                            <p><strong>Problem:</strong> {session.problem || 'None'}</p>
                            <p><strong>Has Questionnaire:</strong> {hasQuestionnaire ? '✅ Yes' : '❌ No'}</p>
                            <p><strong>Created:</strong> {session.created_at ? new Date(session.created_at).toLocaleString() : 'Unknown'}</p>
                          </div>
                        </div>
                        <div className="flex gap-2 ml-4">
                          <Button
                            onClick={() => window.open(`/unified-dashboard/questionnaire/${session.session_id}`, '_blank')}
                            variant="outline"
                            size="sm"
                            disabled={!hasQuestionnaire}
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            View
                          </Button>
                          <Button
                            onClick={() => runSimulationForSession(session.session_id)}
                            variant="default"
                            size="sm"
                            disabled={!hasQuestionnaire}
                          >
                            <Play className="h-4 w-4 mr-2" />
                            Run Simulation
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <h4 className="font-semibold text-yellow-800 mb-2">⚠️ No API Service Sessions Found</h4>
                <p className="text-yellow-700">No sessions found with "API", "legacy", or "sales order" in the business idea.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* API Service Simulations */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              🚀 API Service Simulations ({apiServiceSimulations.length} found)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {apiServiceSimulations.length > 0 ? (
              <div className="space-y-4">
                {apiServiceSimulations.map((sim: any, index: number) => {
                  const businessIdea = sim.results?.business_context?.business_idea || 'Unknown';
                  const interviews = sim.results?.interviews || sim.results?.data?.interviews || [];

                  return (
                    <div key={sim.simulation_id} className="p-4 border rounded-lg bg-blue-50 border-blue-200">
                      <h4 className="font-semibold text-blue-800 mb-2">
                        ✅ API Service Simulation {index + 1}
                      </h4>
                      <div className="space-y-1 text-sm">
                        <p><strong>Simulation ID:</strong> {sim.simulation_id}</p>
                        <p><strong>Business Idea:</strong> {businessIdea}</p>
                        <p><strong>Interviews:</strong> {interviews.length}</p>
                        <p><strong>Created:</strong> {sim.timestamp ? new Date(sim.timestamp).toLocaleString() : 'Unknown'}</p>
                        <p><strong>Source:</strong> {sim.source || 'Unknown'}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-semibold text-red-800 mb-2">❌ No API Service Simulations Found</h4>
                <p className="text-red-700">No simulations found with API service content.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* All Sessions Summary */}
        <Card>
          <CardHeader>
            <CardTitle>📊 All Sessions Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p><strong>Total Sessions:</strong> {sessions.length}</p>
              <p><strong>API Service Sessions:</strong> {apiServiceSessions.length}</p>
              <p><strong>Total Simulations:</strong> {simulations.length}</p>
              <p><strong>API Service Simulations:</strong> {apiServiceSimulations.length}</p>
            </div>

            <div className="mt-4">
              <h4 className="font-semibold mb-2">Recent Sessions (by business idea):</h4>
              <div className="space-y-1 text-sm max-h-40 overflow-y-auto">
                {sessions.slice(0, 10).map((session: any) => (
                  <div key={session.session_id} className="flex justify-between">
                    <span className="truncate flex-1 mr-2">{session.business_idea || 'No business idea'}</span>
                    <span className="text-muted-foreground">{session.session_id}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex gap-2 mt-4">
              <Button onClick={loadData} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Data
              </Button>
              <Button onClick={() => window.open('/unified-dashboard/research', '_blank')} variant="outline">
                Open Research Page
              </Button>
              <Button onClick={() => window.open('/unified-dashboard/simulation-history', '_blank')} variant="outline">
                Open Simulation History
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
