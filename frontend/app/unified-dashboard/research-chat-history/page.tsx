'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

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

  // Debug: Check for invalid dates only
  const isInvalid = isNaN(date.getTime());

  if (isInvalid) {
    console.warn('Invalid timestamp detected:', timestamp);
    return <span className="text-red-500">Invalid date</span>;
  }

  // Log the actual date for debugging
  console.log('Displaying timestamp:', timestamp, '→', date.toLocaleDateString('en-GB'));

  if (format === 'localeTimeString') {
    return <span>{date.toLocaleTimeString('en-GB')}</span>;
  } else if (format === 'localeDateString') {
    // Use DD/MM/YYYY format as per user preferences
    return <span>{date.toLocaleDateString('en-GB')}</span>;
  } else {
    // Use DD/MM/YYYY format for full datetime
    return <span>{date.toLocaleString('en-GB')}</span>;
  }
}
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';


import {
  Clock,
  MessageSquare,
  Calendar,

  Eye,
  ArrowRight,
  Plus,
  FileText,
  Download,
  Play,
  BarChart
} from 'lucide-react';
import { useToast } from '@/components/providers/toast-provider';
import { getResearchSessions, type ResearchSession } from '@/lib/api/research';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

export default function ResearchChatHistory() {
  const router = useRouter();
  const { showToast } = useToast();
  const [sessions, setSessions] = useState<ResearchSession[]>([]);
  const [allSessions, setAllSessions] = useState<ResearchSession[]>([]);
  const [selectedSession, setSelectedSession] = useState<ResearchSession | null>(null);
  const [loading, setLoading] = useState(true);
  const [showOnlyWithQuestionnaires, setShowOnlyWithQuestionnaires] = useState(true);
  const [stageFilter, setStageFilter] = useState<string>('all');

  // Function to fix only truly corrupted (invalid) timestamps in localStorage
  const fixCorruptedTimestamps = () => {
    try {
      const stored = localStorage.getItem('axwise_research_sessions');
      if (!stored) return;

      const sessions = JSON.parse(stored);
      let hasChanges = false;
      const now = new Date().toISOString();

      const fixedSessions = sessions.map((session: any) => {
        const createdDate = new Date(session.created_at);
        const updatedDate = new Date(session.updated_at);

        // Only fix truly invalid dates (NaN), not past or future dates
        if (isNaN(createdDate.getTime())) {
          console.warn(`Fixing invalid created_at for session ${session.session_id}:`, session.created_at);
          session.created_at = now;
          hasChanges = true;
        }

        if (isNaN(updatedDate.getTime())) {
          console.warn(`Fixing invalid updated_at for session ${session.session_id}:`, session.updated_at);
          session.updated_at = now;
          hasChanges = true;
        }

        return session;
      });

      if (hasChanges) {
        localStorage.setItem('axwise_research_sessions', JSON.stringify(fixedSessions));
        console.log('✅ Fixed corrupted timestamps in localStorage');
        showToast('Fixed corrupted session timestamps', { variant: 'success' });
      } else {
        console.log('ℹ️ No corrupted timestamps found');
      }
    } catch (error) {
      console.error('Error fixing corrupted timestamps:', error);
    }
  };

  // Function to toggle between showing all sessions vs only those with questionnaires
  const toggleSessionFilter = () => {
    const newValue = !showOnlyWithQuestionnaires;
    setShowOnlyWithQuestionnaires(newValue);

    if (newValue) {
      // Show only sessions with questionnaires
      const sessionsWithQuestionnaires = allSessions.filter(session => {
        if (session.questions_generated) return true;

        if (session.messages && session.messages.length > 0) {
          const hasQuestionnaireMessage = session.messages.some(msg =>
            msg.metadata?.comprehensiveQuestions ||
            msg.metadata?.questionnaire ||
            (msg.role === 'assistant' && msg.content && msg.content.includes('questionnaire'))
          );
          if (hasQuestionnaireMessage) return true;
        }

        const hasBusinessIdea = session.business_idea && session.business_idea.trim().length > 0;
        const hasMessages = session.messages && session.messages.length > 1;
        return hasBusinessIdea && hasMessages;
      });
      setSessions(sessionsWithQuestionnaires);
    } else {
      // Show all sessions
      setSessions(allSessions);
    }
  };

  useEffect(() => {
    // Fix any corrupted timestamps before loading sessions
    fixCorruptedTimestamps();
    loadSessions();
  }, []);

  // Calculate questionnaire stats when sessions change
  useEffect(() => {
    const calculateStats = async () => {
      const stats: Record<string, { questions: number; stakeholders: number }> = {};

      for (const session of sessions) {
        if (session.questions_generated) {
          // For local sessions, we need to get the full session data with messages
          if (session.session_id.startsWith('local_')) {
            try {
              // Import LocalResearchStorage dynamically
              const { LocalResearchStorage } = await import('@/lib/api/research');
              const fullSession = LocalResearchStorage.getSession(session.session_id);
              if (fullSession) {
                stats[session.session_id] = calculateQuestionnaireStats(fullSession);
              } else {
                stats[session.session_id] = { questions: 0, stakeholders: 0 };
              }
            } catch (error) {
              console.error(`Error loading local session ${session.session_id}:`, error);
              stats[session.session_id] = { questions: 0, stakeholders: 0 };
            }
          } else {
            // For backend sessions, use the session data we already have
            stats[session.session_id] = calculateQuestionnaireStats(session);
          }
        }
      }

      setQuestionnaireStats(stats);
    };

    if (sessions.length > 0) {
      calculateStats();
    }
  }, [sessions]);

  // Filter sessions based on stage and questionnaire filters
  useEffect(() => {
    let filtered = showOnlyWithQuestionnaires
      ? allSessions.filter(s => s.questions_generated)
      : allSessions;

    if (stageFilter !== 'all') {
      filtered = filtered.filter(session => {
        const stage = getSessionStage(session);
        return stage.id === stageFilter;
      });
    }

    setSessions(filtered);
  }, [allSessions, showOnlyWithQuestionnaires, stageFilter]);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await getResearchSessions(50);

      // Filter sessions to only show those with generated questionnaires
      const sessionsWithQuestionnaires = data.filter(session => {
        // Check if session has questions_generated flag set to true
        if (session.questions_generated) {
          return true;
        }

        // Also check if session has questionnaire messages
        if (session.messages && session.messages.length > 0) {
          const hasQuestionnaireMessage = session.messages.some(msg =>
            msg.metadata?.comprehensiveQuestions ||
            msg.metadata?.questionnaire ||
            (msg.role === 'assistant' && msg.content && msg.content.includes('questionnaire'))
          );
          if (hasQuestionnaireMessage) {
            return true;
          }
        }

        // Exclude empty sessions without business ideas or meaningful content
        const hasBusinessIdea = session.business_idea && session.business_idea.trim().length > 0;
        const hasMessages = session.messages && session.messages.length > 1; // More than just initial message

        return hasBusinessIdea && hasMessages;
      });

      console.log(`📊 Filtered sessions: ${data.length} total → ${sessionsWithQuestionnaires.length} with questionnaires`);

      // Store both filtered and unfiltered data
      setAllSessions(data);
      setSessions(showOnlyWithQuestionnaires ? sessionsWithQuestionnaires : data);
    } catch (error) {
      console.error('Failed to load sessions:', error);
    } finally {
      setLoading(false);
    }
  };



  // Helper function to generate comprehensive questionnaire text
  const generateComprehensiveQuestionnaireText = (questionnaire: any, title: string): string => {
    let content = `# Research Questionnaire: ${title}\n\n`;
    content += `Generated on: ${new Date().toLocaleDateString('en-GB')}\n\n`;

    if (questionnaire.timeEstimate) {
      content += `## Time Estimate\n`;
      content += `Total Questions: ${questionnaire.timeEstimate.totalQuestions || 'N/A'}\n`;
      content += `Estimated Duration: ${questionnaire.timeEstimate.estimatedMinutes || 'N/A'}\n\n`;
    }

    // Primary Stakeholders
    if (questionnaire.primaryStakeholders && questionnaire.primaryStakeholders.length > 0) {
      content += `## Primary Stakeholders\n\n`;
      questionnaire.primaryStakeholders.forEach((stakeholder: any, index: number) => {
        content += `### ${index + 1}. ${stakeholder.name}\n`;
        if (stakeholder.description) {
          content += `**Description:** ${stakeholder.description}\n\n`;
        }

        if (stakeholder.questions) {
          if (stakeholder.questions.problemDiscovery && stakeholder.questions.problemDiscovery.length > 0) {
            content += `**Problem Discovery Questions:**\n`;
            stakeholder.questions.problemDiscovery.forEach((q: string, qIndex: number) => {
              content += `${qIndex + 1}. ${q}\n`;
            });
            content += `\n`;
          }

          if (stakeholder.questions.solutionValidation && stakeholder.questions.solutionValidation.length > 0) {
            content += `**Solution Validation Questions:**\n`;
            stakeholder.questions.solutionValidation.forEach((q: string, qIndex: number) => {
              content += `${qIndex + 1}. ${q}\n`;
            });
            content += `\n`;
          }

          if (stakeholder.questions.followUp && stakeholder.questions.followUp.length > 0) {
            content += `**Follow-up Questions:**\n`;
            stakeholder.questions.followUp.forEach((q: string, qIndex: number) => {
              content += `${qIndex + 1}. ${q}\n`;
            });
            content += `\n`;
          }
        }
        content += `---\n\n`;
      });
    }

    // Secondary Stakeholders
    if (questionnaire.secondaryStakeholders && questionnaire.secondaryStakeholders.length > 0) {
      content += `## Secondary Stakeholders\n\n`;
      questionnaire.secondaryStakeholders.forEach((stakeholder: any, index: number) => {
        content += `### ${index + 1}. ${stakeholder.name}\n`;
        if (stakeholder.description) {
          content += `**Description:** ${stakeholder.description}\n\n`;
        }

        if (stakeholder.questions) {
          if (stakeholder.questions.problemDiscovery && stakeholder.questions.problemDiscovery.length > 0) {
            content += `**Problem Discovery Questions:**\n`;
            stakeholder.questions.problemDiscovery.forEach((q: string, qIndex: number) => {
              content += `${qIndex + 1}. ${q}\n`;
            });
            content += `\n`;
          }

          if (stakeholder.questions.solutionValidation && stakeholder.questions.solutionValidation.length > 0) {
            content += `**Solution Validation Questions:**\n`;
            stakeholder.questions.solutionValidation.forEach((q: string, qIndex: number) => {
              content += `${qIndex + 1}. ${q}\n`;
            });
            content += `\n`;
          }

          if (stakeholder.questions.followUp && stakeholder.questions.followUp.length > 0) {
            content += `**Follow-up Questions:**\n`;
            stakeholder.questions.followUp.forEach((q: string, qIndex: number) => {
              content += `${qIndex + 1}. ${q}\n`;
            });
            content += `\n`;
          }
        }
        content += `---\n\n`;
      });
    }

    content += `\nGenerated by AxWise Customer Research Assistant\nReady for simulation bridge and interview analysis`;
    return content;
  };

  // State to store questionnaire stats for each session
  const [questionnaireStats, setQuestionnaireStats] = useState<Record<string, { questions: number; stakeholders: number }>>({});

  // Helper function to calculate questionnaire stats from session data
  const calculateQuestionnaireStats = (session: ResearchSession) => {
    if (!session?.messages) return { questions: 0, stakeholders: 0 };

    try {
      // Use the same detection logic as other components
      const questionnaireMessages = session.messages.filter((msg: any) =>
        msg.metadata?.comprehensiveQuestions ||
        (msg.content === 'COMPREHENSIVE_QUESTIONS_COMPONENT' && msg.metadata?.comprehensiveQuestions)
      );

      if (questionnaireMessages.length === 0) {
        return { questions: 0, stakeholders: 0 };
      }

      // Get the most recent questionnaire message
      const questionnaireMessage = questionnaireMessages.sort((a: any, b: any) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      )[0];

      if (!questionnaireMessage?.metadata?.comprehensiveQuestions) {
        return { questions: 0, stakeholders: 0 };
      }

      const questionnaire = questionnaireMessage.metadata.comprehensiveQuestions;
      const primaryStakeholders = questionnaire.primaryStakeholders || [];
      const secondaryStakeholders = questionnaire.secondaryStakeholders || [];
      const allStakeholders = [...primaryStakeholders, ...secondaryStakeholders];

      // Count total questions across all categories
      const totalQuestions = allStakeholders.reduce((total: number, stakeholder: any) => {
        const questions = stakeholder.questions || {};
        return total +
          (questions.problemDiscovery?.length || 0) +
          (questions.solutionValidation?.length || 0) +
          (questions.followUp?.length || 0);
      }, 0);

      return {
        questions: totalQuestions,
        stakeholders: allStakeholders.length
      };
    } catch (error) {
      console.error('Error calculating questionnaire stats:', error);
      return { questions: 0, stakeholders: 0 };
    }
  };

  // Helper function to get questionnaire stats (now uses pre-calculated state)
  const getQuestionnaireStats = (sessionId: string) => {
    return questionnaireStats[sessionId] || { questions: 0, stakeholders: 0 };
  };

  // Handle downloading questionnaire
  const handleDownloadQuestionnaire = async (sessionId: string, title: string) => {
    try {
      console.log('📥 Downloading questionnaire for session:', sessionId);

      let questionnaire = null;

      if (sessionId.startsWith('local_')) {
        // Handle local session
        if (typeof window !== 'undefined') {
          const { LocalResearchStorage } = await import('@/lib/api/research');
          const session = LocalResearchStorage.getSession(sessionId);

          if (session?.messages) {
            // Use the same detection logic as other components
            const questionnaireMessage = session.messages.find((msg: any) =>
              msg.metadata?.comprehensiveQuestions ||
              (msg.content === 'COMPREHENSIVE_QUESTIONS_COMPONENT' && msg.metadata?.comprehensiveQuestions)
            );

            if (questionnaireMessage?.metadata?.comprehensiveQuestions) {
              questionnaire = questionnaireMessage.metadata.comprehensiveQuestions;
              console.log('📋 Local questionnaire data for download:', questionnaire);
            }
          }
        }
      } else {
        // Handle backend session
        const response = await fetch(`/api/research/sessions/${sessionId}/questionnaire`);

        if (response.ok) {
          const data = await response.json();
          questionnaire = data.questionnaire;
          console.log('📋 Backend questionnaire data for download:', questionnaire);
        } else {
          const errorText = await response.text();
          console.error('❌ Download failed:', response.status, errorText);
          showToast(`Failed to download questionnaire: ${response.status}`, { variant: 'error' });
          return;
        }
      }

      if (questionnaire) {
        // V3 Enhanced format only - validate structure
        if (!questionnaire.primaryStakeholders && !questionnaire.secondaryStakeholders) {
          throw new Error('Invalid questionnaire format - V3 Enhanced format required');
        }

        // Generate V3 Enhanced format
        const textContent = generateComprehensiveQuestionnaireText(questionnaire, title);

        // Create and download the file
        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `questionnaire-${title.replace(/[^a-zA-Z0-9]/g, '-')}-${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        showToast('Questionnaire downloaded successfully', { variant: 'success' });
      } else {
        showToast('No questionnaire data found for this session', { variant: 'error' });
      }
    } catch (error) {
      console.error('❌ Download error:', error);
      showToast('Failed to download questionnaire', { variant: 'error' });
    }
  };



  // Workflow stage logic
  interface SessionStage {
    id: 'in-progress' | 'questionnaire-ready' | 'simulation-complete';
    label: string;
    description: string;
    questionnaire: boolean;
    simulation: boolean;
    nextActions: string[];
  }

  const getSessionStage = (session: ResearchSession): SessionStage => {
    // Check if simulation is complete (check localStorage for simulation results)
    const simulationResults = JSON.parse(localStorage.getItem('simulation_results') || '[]');
    const hasSimulationResults = simulationResults.some((sim: any) =>
      sim.source_session_id === session.session_id ||
      sim.metadata?.source_session_id === session.session_id
    );

    if (hasSimulationResults) {
      return {
        id: 'simulation-complete',
        label: 'Simulation Complete',
        description: 'Ready for analysis',
        questionnaire: true,
        simulation: true,
        nextActions: ['View Results', 'Download', 'Analyze']
      };
    }

    // Check if questionnaire is generated
    if (session.questions_generated) {
      return {
        id: 'questionnaire-ready',
        label: 'Ready for Simulation',
        description: 'Questionnaire generated',
        questionnaire: true,
        simulation: false,
        nextActions: ['View Questions', 'Start Simulation', 'Continue Chat']
      };
    }

    // Still in progress
    return {
      id: 'in-progress',
      label: 'In Progress',
      description: 'Building research context',
      questionnaire: false,
      simulation: false,
      nextActions: ['Continue Chat']
    };
  };

  // Workflow stage indicator component
  const WorkflowStageIndicator = ({ stage }: { stage: SessionStage }) => {
    const stageConfig = {
      'in-progress': { color: 'bg-yellow-100 text-yellow-800', icon: '🔄' },
      'questionnaire-ready': { color: 'bg-blue-100 text-blue-800', icon: '📋' },
      'simulation-complete': { color: 'bg-green-100 text-green-800', icon: '✅' }
    };

    const config = stageConfig[stage.id];

    return (
      <Badge className={`text-xs ${config.color}`}>
        <span className="mr-1">{config.icon}</span>
        {stage.label}
      </Badge>
    );
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
        <h1 className="text-2xl lg:text-3xl font-bold text-foreground">Research History</h1>
        <p className="text-muted-foreground mt-2">
          {showOnlyWithQuestionnaires
            ? 'Showing research sessions that have generated questionnaires'
            : 'View and manage all your research chat conversations and generated questionnaires'
          }
        </p>

        {/* Enhanced Filter Controls */}
        <Card className="mt-4">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                  <input
                    type="checkbox"
                    id="questionnaire-filter"
                    checked={showOnlyWithQuestionnaires}
                    onChange={toggleSessionFilter}
                    className="rounded border-gray-300"
                  />
                  <label htmlFor="questionnaire-filter" className="text-sm font-medium">
                    Show only sessions with questionnaires
                  </label>
                </div>

                {/* Stage-based filter */}
                <Select value={stageFilter} onValueChange={setStageFilter}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filter by stage" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Stages</SelectItem>
                    <SelectItem value="in-progress">In Progress</SelectItem>
                    <SelectItem value="questionnaire-ready">Ready for Simulation</SelectItem>
                    <SelectItem value="simulation-complete">Simulation Complete</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="text-xs text-muted-foreground">
                Showing {sessions.length} of {allSessions.length} sessions
              </div>
            </div>
          </CardContent>
        </Card>

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
          <Button
            variant="outline"
            onClick={() => {
              fixCorruptedTimestamps();
              loadSessions();
            }}
            className="text-amber-600 hover:text-amber-700"
          >
            <Calendar className="mr-2 h-4 w-4" />
            Fix Timestamps
          </Button>
        </div>
      </div>

      {/* Single Unified Session List */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4 lg:gap-6 mt-6">
        {/* Sessions List */}
        <div className="xl:col-span-2">
          <Card className="h-fit">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Research Sessions
              </CardTitle>
              <CardDescription>
                Your research journey from idea to analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {sessions.map((session) => {
                  const stage = getSessionStage(session);
                  const stats = getQuestionnaireStats(session.session_id);
                  const isSelected = selectedSession?.session_id === session.session_id;

                  return (
                    <Card
                      key={session.session_id}
                      className={`cursor-pointer transition-all hover:shadow-md ${isSelected ? 'ring-2 ring-primary' : ''}`}
                      onClick={() => setSelectedSession(session)}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 min-w-0">
                            {/* Business Idea Title */}
                            <h3 className="font-medium truncate mb-2">
                              {session.business_idea || 'Untitled Research Session'}
                            </h3>

                            {/* Workflow Stage Indicator */}
                            <div className="flex items-center gap-2 mb-3">
                              <WorkflowStageIndicator stage={stage} />
                              <Badge variant="outline" className="text-xs">
                                {session.industry}
                              </Badge>
                            </div>

                            {/* Progress Information */}
                            <div className="flex items-center gap-4 text-sm text-muted-foreground">
                              <span className="flex items-center gap-1">
                                <MessageSquare className="h-3 w-3" />
                                {session.message_count || session.messages?.length || 0} messages
                              </span>

                              {stage.questionnaire && (
                                <span className="flex items-center gap-1">
                                  <FileText className="h-3 w-3" />
                                  {stats.questions} questions, {stats.stakeholders} stakeholders
                                </span>
                              )}

                              <span className="flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                <ClientTimestamp timestamp={session.updated_at || session.created_at} format="localeDateString" />
                              </span>
                            </div>
                          </div>

                          {/* Quick Actions */}
                          <div className="flex items-center gap-1 ml-4">
                            {/* Always show continue chat */}
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation();
                                router.push(`/unified-dashboard/research-chat?session=${session.session_id}`);
                              }}
                              title="Continue conversation"
                            >
                              <MessageSquare className="h-4 w-4" />
                            </Button>

                            {/* Show questionnaire actions if available */}
                            {stage.questionnaire && (
                              <>
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    router.push(`/unified-dashboard/questionnaire/${session.session_id}`);
                                  }}
                                  title="View questionnaire"
                                >
                                  <Eye className="h-4 w-4" />
                                </Button>

                                {!stage.simulation && (
                                  <Button
                                    variant="ghost"
                                    size="sm"
                                    onClick={(e) => {
                                      e.stopPropagation();
                                      router.push(`/unified-dashboard/research?session=${session.session_id}`);
                                    }}
                                    title="Start simulation"
                                  >
                                    <Play className="h-4 w-4" />
                                  </Button>
                                )}
                              </>
                            )}

                            {/* Show results if simulation complete */}
                            {stage.simulation && (
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={(e) => {
                                  e.stopPropagation();
                                  router.push(`/unified-dashboard/simulation-history`);
                                }}
                                title="View simulation results"
                              >
                                <BarChart className="h-4 w-4" />
                              </Button>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
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

        {/* Enhanced Session Details */}
        <div>
          {selectedSession ? (
            <Card className="sticky top-4">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <WorkflowStageIndicator stage={getSessionStage(selectedSession)} />
                  Session Details
                </CardTitle>
                <CardDescription>{getSessionStage(selectedSession).description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Session Info */}
                  <div>
                    <h4 className="font-medium mb-2">Business Idea</h4>
                    <p className="text-sm text-muted-foreground">
                      {selectedSession.business_idea || 'No business idea specified'}
                    </p>
                  </div>

                  {/* Next Actions */}
                  <div>
                    <h4 className="font-medium mb-3">Available Actions</h4>
                    <div className="space-y-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => router.push(`/unified-dashboard/research-chat?session=${selectedSession.session_id}`)}
                        className="w-full justify-start"
                      >
                        <MessageSquare className="h-4 w-4 mr-2" />
                        Continue Conversation
                      </Button>

                      {getSessionStage(selectedSession).questionnaire && (
                        <>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => router.push(`/unified-dashboard/questionnaire/${selectedSession.session_id}`)}
                            className="w-full justify-start"
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            View Questionnaire
                          </Button>

                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDownloadQuestionnaire(selectedSession.session_id, selectedSession.business_idea || 'questionnaire')}
                            className="w-full justify-start"
                          >
                            <Download className="h-4 w-4 mr-2" />
                            Download Questions
                          </Button>

                          {!getSessionStage(selectedSession).simulation && (
                            <Button
                              size="sm"
                              onClick={() => router.push(`/unified-dashboard/research?session=${selectedSession.session_id}`)}
                              className="w-full justify-start"
                            >
                              <Play className="h-4 w-4 mr-2" />
                              Start Simulation
                            </Button>
                          )}
                        </>
                      )}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card className="sticky top-4">
              <CardContent className="p-8 text-center text-muted-foreground">
                <MessageSquare className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Select a session to view details</p>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
