/**
 * API handlers and message processing for the Customer Research Chat Interface
 * Extracted from ChatInterface.tsx for better modularity
 */

import { Message, ApiResponse, ChatState, ChatActions } from './types';
import { sendResearchChatMessage, getResearchSession, type Message as ApiMessage } from '@/lib/api/research';
import { validateMessage } from '@/lib/config/research-config';
import { formatErrorForUser, logError } from '@/lib/utils/research-error-handler';
import {
  createUserMessage,
  createAssistantMessage,
  extractSuggestions,
  hasCompleteQuestions,
  convertToSimpleQuestions,
  logSuggestionsDebug,
  scrollToBottomIfNeeded
} from './chat-utils';

/**
 * Save questionnaire data to backend
 */
const saveQuestionnaireToBackend = async (sessionId: string, questionnaireData: any): Promise<void> => {
  const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const response = await fetch(`${API_BASE_URL}/api/research/sessions/${sessionId}/questionnaire`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(questionnaireData),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`Failed to save questionnaire: ${errorText}`);
  }

  return response.json();
};

/**
 * Handle sending a message to the research API
 */
export const handleSendMessage = async (
  messageText: string | undefined,
  state: ChatState,
  actions: ChatActions,
  context: any,
  updateContext: (updates: any) => void,
  updateQuestions: (questions: any) => void,
  onComplete?: (questions: any) => void
) => {
  const textToSend = messageText || state.input;
  if (!textToSend.trim() || state.isLoading) return;

  // Validate input
  const validation = validateMessage(textToSend);
  if (!validation.isValid) {
    const errorMessage: Message = {
      id: Date.now().toString(),
      content: validation.error || 'Please check your input and try again.',
      role: 'assistant',
      timestamp: new Date(),
    };
    actions.setMessages(prev => [...prev, errorMessage]);
    return;
  }

  const userMessage = createUserMessage(textToSend);

  actions.setMessages(prev => [...prev, userMessage]);
  actions.setInput('');
  actions.setIsLoading(true);
  actions.setConversationStarted(true);

  // Track request start time for completion timer
  const requestStartTime = Date.now();



  try {
    // Convert messages to API format
    const apiMessages: ApiMessage[] = [...state.messages, userMessage].map(msg => ({
      id: msg.id,
      content: msg.content,
      role: msg.role,
      timestamp: msg.timestamp.toISOString(),
      metadata: msg.metadata
    }));

    // Call the research API using the new client with V3 Simple features enabled
    const data = await sendResearchChatMessage({
      messages: apiMessages,
      input: textToSend,
      context: context,
      session_id: state.sessionId || undefined,
      user_id: undefined, // Will be populated when auth is added
      // Enable V3 Simple features
      enable_enhanced_analysis: true,
      enable_thinking_process: true,
    });



    // Debug: Log what the backend is returning
    console.log('🔧 DUPLICATE DEBUG: Backend response:', {
      hasQuestions: !!data.questions,
      questionsData: data.questions,
      questionsType: typeof data.questions,
      questionsKeys: data.questions ? Object.keys(data.questions) : [],
      hasStakeholders: !!(data.questions as any)?.stakeholders,
      hasEstimatedTime: !!(data.questions as any)?.estimatedTime,
      hasProblemDiscovery: !!(data.questions as any)?.problemDiscovery,
      extractedContext: data.metadata?.extracted_context,
      messageCount: apiMessages.length
    });

    // Calculate completion time for metadata
    const completionTimeMs = Date.now() - requestStartTime;
    const completionTimeSec = Math.round(completionTimeMs / 1000);

    const assistantMessage = createAssistantMessage(data.content, {
      questionCategory: (data.metadata?.questionCategory === 'discovery' ||
                       data.metadata?.questionCategory === 'validation' ||
                       data.metadata?.questionCategory === 'follow_up')
                       ? data.metadata.questionCategory as 'discovery' | 'validation' | 'follow_up' : undefined,
      researchStage: (data.metadata?.researchStage === 'initial' ||
                     data.metadata?.researchStage === 'validation' ||
                     data.metadata?.researchStage === 'analysis')
                     ? data.metadata.researchStage as 'initial' | 'validation' | 'analysis' : undefined,
      completionTimeMs,
      completionTimeSec,
      // Include all other metadata from the API response
      ...data.metadata
    });

    actions.setMessages(prev => [...prev, assistantMessage]);

    // Update session ID from response
    if (data.session_id && !state.sessionId) {
      actions.setSessionId(data.session_id);
    }

    // Update suggestions from API response with better extraction and fallbacks
    const suggestions = extractSuggestions(data, context, hasCompleteQuestions(data.questions));
    actions.setCurrentSuggestions(suggestions);

    logSuggestionsDebug(suggestions, data, context);

    // Update context from LLM-extracted information in API response
    if (data.metadata?.extracted_context) {
      const extractedContext = data.metadata.extracted_context;

      const newContext = {
        businessIdea: extractedContext.business_idea || context.businessIdea,
        targetCustomer: extractedContext.target_customer || context.targetCustomer,
        problem: extractedContext.problem || context.problem,
        questionsGenerated: extractedContext.questions_generated || context.questionsGenerated
      };
      updateContext(newContext);
    }

    // Debug: Log the full API response to see what we're getting
    console.log('🔍 Full API response:', {
      hasQuestions: !!data.questions,
      questionsKeys: data.questions ? Object.keys(data.questions) : [],
      hasMetadata: !!data.metadata,
      metadataKeys: data.metadata ? Object.keys(data.metadata) : [],
      fullData: data
    });

    // Additional debug for questions structure
    console.log('🔍 Detailed Questions Debug:', {
      questionsData: data.questions,
      hasPrimaryStakeholders: !!(data.questions as any)?.primaryStakeholders,
      hasSecondaryStakeholders: !!(data.questions as any)?.secondaryStakeholders,
      primaryCount: (data.questions as any)?.primaryStakeholders?.length || 0,
      secondaryCount: (data.questions as any)?.secondaryStakeholders?.length || 0,
      hasTimeEstimate: !!(data.questions as any)?.timeEstimate
    });

    // Process questions if generated
    if (data.questions) {
      console.log('✅ Processing questions from API response');
      await processGeneratedQuestions(
        data,
        actions,
        updateQuestions,
        updateContext,
        context,
        onComplete
      );
    } else {
      console.log('❌ No questions found in API response');
    }

  } catch (error) {
    logError(error, 'ChatInterface.handleSend');

    // Use error handler for consistent error messages
    const errorContent = formatErrorForUser(error);

    const errorMessage: Message = {
      id: (Date.now() + 1).toString(),
      content: errorContent,
      role: 'assistant',
      timestamp: new Date(),
    };
    actions.setMessages(prev => [...prev, errorMessage]);
  } finally {
    actions.setIsLoading(false);
    // Note: We don't stop thinking here because the thinking process
    // should remain visible after the user message. The thinking will
    // be cleared when the user sends a new message or clears the chat.
  }
};

/**
 * Process generated questions from API response
 */
const processGeneratedQuestions = async (
  data: ApiResponse,
  actions: ChatActions,
  updateQuestions: (questions: any) => void,
  updateContext: (updates: any) => void,
  context: any,
  onComplete?: (questions: any) => void
) => {
  console.log('🔧 DUPLICATE DEBUG: processGeneratedQuestions called with:', {
    questionsData: data.questions,
    hasStakeholders: !!(data.questions as any)?.stakeholders,
    hasEstimatedTime: !!(data.questions as any)?.estimatedTime,
    hasProblemDiscovery: !!(data.questions as any)?.problemDiscovery,
    questionsKeys: data.questions ? Object.keys(data.questions) : []
  });

  // V3 ENHANCED FORMAT ONLY - Process stakeholder-based questions
  // Backend returns: { questions: { primaryStakeholders: [...], secondaryStakeholders: [...], timeEstimate: {...} } }

  console.log('🔧 V3 Enhanced Processing: Backend response received');

  const questionsData = data.questions as any;

  console.log('🔧 V3 Enhanced Processing: Stakeholder data analysis:', {
    hasPrimaryStakeholders: !!questionsData?.primaryStakeholders,
    hasSecondaryStakeholders: !!questionsData?.secondaryStakeholders,
    hasTimeEstimate: !!questionsData?.timeEstimate,
    hasLegacyStakeholders: !!questionsData?.stakeholders,
    hasEstimatedTime: !!questionsData?.estimatedTime,
    primaryStakeholdersLength: questionsData?.primaryStakeholders?.length || 0,
    secondaryStakeholdersLength: questionsData?.secondaryStakeholders?.length || 0,
    legacyStakeholdersStructure: questionsData?.stakeholders ? Object.keys(questionsData.stakeholders) : []
  });

  // Convert legacy format to V3 format if needed
  let processedQuestionsData = questionsData;

  if (!questionsData?.primaryStakeholders && !questionsData?.secondaryStakeholders && questionsData?.stakeholders) {
    console.log('🔧 V3 Enhanced Processing: Converting legacy format to V3 format');

    // Convert legacy stakeholders format to V3 format
    const stakeholders = questionsData.stakeholders;
    processedQuestionsData = {
      primaryStakeholders: stakeholders.primary || [],
      secondaryStakeholders: stakeholders.secondary || [],
      timeEstimate: {
        totalQuestions: (() => {
          // Calculate total questions from all stakeholders
          let total = 0;
          if (stakeholders.primary) {
            stakeholders.primary.forEach((stakeholder: any) => {
              if (stakeholder.questions) {
                total += (stakeholder.questions.problemDiscovery?.length || 0) +
                        (stakeholder.questions.solutionValidation?.length || 0) +
                        (stakeholder.questions.followUp?.length || 0);
              }
            });
          }
          if (stakeholders.secondary) {
            stakeholders.secondary.forEach((stakeholder: any) => {
              if (stakeholder.questions) {
                total += (stakeholder.questions.problemDiscovery?.length || 0) +
                        (stakeholder.questions.solutionValidation?.length || 0) +
                        (stakeholder.questions.followUp?.length || 0);
              }
            });
          }
          return total;
        })(),
        estimatedMinutes: questionsData.estimatedTime || "0-0",
        breakdown: {
          primary: stakeholders.primary?.length || 0,
          secondary: stakeholders.secondary?.length || 0,
          perQuestion: 3
        }
      }
    };

    console.log('🔧 V3 Enhanced Processing: Converted to V3 format:', {
      primaryStakeholders: processedQuestionsData.primaryStakeholders.length,
      secondaryStakeholders: processedQuestionsData.secondaryStakeholders.length,
      totalQuestions: processedQuestionsData.timeEstimate.totalQuestions
    });
  } else {
    console.log('🔧 V3 Enhanced Processing: Using native V3 format');
  }

  // Process V3 enhanced stakeholder-based questions (using converted data if needed)
  const comprehensiveQuestions = {
    primaryStakeholders: (processedQuestionsData.primaryStakeholders || []).map((stakeholder: any) => ({
      name: stakeholder.name || 'Primary Stakeholder',
      description: stakeholder.description || 'Primary stakeholder description',
      questions: {
        problemDiscovery: stakeholder.questions?.problemDiscovery || [],
        solutionValidation: stakeholder.questions?.solutionValidation || [],
        followUp: stakeholder.questions?.followUp || []
      }
    })),
    secondaryStakeholders: (processedQuestionsData.secondaryStakeholders || []).map((stakeholder: any) => ({
      name: stakeholder.name || 'Secondary Stakeholder',
      description: stakeholder.description || 'Secondary stakeholder description',
      questions: {
        problemDiscovery: stakeholder.questions?.problemDiscovery || [],
        solutionValidation: stakeholder.questions?.solutionValidation || [],
        followUp: stakeholder.questions?.followUp || []
      }
    })),
    timeEstimate: {
      totalQuestions: processedQuestionsData.timeEstimate?.totalQuestions || 0,
      estimatedMinutes: processedQuestionsData.timeEstimate?.estimatedMinutes || "0-0",
      breakdown: processedQuestionsData.timeEstimate?.breakdown || {
        primary: 0,
        secondary: 0,
        perQuestion: 3
      }
    }
  };

  console.log('🔧 V3 Enhanced Processing: Generated comprehensive questions:', {
    primaryStakeholders: comprehensiveQuestions.primaryStakeholders.length,
    secondaryStakeholders: comprehensiveQuestions.secondaryStakeholders.length,
    totalQuestions: comprehensiveQuestions.timeEstimate.totalQuestions,
    estimatedMinutes: comprehensiveQuestions.timeEstimate.estimatedMinutes
  });

  // Add comprehensive questions component
  const messageId = Date.now().toString() + '_comprehensive_questions';
  const comprehensiveQuestionsMessage: Message = {
    id: messageId,
    content: 'COMPREHENSIVE_QUESTIONS_COMPONENT',
    role: 'assistant',
    timestamp: new Date(),
    metadata: {
      type: 'component',
      comprehensiveQuestions,
      businessContext: (data as any).context_analysis?.business_idea || context.businessIdea
    }
  };

  console.log('🔧 V3 Enhanced Processing: Adding comprehensive questions component');

  actions.setMessages(prev => {
    // Check if we already have a COMPREHENSIVE_QUESTIONS_COMPONENT with actual questions
    const existingComprehensiveComponent = prev.find(m => {
      if (m.content !== 'COMPREHENSIVE_QUESTIONS_COMPONENT') return false;
      const existingQuestions = m.metadata?.comprehensiveQuestions?.timeEstimate?.totalQuestions || 0;
      return existingQuestions > 0; // Only consider it existing if it has actual questions
    });

    if (existingComprehensiveComponent) {
      console.log('🔧 V3 Enhanced Processing: Questions component already exists, skipping');
      return prev; // Return unchanged array
    }

    // If we have an empty component and this new one has questions, replace the empty one
    const emptyComprehensiveComponent = prev.find(m => {
      if (m.content !== 'COMPREHENSIVE_QUESTIONS_COMPONENT') return false;
      const existingQuestions = m.metadata?.comprehensiveQuestions?.timeEstimate?.totalQuestions || 0;
      return existingQuestions === 0; // Find empty component
    });

    if (emptyComprehensiveComponent && comprehensiveQuestions.timeEstimate.totalQuestions > 0) {
      console.log('🔧 V3 Enhanced Processing: Replacing empty component with actual questions');
      // Remove the empty component and add the new one
      const filteredMessages = prev.filter(m => m.id !== emptyComprehensiveComponent.id);
      return [...filteredMessages, comprehensiveQuestionsMessage];
    }

    return [...prev, comprehensiveQuestionsMessage];
  });

  // Update local questions state for backward compatibility
  const allQuestions = convertToSimpleQuestions(comprehensiveQuestions);

  actions.setLocalQuestions(allQuestions);
  updateQuestions(allQuestions);
  updateContext({ questionsGenerated: true });

  // Save comprehensive questionnaire data to backend if we have a session ID
  if (data.session_id && !data.session_id.startsWith('local_')) {
    try {
      await saveQuestionnaireToBackend(data.session_id, comprehensiveQuestions);
      console.log('✅ Questionnaire saved to backend successfully');
    } catch (error) {
      console.error('❌ Failed to save questionnaire to backend:', error);
      // Don't throw error - this is not critical for the user experience
    }
  }

  // Always add next steps for comprehensive questions
  const nextStepsMessage: Message = {
    id: Date.now().toString() + '_nextsteps',
    content: 'NEXT_STEPS_COMPONENT',
    role: 'assistant',
    timestamp: new Date(),
    metadata: {
      type: 'component',
      timeEstimate: comprehensiveQuestions.timeEstimate
    }
  };

  actions.setMessages(prev => [...prev, nextStepsMessage]);

  if (onComplete) {
    onComplete(allQuestions);
  }

  return; // V3 Enhanced format processing complete
};

// Legacy stakeholder processing removed - V3 Enhanced format only

/**
 * Handle suggestion click
 */
export const handleSuggestionClick = (
  suggestion: string,
  state: ChatState,
  actions: ChatActions,
  context: any,
  updateContext: (updates: any) => void,
  updateQuestions: (questions: any) => void,
  onComplete?: (questions: any) => void
) => {
  console.log('🔧 Suggestion clicked:', suggestion);
  handleSendMessage(suggestion, state, actions, context, updateContext, updateQuestions, onComplete);
};

/**
 * Load a research session
 */
export const loadSession = async (
  sessionId: string,
  actions: ChatActions,
  updateContext: (updates: any) => void
) => {
  try {
    console.log('Loading session:', sessionId);

    let sessionData;

    // Check if it's a local session (starts with 'local_')
    if (sessionId.startsWith('local_')) {
      console.log('Loading local session from localStorage');
      // Import LocalResearchStorage dynamically to avoid SSR issues
      const { LocalResearchStorage } = await import('@/lib/api/research');
      sessionData = LocalResearchStorage.getSession(sessionId);

      if (!sessionData) {
        console.error('Local session not found in localStorage:', sessionId);
        return;
      }
    } else {
      // Load from backend API
      sessionData = await getResearchSession(sessionId);
    }

    console.log('Session data loaded:', sessionData);

    // Update context from session
    updateContext({
      businessIdea: sessionData.business_idea,
      targetCustomer: sessionData.target_customer,
      problem: sessionData.problem,
      questionsGenerated: sessionData.questions_generated,
      multiStakeholderConsidered: sessionData.questions_generated // If questions exist, assume multi-stakeholder was considered
    });

    // Load actual messages from the session if available
    if (sessionData.messages && sessionData.messages.length > 0) {
      console.log(`Loading ${sessionData.messages.length} messages from session`);

      // Convert message format to chat interface format
      const chatMessages = sessionData.messages.map((msg: any, index: number) => ({
        id: msg.id || `loaded_${index}`,
        content: msg.content,
        role: msg.role,
        timestamp: msg.timestamp ? new Date(msg.timestamp) : new Date(),
        metadata: msg.metadata || {}
      }));

      actions.setMessages(chatMessages);
      actions.setConversationStarted(true);
    } else {
      // If no messages, start with a welcome message
      actions.setMessages([
        {
          id: '1',
          content: "Hi! I'm your customer research assistant. I can see you have a previous session. Let's continue from where you left off.",
          role: 'assistant',
          timestamp: new Date(),
        }
      ]);
    }

    // Set session ID
    actions.setSessionId(sessionId);

    console.log('Session loaded successfully with', sessionData.messages?.length || 0, 'messages');
  } catch (error) {
    console.error('Failed to load session:', error);
  }
};
