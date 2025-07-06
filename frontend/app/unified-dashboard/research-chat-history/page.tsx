'use client';

import { useState, useEffect } from 'react';

// Client-side timestamp component to avoid hydration errors
function ClientTimestamp({ timestamp, format = 'localeString' }: { timestamp: string; format?: 'localeString' | 'localeTimeString' | 'localeDateString' }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <span>Loading...</span>;
  }

  const date = new Date(timestamp);
  if (format === 'localeTimeString') {
    return <span>{date.toLocaleTimeString()}</span>;
  } else if (format === 'localeDateString') {
    return <span>{date.toLocaleDateString()}</span>;
  } else {
    return <span>{date.toLocaleString()}</span>;
  }
}
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScrollArea } from '@/components/ui/scroll-area';
import {
  Clock,
  Target,
  Users,
  CheckCircle,
  MessageSquare,
  Calendar,
  Trash2,
  Eye,
  ArrowRight,
  Plus
} from 'lucide-react';
import { getResearchSessions, deleteResearchSession, type ResearchSession } from '@/lib/api/research';

export default function ResearchChatHistory() {
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<ResearchSession | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSessions();
  }, []);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await getResearchSessions(50);
      setSessions(data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };

  const viewSession = (sessionId: string) => {
    const session = sessions.find(s => s.session_id === sessionId);
    setSelectedSession(session || null);
  };

  const deleteSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this research chat session?')) {
      return;
    }

    try {
      await deleteResearchSession(sessionId);
      setSessions(sessions.filter(s => s.session_id !== sessionId));

      if (selectedSession && selectedSession.session_id === sessionId) {
        setSelectedSession(null);
      }

      console.log('Session deleted successfully');
    } catch (error) {
      console.error('Error deleting session:', error);
      alert(`Error deleting session: ${error}`);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'active': return 'bg-blue-100 text-blue-800';
      case 'abandoned': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStageIcon = (stage: string) => {
    switch (stage) {
      case 'initial': return <Clock className="h-4 w-4" />;
      case 'business_idea': return <Target className="h-4 w-4" />;
      case 'target_customer': return <Users className="h-4 w-4" />;
      case 'validation': return <CheckCircle className="h-4 w-4" />;
      case 'conversation': return <MessageSquare className="h-4 w-4" />;
      case 'completed': return <CheckCircle className="h-4 w-4" />;
      default: return <Clock className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center h-64">
          <div className="text-lg">Loading research chat history...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 max-w-7xl">
      <div className="mb-6">
        <h1 className="text-2xl lg:text-3xl font-bold text-foreground">Research Chat History</h1>
        <p className="text-muted-foreground mt-2">View and manage your research chat conversations</p>
        <div className="flex gap-3 mt-4">
          <Button
            onClick={() => {
              localStorage.removeItem('current_research_session');
              window.location.href = '/unified-dashboard/research-chat';
            }}
          >
            <Plus className="mr-2 h-4 w-4" />
            Start New Research Chat
          </Button>
          <Button
            variant="outline"
            onClick={() => window.location.href = '/unified-dashboard/research'}
          >
            <ArrowRight className="mr-2 h-4 w-4" />
            Go to Interview Simulation
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 lg:gap-6">
        {/* Sessions List */}
        <div className="xl:col-span-2">
          <Card className="h-fit">
            <CardHeader>
              <CardTitle>Research Chat Sessions</CardTitle>
              <CardDescription>
                {sessions.length} total sessions
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {sessions.map((session) => (
                  <Card
                    key={session.session_id}
                    className="p-3 lg:p-4 hover:bg-muted/50 transition-colors cursor-pointer border-l-4 border-l-primary"
                    onClick={() => viewSession(session.session_id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          {getStageIcon(session.stage)}
                          <h3 className="font-medium truncate">
                            {session.business_idea || 'Untitled Session'}
                          </h3>
                        </div>

                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                          <Badge variant="outline" className="text-xs">
                            {session.industry}
                          </Badge>
                          <Badge className={`text-xs ${getStatusColor(session.status)}`}>
                            {session.status}
                          </Badge>
                          {session.questions_generated && (
                            <Badge variant="outline" className="text-xs bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400">
                              Questions Generated
                            </Badge>
                          )}
                        </div>

                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            <ClientTimestamp timestamp={session.created_at} format="localeDateString" />
                          </span>
                          <span>{session.message_count || session.messages?.length || 0} messages</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            viewSession(session.session_id);
                          }}
                          className="h-8 w-8 p-0"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={(e) => {
                            e.stopPropagation();
                            deleteSession(session.session_id);
                          }}
                          className="h-8 w-8 p-0 text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </Card>
                ))}
                {sessions.length === 0 && (
                  <div className="text-center py-8 text-muted-foreground">
                    <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-lg font-medium">No research chat sessions yet</p>
                    <p className="text-sm">Start a research chat to create your first session</p>
                    <Button
                      className="mt-4"
                      onClick={() => window.location.href = '/unified-dashboard/research-chat'}
                    >
                      Start Research Chat
                    </Button>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Session Details */}
        <div>
          <Card className="sticky top-4">
            <CardHeader>
              <CardTitle>Session Details</CardTitle>
              <CardDescription>
                {selectedSession ? 'Session information' : 'Click a session to view details'}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {selectedSession ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium">Session Info</h4>
                    <Button
                      size="sm"
                      onClick={() => {
                        // Navigate to research chat with session ID as URL parameter
                        window.location.href = `/unified-dashboard/research-chat?session=${selectedSession.session_id}`;
                      }}
                    >
                      Continue Session
                    </Button>
                  </div>

                  <div className="space-y-3 text-sm">
                    <div>
                      <span className="font-medium">Business Idea:</span>
                      <p className="text-muted-foreground mt-1">{selectedSession.business_idea || 'Not specified'}</p>
                    </div>

                    {selectedSession.target_customer && (
                      <div>
                        <span className="font-medium">Target Customer:</span>
                        <p className="text-muted-foreground mt-1">{selectedSession.target_customer}</p>
                      </div>
                    )}

                    {selectedSession.problem && (
                      <div>
                        <span className="font-medium">Problem:</span>
                        <p className="text-muted-foreground mt-1">{selectedSession.problem}</p>
                      </div>
                    )}

                    <div>
                      <span className="font-medium">Status:</span>
                      <Badge className={`ml-2 text-xs ${getStatusColor(selectedSession.status)}`}>
                        {selectedSession.status}
                      </Badge>
                    </div>

                    <div>
                      <span className="font-medium">Created:</span>
                      <p className="text-muted-foreground mt-1">
                        <ClientTimestamp timestamp={selectedSession.created_at} />
                      </p>
                    </div>

                    <div>
                      <span className="font-medium">Messages:</span>
                      <p className="text-muted-foreground mt-1">
                        {selectedSession.message_count || selectedSession.messages?.length || 0} messages
                      </p>
                    </div>
                  </div>

                  {/* Message History */}
                  {selectedSession.messages && selectedSession.messages.length > 0 && (
                    <div className="mt-6">
                      <h5 className="font-medium mb-3">
                        Messages ({selectedSession.messages?.length || 0})
                      </h5>
                      <ScrollArea className="h-40 border rounded p-3 bg-muted">
                        {selectedSession.messages && selectedSession.messages.length > 0 ? (
                          selectedSession.messages.map((msg: any, idx: number) => (
                            <div key={idx} className="mb-3 last:mb-0">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge variant={msg.role === 'user' ? 'default' : 'secondary'} className="text-xs">
                                  {msg.role}
                                </Badge>
                                <span className="text-xs text-muted-foreground">
                                  <ClientTimestamp timestamp={msg.timestamp} format="localeTimeString" />
                                </span>
                              </div>
                              <p className="text-sm text-muted-foreground">
                                {msg.content.length > 100 ? `${msg.content.substring(0, 100)}...` : msg.content}
                              </p>
                            </div>
                          ))
                        ) : (
                          <p className="text-sm text-muted-foreground">No messages available</p>
                        )}
                      </ScrollArea>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Eye className="h-8 w-8 mx-auto mb-3 text-muted-foreground/50" />
                  <p className="text-sm">Click on a session to view details</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
