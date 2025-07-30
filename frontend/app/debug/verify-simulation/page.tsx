'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Download, Eye, RefreshCw } from 'lucide-react';

export default function VerifySimulationPage() {
  const [simulationData, setSimulationData] = useState<any>(null);
  const [sessionData, setSessionData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const targetSimulationId = 'ed7f0192';
  const targetSessionId = 'local_1753381099605_p87dvy82b';

  const loadData = () => {
    try {
      setLoading(true);
      setError(null);

      // Load simulation results
      const simulationResults = JSON.parse(localStorage.getItem('simulation_results') || '[]');
      const targetSimulation = simulationResults.find((sim: any) => 
        sim.simulation_id === targetSimulationId || 
        sim.results?.simulation_id === targetSimulationId
      );

      // Load session data
      const sessions = JSON.parse(localStorage.getItem('axwise_research_sessions') || '{}');
      const relatedSession = Object.values(sessions).find((s: any) => s.session_id === targetSessionId);

      setSimulationData(targetSimulation);
      setSessionData(relatedSession);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const downloadInterviews = () => {
    if (!simulationData) return;

    const interviews = simulationData.results?.interviews || 
                     simulationData.results?.data?.interviews || 
                     [];
    const businessIdea = simulationData.results?.business_context?.business_idea || 'Unknown Business';
    
    let content = `SIMULATION INTERVIEWS - ${targetSimulationId}\n`;
    content += `=====================================\n\n`;
    content += `Business Idea: ${businessIdea}\n`;
    content += `Total Interviews: ${interviews.length}\n`;
    content += `Generated: ${simulationData.timestamp ? new Date(simulationData.timestamp).toLocaleString() : 'Unknown'}\n\n`;
    
    interviews.forEach((interview: any, i: number) => {
      content += `INTERVIEW ${i + 1}\n`;
      content += `================\n`;
      content += `Stakeholder: ${interview.stakeholder_type || 'Unknown'}\n`;
      content += `Person ID: ${interview.person_id || interview.persona_id || 'Unknown'}\n\n`;
      content += `Responses:\n`;
      content += JSON.stringify(interview.responses || interview.content || interview, null, 2);
      content += `\n\n`;
    });
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `simulation-${targetSimulationId}-interviews.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const showInterviews = () => {
    if (!simulationData) return;

    const interviews = simulationData.results?.interviews || 
                     simulationData.results?.data?.interviews || 
                     [];
    
    const popup = window.open('', '_blank', 'width=1200,height=800');
    if (popup) {
      popup.document.write(`
        <html>
          <head><title>Interviews: ${targetSimulationId}</title></head>
          <body>
            <h1>Interviews for Simulation ${targetSimulationId}</h1>
            <p><strong>Total Interviews:</strong> ${interviews.length}</p>
            <hr>
            ${interviews.map((interview: any, i: number) => `
              <div style="border: 1px solid #ddd; margin: 20px 0; padding: 15px;">
                <h3>Interview ${i + 1}</h3>
                <p><strong>Stakeholder:</strong> ${interview.stakeholder_type || 'Unknown'}</p>
                <p><strong>Person ID:</strong> ${interview.person_id || interview.persona_id || 'Unknown'}</p>
                <h4>Responses:</h4>
                <pre style="white-space: pre-wrap; background: #f5f5f5; padding: 10px; max-height: 400px; overflow-y: auto;">${JSON.stringify(interview.responses || interview.content || interview, null, 2)}</pre>
              </div>
            `).join('')}
          </body>
        </html>
      `);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Loading verification data...
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
        <div className="max-w-4xl mx-auto">
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

  const businessIdea = simulationData?.results?.business_context?.business_idea || 
                      simulationData?.results?.data?.business_context?.business_idea || 
                      'Unknown';
  const targetCustomer = simulationData?.results?.business_context?.target_customer || 
                        simulationData?.results?.data?.business_context?.target_customer || 
                        'Unknown';
  const problem = simulationData?.results?.business_context?.problem || 
                 simulationData?.results?.data?.business_context?.problem || 
                 'Unknown';
  const interviews = simulationData?.results?.interviews || 
                    simulationData?.results?.data?.interviews || 
                    [];

  const isApiService = businessIdea.toLowerCase().includes('api') || 
                      businessIdea.toLowerCase().includes('legacy') ||
                      businessIdea.toLowerCase().includes('sales order');

  // Calculate stakeholder breakdown
  const stakeholderCounts: Record<string, number> = {};
  interviews.forEach((interview: any) => {
    const stakeholder = interview.stakeholder_type || 'Unknown';
    stakeholderCounts[stakeholder] = (stakeholderCounts[stakeholder] || 0) + 1;
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl">🔍 Simulation Verification</CardTitle>
            <div className="text-sm text-muted-foreground">
              <p><strong>Target Simulation ID:</strong> {targetSimulationId}</p>
              <p><strong>Related Session ID:</strong> {targetSessionId}</p>
            </div>
          </CardHeader>
        </Card>

        {/* Simulation Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {simulationData ? '✅' : '❌'} Simulation Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            {simulationData ? (
              <div className={`p-4 rounded-lg ${isApiService ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'}`}>
                <div className="space-y-2">
                  <p><strong>Business Idea:</strong> {businessIdea}</p>
                  <p><strong>Target Customer:</strong> {targetCustomer}</p>
                  <p><strong>Problem:</strong> {problem}</p>
                  <p><strong>Interviews:</strong> {interviews.length}</p>
                  <p><strong>Created:</strong> {simulationData.timestamp ? new Date(simulationData.timestamp).toLocaleString() : 'Unknown'}</p>
                  <p><strong>Source:</strong> {simulationData.source || 'Unknown'}</p>
                </div>
                
                <div className={`mt-4 p-3 rounded font-semibold ${isApiService ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                  {isApiService ? 
                    '🎯 This IS the API service simulation!' : 
                    '⚠️ This is NOT the API service simulation.'
                  }
                </div>

                {interviews.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-semibold mb-2">📋 Interview Summary</h4>
                    <p className="mb-2"><strong>Total Interviews:</strong> {interviews.length}</p>
                    
                    <div className="mb-4">
                      <h5 className="font-medium mb-1">Stakeholder Breakdown:</h5>
                      <ul className="list-disc list-inside space-y-1">
                        {Object.entries(stakeholderCounts).map(([stakeholder, count]) => (
                          <li key={stakeholder}>
                            <strong>{stakeholder}:</strong> {count} interviews
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="flex gap-2">
                      <Button onClick={showInterviews} variant="outline">
                        <Eye className="h-4 w-4 mr-2" />
                        Show All Interviews
                      </Button>
                      <Button onClick={downloadInterviews} variant="default">
                        <Download className="h-4 w-4 mr-2" />
                        Download Interviews
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-semibold text-red-800 mb-2">❌ Simulation Not Found</h4>
                <p className="text-red-700">Simulation {targetSimulationId} was not found in localStorage.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Session Analysis */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {sessionData ? '✅' : '❌'} Related Session Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            {sessionData ? (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="space-y-2">
                  <p><strong>Session ID:</strong> {sessionData.session_id}</p>
                  <p><strong>Business Idea:</strong> {sessionData.business_idea || 'None'}</p>
                  <p><strong>Target Customer:</strong> {sessionData.target_customer || 'None'}</p>
                  <p><strong>Problem:</strong> {sessionData.problem || 'None'}</p>
                  <p><strong>Questions Generated:</strong> {sessionData.questions_generated ? 'Yes' : 'No'}</p>
                </div>
              </div>
            ) : (
              <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-semibold text-red-800 mb-2">❌ Related Session Not Found</h4>
                <p className="text-red-700">Session {targetSessionId} was not found in localStorage.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle>🔧 Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2 flex-wrap">
              <Button onClick={() => window.open('/unified-dashboard/simulation-history', '_blank')} variant="outline">
                Open Simulation History
              </Button>
              <Button onClick={() => window.open('/unified-dashboard/research', '_blank')} variant="outline">
                Open Research Page
              </Button>
              <Button onClick={loadData} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Check
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
