'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, Play, Search, AlertTriangle, CheckCircle } from 'lucide-react';

export default function FindAndFixPage() {
  const [sessions, setSessions] = useState<any[]>([]);
  const [apiSessions, setApiSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);
  const [results, setResults] = useState<any[]>([]);

  const loadAndAnalyzeSessions = () => {
    try {
      setLoading(true);

      // Load all sessions
      const sessionsData = JSON.parse(localStorage.getItem('axwise_research_sessions') || '{}');
      const sessionsList = Object.values(sessionsData);

      // Find API service sessions
      const apiServiceSessions = sessionsList.filter((session: any) => {
        const businessIdea = session.business_idea || '';
        return businessIdea.toLowerCase().includes('api') ||
               businessIdea.toLowerCase().includes('legacy') ||
               businessIdea.toLowerCase().includes('sales order') ||
               businessIdea.toLowerCase().includes('pull') ||
               businessIdea.toLowerCase().includes('data');
      });

      // Analyze each API session
      const analyzedApiSessions = apiServiceSessions.map((session: any) => {
        const questionnaireMessage = session.messages?.find((msg: any) =>
          msg.metadata?.comprehensiveQuestions ||
          (msg.content === 'COMPREHENSIVE_QUESTIONS_COMPONENT' && msg.metadata?.comprehensiveQuestions)
        );

        let stakeholderAnalysis = null;
        if (questionnaireMessage) {
          const questionnaire = questionnaireMessage.metadata.comprehensiveQuestions;
          const allStakeholders = [
            ...(questionnaire.primaryStakeholders || []),
            ...(questionnaire.secondaryStakeholders || [])
          ];

          stakeholderAnalysis = {
            total: allStakeholders.length,
            primary: questionnaire.primaryStakeholders?.length || 0,
            secondary: questionnaire.secondaryStakeholders?.length || 0,
            names: allStakeholders.map((s: any) => s.name || s.title || 'Unknown'),
            hasCaregiver: allStakeholders.some((s: any) =>
              (s.name || s.title || '').toLowerCase().includes('caregiver') ||
              (s.name || s.title || '').toLowerCase().includes('adult child')
            ),
            isApiRelated: allStakeholders.some((s: any) =>
              (s.name || s.title || '').toLowerCase().includes('developer') ||
              (s.name || s.title || '').toLowerCase().includes('technical') ||
              (s.name || s.title || '').toLowerCase().includes('integration') ||
              (s.name || s.title || '').toLowerCase().includes('system')
            )
          };
        }

        return {
          ...session,
          hasQuestionnaire: !!questionnaireMessage,
          stakeholderAnalysis
        };
      });

      setSessions(sessionsList);
      setApiSessions(analyzedApiSessions);

      console.log('📊 Total sessions:', sessionsList.length);
      console.log('🎯 API service sessions:', analyzedApiSessions.length);
      console.log('📋 API sessions details:', analyzedApiSessions);

    } catch (error) {
      console.error('Error loading sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const runCorrectSimulation = async (sessionId: string) => {
    try {
      setProcessing(sessionId);

      const session = sessions.find((s: any) => s.session_id === sessionId);
      if (!session) {
        alert('❌ Session not found');
        return;
      }

      console.log('🚀 Running simulation for session:', sessionId);
      console.log('📊 Session business idea:', session.business_idea);

      // Get questionnaire data
      const questionnaireMessage = session.messages?.find((msg: any) =>
        msg.metadata?.comprehensiveQuestions
      );

      if (!questionnaireMessage) {
        alert('❌ No questionnaire data found');
        return;
      }

      const questionnaire = questionnaireMessage.metadata.comprehensiveQuestions;
      console.log('📋 Raw questionnaire:', questionnaire);

      // Transform stakeholders (same logic as working test)
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

      console.log('📤 Sending request:', {
        questions_data: questionnaireData,
        business_context: businessContext,
        config: config
      });

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
          source: 'find_and_fix_tool'
        };
        existingResults.push(newSimulationEntry);
        localStorage.setItem('simulation_results', JSON.stringify(existingResults));

        // Add to results
        setResults(prev => [...prev, {
          sessionId,
          simulationId: result.simulation_id,
          businessIdea: businessContext.business_idea,
          interviewCount: (result.interviews || result.data?.interviews || []).length,
          success: true,
          timestamp: new Date().toISOString()
        }]);

        alert(`✅ SUCCESS!\n\nSimulation ID: ${result.simulation_id}\nBusiness Idea: ${businessContext.business_idea}\nInterviews: ${(result.interviews || result.data?.interviews || []).length}\n\nThis is your CORRECT API service simulation!\nCheck simulation history to view results.`);

      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('❌ Simulation failed:', errorData);

        setResults(prev => [...prev, {
          sessionId,
          simulationId: null,
          businessIdea: session.business_idea,
          interviewCount: 0,
          success: false,
          error: JSON.stringify(errorData),
          timestamp: new Date().toISOString()
        }]);

        alert(`❌ Simulation failed:\n${JSON.stringify(errorData, null, 2)}`);
      }

    } catch (error) {
      console.error('❌ Error:', error);
      alert(`❌ Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setProcessing(null);
    }
  };

  useEffect(() => {
    loadAndAnalyzeSessions();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Finding API service sessions...
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <Search className="h-6 w-6" />
              Find & Fix API Service Session
            </CardTitle>
            <div className="text-sm text-muted-foreground">
              <p>Finding the real API service session and running the correct simulation</p>
            </div>
          </CardHeader>
        </Card>

        {/* Summary */}
        <Card>
          <CardHeader>
            <CardTitle>📊 Analysis Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-3 gap-4">
              <div className="p-4 bg-blue-50 border border-blue-200 rounded text-center">
                <div className="text-2xl font-bold text-blue-600">{sessions.length}</div>
                <div className="text-sm text-blue-700">Total Sessions</div>
              </div>
              <div className="p-4 bg-green-50 border border-green-200 rounded text-center">
                <div className="text-2xl font-bold text-green-600">{apiSessions.length}</div>
                <div className="text-sm text-green-700">API Service Sessions</div>
              </div>
              <div className="p-4 bg-purple-50 border border-purple-200 rounded text-center">
                <div className="text-2xl font-bold text-purple-600">{results.filter(r => r.success).length}</div>
                <div className="text-sm text-purple-700">Successful Simulations</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* API Service Sessions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              🎯 API Service Sessions Found ({apiSessions.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {apiSessions.length > 0 ? (
              <div className="space-y-4">
                {apiSessions.map((session: any, index: number) => {
                  const isProcessing = processing === session.session_id;
                  const hasCorrectStakeholders = session.stakeholderAnalysis?.isApiRelated;
                  const hasWrongStakeholders = session.stakeholderAnalysis?.hasCaregiver;

                  return (
                    <div key={session.session_id} className={`p-4 border rounded-lg ${
                      hasCorrectStakeholders ? 'bg-green-50 border-green-200' :
                      hasWrongStakeholders ? 'bg-red-50 border-red-200' :
                      'bg-yellow-50 border-yellow-200'
                    }`}>
                      <div className="flex justify-between items-start">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h4 className="font-semibold">
                              {hasCorrectStakeholders ? '✅' : hasWrongStakeholders ? '❌' : '⚠️'}
                              API Session {index + 1}
                            </h4>
                            {hasCorrectStakeholders && <CheckCircle className="h-4 w-4 text-green-600" />}
                            {hasWrongStakeholders && <AlertTriangle className="h-4 w-4 text-red-600" />}
                          </div>

                          <div className="space-y-1 text-sm">
                            <p><strong>Session ID:</strong> {session.session_id}</p>
                            <p><strong>Business Idea:</strong> {session.business_idea}</p>
                            <p><strong>Target Customer:</strong> {session.target_customer || 'None'}</p>
                            <p><strong>Problem:</strong> {session.problem || 'None'}</p>
                            <p><strong>Has Questionnaire:</strong> {session.hasQuestionnaire ? '✅ Yes' : '❌ No'}</p>

                            {session.stakeholderAnalysis && (
                              <div className="mt-2 p-2 bg-white rounded border">
                                <p><strong>Stakeholders ({session.stakeholderAnalysis.total}):</strong></p>
                                <ul className="list-disc list-inside text-xs ml-2">
                                  {session.stakeholderAnalysis.names.map((name: string, i: number) => (
                                    <li key={i}>{name}</li>
                                  ))}
                                </ul>
                                <div className="mt-1 text-xs">
                                  {hasCorrectStakeholders && <span className="text-green-600">✅ API-related stakeholders</span>}
                                  {hasWrongStakeholders && <span className="text-red-600">❌ Has caregiver stakeholders (wrong)</span>}
                                </div>
                              </div>
                            )}
                          </div>
                        </div>

                        <div className="flex gap-2 ml-4">
                          <Button
                            onClick={() => runCorrectSimulation(session.session_id)}
                            disabled={!session.hasQuestionnaire || isProcessing}
                            variant={hasCorrectStakeholders ? "default" : "outline"}
                            size="sm"
                          >
                            {isProcessing ? (
                              <>
                                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                                Processing...
                              </>
                            ) : (
                              <>
                                <Play className="h-4 w-4 mr-2" />
                                Run Simulation
                              </>
                            )}
                          </Button>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-4 bg-red-50 border border-red-200 rounded">
                <h4 className="font-semibold text-red-800 mb-2">❌ No API Service Sessions Found</h4>
                <p className="text-red-700">No sessions found with API, legacy, sales order, or data-related keywords.</p>
                <p className="text-red-700 mt-2">The API service session might have been overwritten or lost.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Results */}
        {results.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>🚀 Simulation Results</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {results.map((result, index) => (
                  <div key={index} className={`p-3 border rounded ${
                    result.success ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
                  }`}>
                    <div className="flex justify-between items-start">
                      <div>
                        <p><strong>{result.success ? '✅' : '❌'} {result.businessIdea}</strong></p>
                        <p className="text-sm text-muted-foreground">
                          Session: {result.sessionId} |
                          {result.success ? ` Simulation: ${result.simulationId} | Interviews: ${result.interviewCount}` : ` Error: ${result.error}`}
                        </p>
                        <p className="text-xs text-muted-foreground">{new Date(result.timestamp).toLocaleString()}</p>
                      </div>
                      {result.success && (
                        <Button
                          onClick={() => window.open('/unified-dashboard/simulation-history', '_blank')}
                          variant="outline"
                          size="sm"
                        >
                          View Results
                        </Button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle>🔧 Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 flex-wrap">
              <Button onClick={loadAndAnalyzeSessions} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Analysis
              </Button>
              <Button onClick={() => window.open('/unified-dashboard/simulation-history', '_blank')} variant="outline">
                View Simulation History
              </Button>
              <Button onClick={() => window.open('/unified-dashboard/research', '_blank')} variant="outline">
                Open Research Page
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
