'use client';

import { useState, useEffect } from 'react';
import { useSearchParams } from 'next/navigation';
import { ChatInterface } from '@/components/research/ChatInterface';
import { SessionManager } from '@/components/research/SessionManager';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { MessageSquare, FileText, Users, Target, ArrowRight } from 'lucide-react';

export default function CustomerResearchPage() {
  const [showChat, setShowChat] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);
  const searchParams = useSearchParams();

  // Check for session parameter in URL on mount
  useEffect(() => {
    const sessionParam = searchParams.get('session');
    if (sessionParam) {
      console.log('Loading session from URL:', sessionParam);
      handleLoadSession(sessionParam);
    }
  }, [searchParams]);

  const handleQuestionsGenerated = (_questions: any) => {
    // Questions are handled within the ChatInterface component
  };

  const handleLoadSession = (sessionId: string) => {
    console.log('Page: Loading session', sessionId);
    setCurrentSessionId(sessionId);
    // Ensure we're in chat mode when loading a session
    if (!showChat) {
      setShowChat(true);
    }
  };

  if (showChat) {
    return (
      <div className="min-h-screen bg-background">
        <ChatInterface
          onComplete={handleQuestionsGenerated}
          onBack={() => setShowChat(false)}
          loadSessionId={currentSessionId || undefined}
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold tracking-tight">Customer Research</h1>
        <p className="text-muted-foreground">
          Develop your business idea and generate targeted questionnaires
        </p>
      </div>

      {/* Quick Start Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3 mb-8">
        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setShowChat(true)}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="h-5 w-5" />
              Start New Research
            </CardTitle>
            <CardDescription>
              Begin a guided conversation to develop your business idea
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <Badge variant="secondary">Interactive</Badge>
              <ArrowRight className="h-4 w-4" />
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => window.location.href = '/unified-dashboard/research'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5" />
              Interview Simulation
            </CardTitle>
            <CardDescription>
              Generate AI persona interviews from your questionnaires
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <Badge variant="secondary">AI Powered</Badge>
              <ArrowRight className="h-4 w-4" />
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => window.location.href = '/unified-dashboard/upload'}>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="h-5 w-5" />
              Analyze Interviews
            </CardTitle>
            <CardDescription>
              Upload and analyze existing interview data
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between">
              <Badge variant="secondary">Analysis</Badge>
              <ArrowRight className="h-4 w-4" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Session Manager */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Recent Sessions
          </CardTitle>
          <CardDescription>
            Continue your previous research conversations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <SessionManager onLoadSession={handleLoadSession} />
        </CardContent>
      </Card>
    </div>
  );
}
