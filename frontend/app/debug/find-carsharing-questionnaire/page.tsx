'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { RefreshCw, Eye, ExternalLink } from 'lucide-react';

export default function FindCarsharingQuestionnairePage() {
  const [carsharingSessions, setCarsharingSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const findCarsharingSessions = () => {
    try {
      setLoading(true);

      // Load all sessions
      const sessionsData = JSON.parse(localStorage.getItem('axwise_research_sessions') || '{}');
      const sessionsList = Object.values(sessionsData);

      // Find carsharing sessions
      const carsharingSessionsList = sessionsList.filter((session: any) => {
        const businessIdea = session.business_idea || '';
        return businessIdea.toLowerCase().includes('carsharing') ||
               businessIdea.toLowerCase().includes('car sharing') ||
               businessIdea.toLowerCase().includes('peer-to-peer') ||
               businessIdea.toLowerCase().includes('marketplace');
      });

      // Analyze each carsharing session
      const analyzedSessions = carsharingSessionsList.map((session: any) => {
        const questionnaireMessage = session.messages?.find((msg: any) =>
          msg.metadata?.comprehensiveQuestions
        );

        let questionnaireAnalysis = null;
        if (questionnaireMessage) {
          const questionnaire = questionnaireMessage.metadata.comprehensiveQuestions;
          const primaryStakeholders = questionnaire.primaryStakeholders || [];
          const secondaryStakeholders = questionnaire.secondaryStakeholders || [];
          const allStakeholders = [...primaryStakeholders, ...secondaryStakeholders];

          // Count total questions
          const totalQuestions = allStakeholders.reduce((total: number, stakeholder: any) => {
            const questions = stakeholder.questions || {};
            return total +
              (questions.problemDiscovery?.length || 0) +
              (questions.solutionValidation?.length || 0) +
              (questions.followUp?.length || 0);
          }, 0);

          questionnaireAnalysis = {
            totalStakeholders: allStakeholders.length,
            primaryCount: primaryStakeholders.length,
            secondaryCount: secondaryStakeholders.length,
            totalQuestions: totalQuestions,
            timeEstimate: questionnaire.timeEstimate,
            stakeholderNames: allStakeholders.map((s: any) => s.name || s.title || 'Unknown'),
            questionnaire: questionnaire
          };
        }

        return {
          ...session,
          hasQuestionnaire: !!questionnaireMessage,
          questionnaireAnalysis
        };
      });

      setCarsharingSessions(analyzedSessions);

      console.log('🚗 Carsharing sessions found:', analyzedSessions.length);
      console.log('📋 Sessions details:', analyzedSessions);

    } catch (error) {
      console.error('Error finding carsharing sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewQuestionnaire = (sessionId: string) => {
    // Open the questionnaire page
    window.open(`/unified-dashboard/questionnaire/${sessionId}`, '_blank');
  };

  const showQuestionnaireDetails = (session: any) => {
    if (!session.questionnaireAnalysis) {
      alert('No questionnaire data found');
      return;
    }

    const analysis = session.questionnaireAnalysis;
    const questionnaire = analysis.questionnaire;

    const popup = window.open('', '_blank', 'width=1200,height=800');
    if (popup) {
      popup.document.write(`
        <html>
          <head><title>Carsharing Questionnaire: ${session.session_id}</title></head>
          <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h1>🚗 Carsharing Questionnaire</h1>
            <div style="background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <h3>Business Context</h3>
              <p><strong>Business Idea:</strong> ${session.business_idea}</p>
              <p><strong>Target Customer:</strong> ${session.target_customer || 'None'}</p>
              <p><strong>Problem:</strong> ${session.problem || 'None'}</p>
            </div>

            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
              <h3>Questionnaire Summary</h3>
              <p><strong>Total Stakeholders:</strong> ${analysis.totalStakeholders}</p>
              <p><strong>Primary Stakeholders:</strong> ${analysis.primaryCount}</p>
              <p><strong>Secondary Stakeholders:</strong> ${analysis.secondaryCount}</p>
              <p><strong>Total Questions:</strong> ${analysis.totalQuestions}</p>
              <p><strong>Time Estimate:</strong> ${
                analysis.timeEstimate
                  ? (typeof analysis.timeEstimate === 'object'
                      ? `${analysis.timeEstimate.estimatedMinutes || analysis.timeEstimate.totalQuestions || 'Unknown'} minutes`
                      : analysis.timeEstimate)
                  : 'Unknown'
              }</p>
            </div>

            <h3>📋 Stakeholders</h3>
            ${questionnaire.primaryStakeholders ? `
              <h4>Primary Stakeholders:</h4>
              ${questionnaire.primaryStakeholders.map((stakeholder: any, index: number) => `
                <div style="border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px;">
                  <h5>${stakeholder.name || stakeholder.title || `Primary Stakeholder ${index + 1}`}</h5>
                  <p><strong>Description:</strong> ${stakeholder.description || stakeholder.role || 'No description'}</p>
                  <p><strong>Questions:</strong></p>
                  <ul>
                    ${(stakeholder.questions?.problemDiscovery || []).map((q: string) => `<li><strong>Problem Discovery:</strong> ${q}</li>`).join('')}
                    ${(stakeholder.questions?.solutionValidation || []).map((q: string) => `<li><strong>Solution Validation:</strong> ${q}</li>`).join('')}
                    ${(stakeholder.questions?.followUp || []).map((q: string) => `<li><strong>Follow-up:</strong> ${q}</li>`).join('')}
                  </ul>
                </div>
              `).join('')}
            ` : ''}

            ${questionnaire.secondaryStakeholders ? `
              <h4>Secondary Stakeholders:</h4>
              ${questionnaire.secondaryStakeholders.map((stakeholder: any, index: number) => `
                <div style="border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px;">
                  <h5>${stakeholder.name || stakeholder.title || `Secondary Stakeholder ${index + 1}`}</h5>
                  <p><strong>Description:</strong> ${stakeholder.description || stakeholder.role || 'No description'}</p>
                  <p><strong>Questions:</strong></p>
                  <ul>
                    ${(stakeholder.questions?.problemDiscovery || []).map((q: string) => `<li><strong>Problem Discovery:</strong> ${q}</li>`).join('')}
                    ${(stakeholder.questions?.solutionValidation || []).map((q: string) => `<li><strong>Solution Validation:</strong> ${q}</li>`).join('')}
                    ${(stakeholder.questions?.followUp || []).map((q: string) => `<li><strong>Follow-up:</strong> ${q}</li>`).join('')}
                  </ul>
                </div>
              `).join('')}
            ` : ''}
          </body>
        </html>
      `);
    }
  };

  useEffect(() => {
    findCarsharingSessions();
  }, []);

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-center">
                <RefreshCw className="h-6 w-6 animate-spin mr-2" />
                Finding carsharing questionnaires...
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
              🚗 Find Carsharing Questionnaire
            </CardTitle>
            <div className="text-sm text-muted-foreground">
              <p>Locating peer-to-peer carsharing questionnaires in your sessions</p>
            </div>
          </CardHeader>
        </Card>

        {/* Carsharing Sessions */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              📋 Carsharing Sessions Found ({carsharingSessions.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {carsharingSessions.length > 0 ? (
              <div className="space-y-4">
                {carsharingSessions.map((session: any, index: number) => (
                  <div key={session.session_id} className="p-4 border rounded-lg bg-blue-50 border-blue-200">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <h4 className="font-semibold text-blue-800 mb-2">
                          🚗 Carsharing Session {index + 1}
                        </h4>

                        <div className="space-y-1 text-sm">
                          <p><strong>Session ID:</strong> {session.session_id}</p>
                          <p><strong>Business Idea:</strong> {session.business_idea}</p>
                          <p><strong>Target Customer:</strong> {session.target_customer || 'None'}</p>
                          <p><strong>Problem:</strong> {session.problem || 'None'}</p>
                          <p><strong>Has Questionnaire:</strong> {session.hasQuestionnaire ? '✅ Yes' : '❌ No'}</p>
                          <p><strong>Created:</strong> {session.created_at ? new Date(session.created_at).toLocaleString() : 'Unknown'}</p>

                          {session.questionnaireAnalysis && (
                            <div className="mt-2 p-2 bg-white rounded border">
                              <p><strong>Questionnaire Summary:</strong></p>
                              <ul className="list-disc list-inside text-xs ml-2">
                                <li>{session.questionnaireAnalysis.totalStakeholders} stakeholders ({session.questionnaireAnalysis.primaryCount} primary, {session.questionnaireAnalysis.secondaryCount} secondary)</li>
                                <li>{session.questionnaireAnalysis.totalQuestions} total questions</li>
                                <li>Time estimate: {
                                  session.questionnaireAnalysis.timeEstimate
                                    ? (typeof session.questionnaireAnalysis.timeEstimate === 'object'
                                        ? `${session.questionnaireAnalysis.timeEstimate.estimatedMinutes || session.questionnaireAnalysis.timeEstimate.totalQuestions || 'Unknown'} minutes`
                                        : session.questionnaireAnalysis.timeEstimate)
                                    : 'Unknown'
                                }</li>
                              </ul>
                              <p className="text-xs mt-1"><strong>Stakeholders:</strong> {session.questionnaireAnalysis.stakeholderNames.join(', ')}</p>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex gap-2 ml-4">
                        {session.hasQuestionnaire && (
                          <>
                            <Button
                              onClick={() => showQuestionnaireDetails(session)}
                              variant="outline"
                              size="sm"
                            >
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </Button>
                            <Button
                              onClick={() => viewQuestionnaire(session.session_id)}
                              variant="default"
                              size="sm"
                            >
                              <ExternalLink className="h-4 w-4 mr-2" />
                              Open Questionnaire
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-4 bg-yellow-50 border border-yellow-200 rounded">
                <h4 className="font-semibold text-yellow-800 mb-2">⚠️ No Carsharing Sessions Found</h4>
                <p className="text-yellow-700">No sessions found with carsharing, peer-to-peer, or marketplace keywords.</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Quick Links */}
        <Card>
          <CardHeader>
            <CardTitle>🔗 Quick Links</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground mb-3">Based on our earlier investigation:</p>
              <div className="flex gap-2 flex-wrap">
                <Button
                  onClick={() => window.open('/unified-dashboard/questionnaire/local_1753381099605_p87dvy82b', '_blank')}
                  variant="outline"
                >
                  <ExternalLink className="h-4 w-4 mr-2" />
                  Open Known Carsharing Session
                </Button>
                <Button
                  onClick={() => window.open('/unified-dashboard/research', '_blank')}
                  variant="outline"
                >
                  View Research Page
                </Button>
                <Button
                  onClick={findCarsharingSessions}
                  variant="outline"
                >
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh Search
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
