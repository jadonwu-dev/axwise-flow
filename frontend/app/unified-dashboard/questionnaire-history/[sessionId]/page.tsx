'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, Play, Loader2 } from 'lucide-react';
import { ComprehensiveQuestionsComponent } from '@/components/research/ComprehensiveQuestionsComponent';
import { useToast } from '@/components/providers/toast-provider';
import { generateComprehensiveQuestionnaireText } from '@/lib/questionnaire-export';

export default function QuestionnaireViewPage() {
  const params = useParams();
  const router = useRouter();
  const { showToast } = useToast();
  const sessionId = params.sessionId as string;

  const [questionnaire, setQuestionnaire] = useState<any>(null);
  const [sessionInfo, setSessionInfo] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadQuestionnaire = async () => {
      if (!sessionId) return;

      setIsLoading(true);
      setError(null);

      try {
        let questionnaireData = null;
        let sessionData = null;

        if (sessionId.startsWith('local_')) {
          // Handle local session
          if (typeof window !== 'undefined') {
            const { LocalResearchStorage } = await import('@/lib/api/research');
            const session = LocalResearchStorage.getSession(sessionId);

            if (session?.messages) {
              const questionnaireMessage = session.messages.find((msg: any) =>
                msg.metadata?.comprehensiveQuestions
              );

              if (questionnaireMessage?.metadata?.comprehensiveQuestions) {
                questionnaireData = questionnaireMessage.metadata.comprehensiveQuestions;
                sessionData = {
                  title: session.business_idea || `Session ${sessionId.slice(-8)}`,
                  business_idea: session.business_idea,
                  target_customer: session.target_customer,
                  problem: session.problem,
                  created_at: session.created_at,
                  questionnaire_generated_at: questionnaireMessage.timestamp || session.updated_at
                };
              }
            }
          }
        } else {
          // Handle backend session
          const response = await fetch(`/api/research/sessions/${sessionId}/questionnaire`);

          if (response.ok) {
            const data = await response.json();
            questionnaireData = data.questionnaire;

            // Also fetch session info
            const sessionResponse = await fetch(`/api/research/sessions/${sessionId}`);
            if (sessionResponse.ok) {
              const sessionData = await sessionResponse.json();
              setSessionInfo({
                title: sessionData.business_idea || `Session ${sessionId.slice(-8)}`,
                business_idea: sessionData.business_idea,
                target_customer: sessionData.target_customer,
                problem: sessionData.problem,
                created_at: sessionData.created_at,
                questionnaire_generated_at: data.generated_at || sessionData.completed_at
              });
            }
          } else {
            throw new Error(`Failed to load questionnaire: ${response.status}`);
          }
        }

        if (questionnaireData) {
          setQuestionnaire(questionnaireData);
          if (sessionData) {
            setSessionInfo(sessionData);
          }
        } else {
          setError('No questionnaire data found for this session');
        }
      } catch (err) {
        console.error('Error loading questionnaire:', err);
        setError(err instanceof Error ? err.message : 'Failed to load questionnaire');
      } finally {
        setIsLoading(false);
      }
    };

    loadQuestionnaire();
  }, [sessionId]);

  const handleDownload = async () => {
    if (!questionnaire || !sessionInfo) return;

    try {
      const textContent = generateComprehensiveQuestionnaireText(questionnaire, sessionInfo.title);
      const blob = new Blob([textContent], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `questionnaire-${sessionInfo.title.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showToast('Questionnaire downloaded successfully', { variant: 'success' });
    } catch (error) {
      console.error('Download failed:', error);
      showToast('Failed to download questionnaire', { variant: 'error' });
    }
  };

  const handleUseForSimulation = () => {
    router.push(`/unified-dashboard/research?session=${sessionId}`);
  };

  const handleGoToDashboard = () => {
    router.push('/unified-dashboard');
  };

  if (isLoading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="flex items-center gap-2">
            <Loader2 className="h-6 w-6 animate-spin" />
            <span>Loading questionnaire...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-6">
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Button variant="ghost" size="sm" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4" />
                Back
              </Button>
              <CardTitle>Error Loading Questionnaire</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">{error}</p>
            <Button className="mt-4" onClick={() => router.push('/unified-dashboard/questionnaire-history')}>
              Return to Questionnaire History
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-6xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={() => router.back()}>
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold">{sessionInfo?.title || 'Questionnaire'}</h1>
            {sessionInfo?.questionnaire_generated_at && (
              <p className="text-sm text-muted-foreground">
                Generated on {new Date(sessionInfo.questionnaire_generated_at).toLocaleDateString('en-GB')} at{' '}
                {new Date(sessionInfo.questionnaire_generated_at).toLocaleTimeString()}
              </p>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleDownload}>
            <Download className="h-4 w-4 mr-2" />
            Download
          </Button>
          <Button onClick={handleUseForSimulation}>
            <Play className="h-4 w-4 mr-2" />
            Use for Simulation
          </Button>
        </div>
      </div>

      {/* Business Context */}
      {sessionInfo && (sessionInfo.business_idea || sessionInfo.target_customer || sessionInfo.problem) && (
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="text-lg">Business Context</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {sessionInfo.business_idea && (
              <div>
                <span className="font-medium text-sm">Business Idea:</span>
                <p className="text-sm text-muted-foreground mt-1">{sessionInfo.business_idea}</p>
              </div>
            )}
            {sessionInfo.target_customer && (
              <div>
                <span className="font-medium text-sm">Target Customer:</span>
                <p className="text-sm text-muted-foreground mt-1">{sessionInfo.target_customer}</p>
              </div>
            )}
            {sessionInfo.problem && (
              <div>
                <span className="font-medium text-sm">Problem:</span>
                <p className="text-sm text-muted-foreground mt-1">{sessionInfo.problem}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Questionnaire Component */}
      {questionnaire && (
        <Card>
          <CardContent className="p-6">
            <ComprehensiveQuestionsComponent
              primaryStakeholders={questionnaire.primaryStakeholders || []}
              secondaryStakeholders={questionnaire.secondaryStakeholders || []}
              timeEstimate={questionnaire.timeEstimate}
              businessContext={sessionInfo?.business_idea}
              onExport={handleDownload}
              onDashboard={handleGoToDashboard}
            />
          </CardContent>
        </Card>
      )}
    </div>
  );
}
