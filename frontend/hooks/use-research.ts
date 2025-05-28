'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';

export interface ResearchQuestion {
  id: string;
  question: string;
  category: 'discovery' | 'validation' | 'follow_up';
  purpose: string;
  followUpPrompts?: string[];
}

export interface ResearchSession {
  id: string;
  businessIdea: string;
  targetCustomer: string;
  problem: string;
  stage: string;
  questions: ResearchQuestion[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ResearchContext {
  businessIdea?: string;
  targetCustomer?: string;
  problem?: string;
  stage?: string;
  questionsGenerated?: boolean;
  multiStakeholderConsidered?: boolean;
}

export interface GeneratedQuestions {
  problemDiscovery: string[];
  solutionValidation: string[];
  followUp: string[];
}

interface UseResearchReturn {
  // State
  currentSession: ResearchSession | null;
  context: ResearchContext;
  questions: GeneratedQuestions | null;
  isLoading: boolean;
  error: string | null;

  // Actions
  updateContext: (updates: Partial<ResearchContext>) => void;
  generateQuestions: (conversationHistory: any[]) => Promise<GeneratedQuestions | null>;
  saveSession: () => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  exportQuestions: (format: 'pdf' | 'json' | 'csv') => Promise<void>;
  continueToAnalysis: () => void;

  // Utilities
  getCompletionPercentage: () => number;
  getCurrentStage: () => 'initial' | 'business_idea' | 'target_customer' | 'problem_validation' | 'solution_validation';
}

export function useResearch(): UseResearchReturn {
  const [currentSession, setCurrentSession] = useState<ResearchSession | null>(null);
  const [context, setContext] = useState<ResearchContext>({});
  const [questions, setQuestions] = useState<GeneratedQuestions | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  // Update context
  const updateContext = useCallback((updates: Partial<ResearchContext>) => {
    setContext(prev => ({ ...prev, ...updates }));
  }, []);

  // Generate questions using your existing API
  const generateQuestions = useCallback(async (conversationHistory: any[]): Promise<GeneratedQuestions | null> => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/api/research/generate-questions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context,
          conversationHistory,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate questions');
      }

      const data = await response.json();
      const generatedQuestions: GeneratedQuestions = {
        problemDiscovery: data.problemDiscovery || [],
        solutionValidation: data.solutionValidation || [],
        followUp: data.followUp || [],
      };

      setQuestions(generatedQuestions);
      updateContext({ questionsGenerated: true });

      return generatedQuestions;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate questions';
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [context, updateContext]);

  // Save session to your backend
  const saveSession = useCallback(async () => {
    if (!context.businessIdea || !questions) return;

    setIsLoading(true);
    try {
      const sessionData = {
        businessIdea: context.businessIdea,
        targetCustomer: context.targetCustomer || '',
        problem: context.problem || '',
        stage: context.stage || '',
        questions: [
          ...questions.problemDiscovery.map((q, i) => ({
            id: `discovery_${i}`,
            question: q,
            category: 'discovery' as const,
            purpose: 'Understand the problem space',
          })),
          ...questions.solutionValidation.map((q, i) => ({
            id: `validation_${i}`,
            question: q,
            category: 'validation' as const,
            purpose: 'Validate solution fit',
          })),
          ...questions.followUp.map((q, i) => ({
            id: `followup_${i}`,
            question: q,
            category: 'follow_up' as const,
            purpose: 'Gather additional insights',
          })),
        ],
      };

      const response = await fetch('/api/research/sessions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(sessionData),
      });

      if (!response.ok) {
        throw new Error('Failed to save session');
      }

      const savedSession = await response.json();
      setCurrentSession(savedSession);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save session';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [context, questions]);

  // Load existing session
  const loadSession = useCallback(async (sessionId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/research/sessions/${sessionId}`);

      if (!response.ok) {
        throw new Error('Failed to load session');
      }

      const session = await response.json();
      setCurrentSession(session);

      // Reconstruct context and questions from session
      setContext({
        businessIdea: session.businessIdea,
        targetCustomer: session.targetCustomer,
        problem: session.problem,
        stage: session.stage,
        questionsGenerated: true,
      });

      // Group questions by category
      const groupedQuestions: GeneratedQuestions = {
        problemDiscovery: session.questions.filter((q: any) => q.category === 'discovery').map((q: any) => q.question),
        solutionValidation: session.questions.filter((q: any) => q.category === 'validation').map((q: any) => q.question),
        followUp: session.questions.filter((q: any) => q.category === 'follow_up').map((q: any) => q.question),
      };

      setQuestions(groupedQuestions);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load session';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Export questions in different formats
  const exportQuestions = useCallback(async (format: 'pdf' | 'json' | 'csv') => {
    if (!questions) {
      setError('No questions available to export');
      return;
    }

    try {
      // Create export content
      const exportData = {
        businessIdea: context.businessIdea || 'Not specified',
        targetCustomer: context.targetCustomer || 'Not specified',
        problem: context.problem || 'Not specified',
        questions: {
          problemDiscovery: questions.problemDiscovery,
          solutionValidation: questions.solutionValidation,
          followUp: questions.followUp
        },
        generatedAt: new Date().toISOString()
      };

      if (format === 'json') {
        // Export as JSON
        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'research-questions.json';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        // For PDF/CSV, create a formatted text version
        const textContent = `Customer Research Questions
Generated: ${new Date().toLocaleDateString()}

Business Idea: ${exportData.businessIdea}
Target Customer: ${exportData.targetCustomer}
Problem: ${exportData.problem}

PROBLEM DISCOVERY QUESTIONS:
${questions.problemDiscovery.map((q, i) => `${i + 1}. ${q}`).join('\n')}

SOLUTION VALIDATION QUESTIONS:
${questions.solutionValidation.map((q, i) => `${i + 1}. ${q}`).join('\n')}

FOLLOW-UP QUESTIONS:
${questions.followUp.map((q, i) => `${i + 1}. ${q}`).join('\n')}`;

        const blob = new Blob([textContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `research-questions.txt`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to export questions';
      setError(errorMessage);
    }
  }, [questions, context]);

  // Continue to analysis (integrate with your existing dashboard)
  const continueToAnalysis = useCallback(() => {
    // Save session first, then navigate
    saveSession().then(() => {
      router.push('/unified-dashboard/upload');
    });
  }, [saveSession, router]);

  // Get completion percentage
  const getCompletionPercentage = useCallback(() => {
    let completed = 0;
    const total = 4;

    if (context.businessIdea) completed++;
    if (context.targetCustomer) completed++;
    if (context.problem) completed++;
    if (context.questionsGenerated) completed++;

    return Math.round((completed / total) * 100);
  }, [context]);

  // Get current conversation stage
  const getCurrentStage = useCallback((): 'initial' | 'business_idea' | 'target_customer' | 'problem_validation' | 'solution_validation' => {
    if (!context.businessIdea) return 'initial';
    if (!context.targetCustomer) return 'business_idea';
    if (!context.problem) return 'target_customer';
    if (!context.questionsGenerated) return 'problem_validation';
    return 'solution_validation';
  }, [context]);

  // Auto-save context changes
  useEffect(() => {
    if (context.businessIdea && context.targetCustomer && context.problem) {
      // Auto-save when we have enough context
      const timeoutId = setTimeout(() => {
        if (questions) {
          saveSession();
        }
      }, 2000);

      return () => clearTimeout(timeoutId);
    }
  }, [context, questions, saveSession]);

  return {
    // State
    currentSession,
    context,
    questions,
    isLoading,
    error,

    // Actions
    updateContext,
    generateQuestions,
    saveSession,
    loadSession,
    exportQuestions,
    continueToAnalysis,

    // Utilities
    getCompletionPercentage,
    getCurrentStage,
  };
}
