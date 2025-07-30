'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, AlertTriangle } from 'lucide-react';

export default function CheckDataMixingPage() {
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const analyzeDataMixing = () => {
    try {
      setLoading(true);
      setError(null);

      // Load all sessions
      const sessions = JSON.parse(localStorage.getItem('axwise_research_sessions') || '{}');
      const sessionsList = Object.values(sessions);

      // Load simulation ed7f0192
      const simulations = JSON.parse(localStorage.getItem('simulation_results') || '[]');
      const targetSimulation = simulations.find((sim: any) => 
        sim.simulation_id === 'ed7f0192' || 
        sim.results?.simulation_id === 'ed7f0192'
      );

      if (!targetSimulation) {
        setError('Simulation ed7f0192 not found in localStorage');
        return;
      }

      // Extract simulation data
      const simBusinessIdea = targetSimulation.results?.business_context?.business_idea || 
                             targetSimulation.results?.data?.business_context?.business_idea || '';
      const simInterviews = targetSimulation.results?.interviews || 
                           targetSimulation.results?.data?.interviews || [];

      // Get unique stakeholder types from simulation
      const simStakeholderTypes = [...new Set(simInterviews.map((interview: any) => 
        interview.stakeholder_type || 'Unknown'
      ))];

      console.log('🔍 Simulation business idea:', simBusinessIdea);
      console.log('🔍 Simulation stakeholder types:', simStakeholderTypes);

      // Find sessions that match the business idea
      const matchingBusinessSessions = sessionsList.filter((session: any) => 
        session.business_idea && session.business_idea.toLowerCase().includes('carsharing')
      );

      // Find sessions that have matching stakeholder types
      const matchingStakeholderSessions = sessionsList.filter((session: any) => {
        const questionnaireMessage = session.messages?.find((msg: any) =>
          msg.metadata?.comprehensiveQuestions
        );

        if (!questionnaireMessage) return false;

        const questionnaire = questionnaireMessage.metadata.comprehensiveQuestions;
        const allStakeholders = [
          ...(questionnaire.primaryStakeholders || []),
          ...(questionnaire.secondaryStakeholders || [])
        ];

        const sessionStakeholderTypes = allStakeholders.map((s: any) => s.name || s.title || 'Unknown');
        
        // Check if any simulation stakeholder types match this session
        return simStakeholderTypes.some(simType => 
          sessionStakeholderTypes.some(sessionType => 
            sessionType.toLowerCase().includes(simType.toLowerCase()) ||
            simType.toLowerCase().includes(sessionType.toLowerCase())
          )
        );
      });

      // Find laundromat sessions specifically
      const laundrySessionsWithStakeholders = sessionsList.filter((session: any) => {
        if (!session.business_idea || !session.business_idea.toLowerCase().includes('laundromat')) {
          return false;
        }

        const questionnaireMessage = session.messages?.find((msg: any) =>
          msg.metadata?.comprehensiveQuestions
        );

        if (!questionnaireMessage) return false;

        const questionnaire = questionnaireMessage.metadata.comprehensiveQuestions;
        const allStakeholders = [
          ...(questionnaire.primaryStakeholders || []),
          ...(questionnaire.secondaryStakeholders || [])
        ];

        const sessionStakeholderTypes = allStakeholders.map((s: any) => s.name || s.title || 'Unknown');
        
        // Check if this laundromat session has "Adult Child/Caregiver" stakeholders
        return sessionStakeholderTypes.some(type => 
          type.toLowerCase().includes('adult child') || 
          type.toLowerCase().includes('caregiver') ||
          type.toLowerCase().includes('senior')
        );
      });

      setAnalysis({
        simulation: {
          id: 'ed7f0192',
          businessIdea: simBusinessIdea,
          stakeholderTypes: simStakeholderTypes,
          interviewCount: simInterviews.length,
          timestamp: targetSimulation.timestamp
        },
        sessions: {
          total: sessionsList.length,
          matchingBusiness: matchingBusinessSessions.length,
          matchingStakeholders: matchingStakeholderSessions.length,
          laundryWithCaregivers: laundrySessionsWithStakeholders.length
        },
        matchingBusinessSessions: matchingBusinessSessions.map((s: any) => ({
          id: s.session_id,
          businessIdea: s.business_idea,
          hasQuestionnaire: !!s.messages?.find((msg: any) => msg.metadata?.comprehensiveQuestions)
        })),
        matchingStakeholderSessions: matchingStakeholderSessions.map((s: any) => {
          const questionnaireMessage = s.messages?.find((msg: any) =>
            msg.metadata?.comprehensiveQuestions
          );
          const questionnaire = questionnaireMessage?.metadata?.comprehensiveQuestions;
          const allStakeholders = [
            ...(questionnaire?.primaryStakeholders || []),
            ...(questionnaire?.secondaryStakeholders || [])
          ];
          const stakeholderTypes = allStakeholders.map((st: any) => st.name || st.title || 'Unknown');

          return {
            id: s.session_id,
            businessIdea: s.business_idea,
            stakeholderTypes: stakeholderTypes
          };
        }),
        laundrySessionsWithCaregivers: laundrySessionsWithStakeholders.map((s: any) => {
          const questionnaireMessage = s.messages?.find((msg: any) =>
            msg.metadata?.comprehensiveQuestions
          );
          const questionnaire = questionnaireMessage?.metadata?.comprehensiveQuestions;
          const allStakeholders = [
            ...(questionnaire?.primaryStakeholders || []),
            ...(questionnaire?.secondaryStakeholders || [])
          ];
          const stakeholderTypes = allStakeholders.map((st: any) => st.name || st.title || 'Unknown');

          return {
            id: s.session_id,
            businessIdea: s.business_idea,
            stakeholderTypes: stakeholderTypes
          };
        })
      });

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    analyzeDataMixing();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Analyzing data mixing issue...
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
                <h3 className="font-semibold mb-2">Error</h3>
                <p>{error}</p>
                <Button onClick={analyzeDataMixing} className="mt-4">
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

  const isDataMixed = analysis.simulation.businessIdea.toLowerCase().includes('carsharing') &&
                     analysis.simulation.stakeholderTypes.some((type: string) => 
                       type.toLowerCase().includes('caregiver') || 
                       type.toLowerCase().includes('adult child')
                     );

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto space-y-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl flex items-center gap-2">
              <AlertTriangle className="h-6 w-6" />
              Data Mixing Analysis - Simulation ed7f0192
            </CardTitle>
            <div className="text-sm text-muted-foreground">
              <p>Investigating why carsharing business context has laundromat stakeholders</p>
            </div>
          </CardHeader>
        </Card>

        {/* Data Mixing Detection */}
        <Card>
          <CardHeader>
            <CardTitle className={`flex items-center gap-2 ${isDataMixed ? 'text-red-600' : 'text-green-600'}`}>
              {isDataMixed ? '❌' : '✅'} Data Mixing Detection
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`p-4 rounded-lg ${isDataMixed ? 'bg-red-50 border border-red-200' : 'bg-green-50 border border-green-200'}`}>
              <h4 className="font-semibold mb-2">
                {isDataMixed ? '🚨 Data Mixing Detected!' : '✅ No Data Mixing Detected'}
              </h4>
              <div className="space-y-2 text-sm">
                <p><strong>Business Idea:</strong> {analysis.simulation.businessIdea}</p>
                <p><strong>Stakeholder Types:</strong> {analysis.simulation.stakeholderTypes.join(', ')}</p>
                <p><strong>Interview Count:</strong> {analysis.simulation.interviewCount}</p>
                <p><strong>Created:</strong> {analysis.simulation.timestamp ? new Date(analysis.simulation.timestamp).toLocaleString() : 'Unknown'}</p>
              </div>
              
              {isDataMixed && (
                <div className="mt-4 p-3 bg-red-100 rounded text-red-800">
                  <strong>Issue:</strong> This simulation has carsharing business context but laundromat/caregiver stakeholders. 
                  This indicates questionnaire data was mixed between sessions.
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Business Context Matches */}
        <Card>
          <CardHeader>
            <CardTitle>🎯 Sessions Matching Business Context</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4"><strong>Found {analysis.sessions.matchingBusiness} carsharing sessions:</strong></p>
            {analysis.matchingBusinessSessions.length > 0 ? (
              <div className="space-y-2">
                {analysis.matchingBusinessSessions.map((session: any) => (
                  <div key={session.id} className="p-3 border rounded bg-blue-50">
                    <p><strong>Session:</strong> {session.id}</p>
                    <p><strong>Business Idea:</strong> {session.businessIdea}</p>
                    <p><strong>Has Questionnaire:</strong> {session.hasQuestionnaire ? '✅ Yes' : '❌ No'}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No carsharing sessions found</p>
            )}
          </CardContent>
        </Card>

        {/* Stakeholder Matches */}
        <Card>
          <CardHeader>
            <CardTitle>👥 Sessions Matching Stakeholder Types</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4"><strong>Found {analysis.sessions.matchingStakeholders} sessions with matching stakeholders:</strong></p>
            {analysis.matchingStakeholderSessions.length > 0 ? (
              <div className="space-y-2">
                {analysis.matchingStakeholderSessions.map((session: any) => (
                  <div key={session.id} className="p-3 border rounded bg-yellow-50">
                    <p><strong>Session:</strong> {session.id}</p>
                    <p><strong>Business Idea:</strong> {session.businessIdea}</p>
                    <p><strong>Stakeholders:</strong> {session.stakeholderTypes.join(', ')}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No sessions with matching stakeholders found</p>
            )}
          </CardContent>
        </Card>

        {/* Laundromat Sessions with Caregivers */}
        <Card>
          <CardHeader>
            <CardTitle>🧺 Laundromat Sessions with Caregiver Stakeholders</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="mb-4"><strong>Found {analysis.sessions.laundryWithCaregivers} laundromat sessions with caregiver stakeholders:</strong></p>
            {analysis.laundrySessionsWithCaregivers.length > 0 ? (
              <div className="space-y-2">
                {analysis.laundrySessionsWithCaregivers.map((session: any) => (
                  <div key={session.id} className="p-3 border rounded bg-orange-50">
                    <p><strong>Session:</strong> {session.id}</p>
                    <p><strong>Business Idea:</strong> {session.businessIdea}</p>
                    <p><strong>Stakeholders:</strong> {session.stakeholderTypes.join(', ')}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-muted-foreground">No laundromat sessions with caregiver stakeholders found</p>
            )}
          </CardContent>
        </Card>

        {/* Summary */}
        <Card>
          <CardHeader>
            <CardTitle>📊 Analysis Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p><strong>Total Sessions:</strong> {analysis.sessions.total}</p>
              <p><strong>Carsharing Sessions:</strong> {analysis.sessions.matchingBusiness}</p>
              <p><strong>Sessions with Caregiver Stakeholders:</strong> {analysis.sessions.matchingStakeholders}</p>
              <p><strong>Laundromat + Caregiver Sessions:</strong> {analysis.sessions.laundryWithCaregivers}</p>
            </div>

            {isDataMixed && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
                <h4 className="font-semibold text-yellow-800 mb-2">🔧 Recommended Fix</h4>
                <p className="text-yellow-700">
                  The simulation mixed questionnaire data from different sessions. To get the correct API service simulation:
                </p>
                <ol className="list-decimal list-inside mt-2 text-yellow-700">
                  <li>Find the actual API service session</li>
                  <li>Run simulation directly on that session</li>
                  <li>Investigate the session selection logic in the research page</li>
                </ol>
              </div>
            )}

            <div className="flex gap-2 mt-4">
              <Button onClick={analyzeDataMixing} variant="outline">
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh Analysis
              </Button>
              <Button onClick={() => window.open('/debug/find-api-session', '_blank')} variant="outline">
                Find API Service Session
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
