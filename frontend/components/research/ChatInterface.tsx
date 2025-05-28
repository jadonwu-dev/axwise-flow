'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Send, Bot, User, Download, Copy, ArrowLeft } from 'lucide-react';
import { AutoSuggestions } from './AutoSuggestions';
import { ContextPanel } from './ContextPanel';
import { StakeholderAlert } from './StakeholderAlert';
import { MultiStakeholderSummary } from './MultiStakeholderSummary';
import { MultiStakeholderChatMessage } from './MultiStakeholderChatMessage';
import { NextStepsChatMessage } from './NextStepsChatMessage';
import { useResearch } from '@/hooks/use-research';
import { sendResearchChatMessage, getResearchSession, type Message as ApiMessage, type ResearchContext } from '@/lib/api/research';

interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  metadata?: {
    questionCategory?: 'discovery' | 'validation' | 'follow_up';
    researchStage?: 'initial' | 'validation' | 'analysis';
  };
}

interface ChatInterfaceProps {
  onComplete?: (questions: any) => void;
  onBack?: () => void;
  loadSessionId?: string;
}

export function ChatInterface({ onComplete, onBack, loadSessionId }: ChatInterfaceProps) {
  const {
    context,
    questions,
    updateContext,
    generateQuestions,
    exportQuestions,
    continueToAnalysis,
    getCurrentStage,
    isLoading: researchLoading,
  } = useResearch();

  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: "Hi! I'm your customer research assistant. I'll help you create targeted research questions for your business idea. Let's start - what's your business idea?",
      role: 'assistant',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStarted, setConversationStarted] = useState(false);
  const [currentSuggestions, setCurrentSuggestions] = useState<string[]>([
    "I have a business idea",
    "I want to decide about one feature",
    "I need help with customer research"
  ]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [showStakeholderAlert, setShowStakeholderAlert] = useState(false);
  const [showMultiStakeholderPlan, setShowMultiStakeholderPlan] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Detect if the business involves multiple stakeholder groups
  const detectMultipleStakeholders = (context: any) => {
    const businessIdea = context.businessIdea?.toLowerCase() || '';
    const targetCustomer = context.targetCustomer?.toLowerCase() || '';
    const problem = context.problem?.toLowerCase() || '';

    const allText = `${businessIdea} ${targetCustomer} ${problem}`;

    // Look for multiple stakeholder indicators
    const stakeholderIndicators = [
      // B2B2C patterns
      ['dealership', 'customer'], ['dealership', 'client'], ['dealership', 'owner'],
      ['business', 'customer'], ['business', 'client'], ['business', 'user'],
      ['company', 'customer'], ['company', 'client'], ['company', 'user'],

      // Multiple user types
      ['owner', 'manager'], ['individual', 'business'], ['consumer', 'enterprise'],
      ['small business', 'enterprise'], ['user', 'admin'], ['customer', 'staff'],

      // Service industry patterns
      ['service', 'customer'], ['provider', 'client'], ['vendor', 'buyer'],

      // Platform patterns
      ['platform', 'user'], ['marketplace', 'buyer'], ['marketplace', 'seller']
    ];

    return stakeholderIndicators.some(([term1, term2]) =>
      allText.includes(term1) && allText.includes(term2)
    );
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load session when loadSessionId changes
  useEffect(() => {
    if (loadSessionId) {
      loadSession(loadSessionId);
    }
  }, [loadSessionId]);

  const loadSession = async (sessionId: string) => {
    try {
      console.log('Loading session:', sessionId);
      const sessionData = await getResearchSession(sessionId);
      console.log('Session data loaded:', sessionData);

      // Update context from session
      updateContext({
        businessIdea: sessionData.business_idea,
        targetCustomer: sessionData.target_customer,
        problem: sessionData.problem,
        questionsGenerated: sessionData.questions_generated,
        multiStakeholderConsidered: sessionData.questions_generated // If questions exist, assume multi-stakeholder was considered
      });

      // Load messages into chat - Note: messages might not be available in the API response
      // For now, we'll start with a fresh conversation when loading a session
      setMessages([
        {
          id: '1',
          content: "Hi! I'm your customer research assistant. I can see you have a previous session. Let's continue from where you left off.",
          role: 'assistant',
          timestamp: new Date(),
        }
      ]);

      // Set session ID
      setSessionId(sessionId);

      console.log('Session loaded successfully');
    } catch (error) {
      console.error('Failed to load session:', error);
    }
  };

  const handleSend = async (messageText?: string) => {
    const textToSend = messageText || input;
    if (!textToSend.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: textToSend,
      role: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setConversationStarted(true);

    // Update context based on conversation
    updateContextFromMessage(textToSend);

    try {
      // Convert messages to API format
      const apiMessages: ApiMessage[] = [...messages, userMessage].map(msg => ({
        id: msg.id,
        content: msg.content,
        role: msg.role,
        timestamp: msg.timestamp.toISOString(),
        metadata: msg.metadata
      }));

      // Call the research API using the new client
      const data = await sendResearchChatMessage({
        messages: apiMessages,
        input: textToSend,
        context: context,
        session_id: sessionId || undefined,
        user_id: undefined, // Will be populated when auth is added
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: data.content,
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          questionCategory: data.metadata?.questionCategory as 'discovery' | 'validation' | 'follow_up' | undefined,
          researchStage: data.metadata?.researchStage as 'initial' | 'validation' | 'analysis' | undefined,
        },
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Update session ID from response
      if (data.session_id && !sessionId) {
        setSessionId(data.session_id);
      }

      // Update suggestions from API response
      if (data.metadata?.suggestions) {
        setCurrentSuggestions(data.metadata.suggestions);
      }

      // Update context from LLM-extracted information in API response
      if (data.metadata?.extracted_context) {
        const extractedContext = data.metadata.extracted_context;
        updateContext({
          businessIdea: extractedContext.business_idea || context.businessIdea,
          targetCustomer: extractedContext.target_customer || context.targetCustomer,
          problem: extractedContext.problem || context.problem,
          questionsGenerated: extractedContext.questions_generated || context.questionsGenerated
        });
      }

      // If questions were generated, generate them using the hook
      if (data.questions) {
        await generateQuestions([...messages, userMessage, assistantMessage]);

        // Add multi-stakeholder message to chat if detected
        const hasMultipleStakeholders = detectMultipleStakeholders(context);
        if (hasMultipleStakeholders) {
          const multiStakeholderMessage: Message = {
            id: Date.now().toString() + '_multistakeholder',
            content: 'MULTI_STAKEHOLDER_COMPONENT',
            role: 'assistant',
            timestamp: new Date()
          };

          const nextStepsMessage: Message = {
            id: Date.now().toString() + '_nextsteps',
            content: 'NEXT_STEPS_COMPONENT',
            role: 'assistant',
            timestamp: new Date()
          };

          setMessages(prev => [...prev, multiStakeholderMessage, nextStepsMessage]);
          updateContext({ multiStakeholderConsidered: true });
        } else {
          // Just add next steps if no multi-stakeholder scenario
          const nextStepsMessage: Message = {
            id: Date.now().toString() + '_nextsteps',
            content: 'NEXT_STEPS_COMPONENT',
            role: 'assistant',
            timestamp: new Date()
          };

          setMessages(prev => [...prev, nextStepsMessage]);
        }

        if (onComplete) {
          onComplete(data.questions);
        }
      }
    } catch (error) {
      console.error('Error:', error);

      // Provide more helpful error messages
      let errorContent = "I'm sorry, I encountered an error. Please try again.";

      if (error instanceof Error) {
        if (error.message.includes('Failed to fetch')) {
          errorContent = "I'm having trouble connecting to the research service. Please check that the backend is running and try again.";
        } else if (error.message.includes('500')) {
          errorContent = "The research service is experiencing issues. Please try rephrasing your message or try again in a moment.";
        }
      }

      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: errorContent,
        role: 'assistant',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const updateContextFromMessage = (message: string) => {
    // Simple approach - let the backend LLM handle context extraction
    // We'll just trigger updates when we get responses from the API
    // The API response will include updated context from LLM analysis
  };

  const handleSuggestionClick = (suggestion: string) => {
    handleSend(suggestion);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const getConversationContext = () => {
    return messages.map(m => `${m.role}: ${m.content}`).join('\n');
  };

  return (
    <div className="w-full max-w-7xl mx-auto">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6">
        {/* Chat Interface */}
        <Card className="lg:col-span-2 flex flex-col h-[500px] lg:h-[600px]">
          {/* Header */}
          <div className="flex items-center justify-between p-3 lg:p-4 border-b">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-sm lg:text-base">Customer Research Assistant</h3>
            </div>
            <div className="flex gap-2">
              {questions && (
                <Button variant="outline" size="sm" onClick={() => exportQuestions('pdf')}>
                  <Download className="h-4 w-4 mr-1 lg:mr-2" />
                  <span className="hidden sm:inline">Export</span>
                </Button>
              )}
            </div>
          </div>

          {/* Messages */}
          <ScrollArea className="flex-1 p-3 lg:p-4">
            <div className="space-y-4">
              {messages.map((message, index) => (
                <div key={message.id}>
                  <div
                    className={`flex gap-2 lg:gap-3 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="flex-shrink-0">
                        <div className="w-6 h-6 lg:w-8 lg:h-8 bg-primary/10 rounded-full flex items-center justify-center">
                          <Bot className="h-3 w-3 lg:h-4 lg:w-4 text-primary" />
                        </div>
                      </div>
                    )}

                    <div
                      className={`max-w-[85%] lg:max-w-[80%] ${
                        message.content === 'MULTI_STAKEHOLDER_COMPONENT' || message.content === 'NEXT_STEPS_COMPONENT'
                          ? ''
                          : `rounded-lg p-2 lg:p-3 text-sm lg:text-base ${
                              message.role === 'user'
                                ? 'bg-primary text-primary-foreground'
                                : 'bg-secondary text-secondary-foreground border border-border'
                            }`
                      }`}
                    >
                  {message.content === 'MULTI_STAKEHOLDER_COMPONENT' ? (
                    <MultiStakeholderChatMessage
                      onContinueWithCurrent={() => {
                        // Add a message confirming the choice
                        const confirmMessage: Message = {
                          id: Date.now().toString() + '_confirm',
                          content: "Great! You'll continue with the current research questions. They're well-suited for your primary stakeholders and will provide valuable insights.",
                          role: 'assistant',
                          timestamp: new Date()
                        };
                        setMessages(prev => [...prev, confirmMessage]);
                      }}
                      onViewDetailedPlan={() => {
                        // Add detailed multi-stakeholder plan to chat
                        const detailedPlanMessage: Message = {
                          id: Date.now().toString() + '_detailed_plan',
                          content: `## 📋 Complete Multi-Stakeholder Research Questionnaire

### ⚠️ **Important: Primary Objective First**
**Start with your primary stakeholder research (dealerships) to validate core assumptions, then expand to secondary stakeholders to refine and validate your approach.**

---

## **Phase 1: Primary Stakeholders - Dealerships (Week 1-2)**
### 🏢 **Target: 5-7 Service Managers, Parts Managers, Service Advisors**

#### **🔍 Problem Discovery Questions:**
1. "Walk me through your current process for getting service approvals from customers."
2. "What's the most frustrating part of your current service approval workflow?"
3. "How much time do you spend each day on service-related communication with customers?"
4. "What happens when customers don't respond to service recommendations quickly?"
5. "How do you currently handle pricing transparency with customers?"

#### **✅ Solution Validation Questions:**
1. "Would an API that automates service approvals be valuable to your dealership?"
2. "What features would be most important in a service approval system?"
3. "How much would you be willing to pay monthly for a system that reduces approval time by 50%?"
4. "What concerns would you have about implementing a new service approval system?"
5. "How do you typically evaluate new technology solutions for your service department?"

#### **💡 Follow-up Questions:**
1. "Who else would be involved in the decision to adopt this type of system?"
2. "What integration requirements would you have with your existing DMS?"
3. "How would you measure the success of this type of solution?"

---

## **Phase 2: Secondary Stakeholders - End Users (Week 3)**

### 🚗 **Car Owners (5-6 interviews)**

#### **🔍 Problem Discovery Questions:**
1. "Describe your last experience getting service work done at a dealership."
2. "What's most frustrating about the service approval process?"
3. "How do you prefer to receive and respond to service recommendations?"
4. "What information do you need to feel confident approving service work?"
5. "How important is pricing transparency before approving service work?"

#### **✅ Solution Validation Questions:**
1. "Would you be interested in a mobile app that lets you approve service work instantly?"
2. "What features would make you trust a digital service approval system?"
3. "How would you want to receive notifications about service recommendations?"
4. "What concerns would you have about approving expensive repairs through an app?"
5. "How do you currently research service recommendations before approving them?"

### 🚛 **Fleet Managers (3-4 interviews)**

#### **🔍 Problem Discovery Questions:**
1. "How do you currently manage service approvals across your fleet?"
2. "What's the biggest challenge in coordinating service work for multiple vehicles?"
3. "How much time do you spend on service-related administrative tasks weekly?"
4. "What reporting do you need for fleet service activities?"
5. "How do you control and track service costs across your fleet?"

#### **✅ Solution Validation Questions:**
1. "Would bulk service approval capabilities be valuable for your fleet operations?"
2. "What reporting features would be essential in a fleet service management system?"
3. "How would you want to set approval limits for different types of service work?"
4. "What integration would you need with your existing fleet management systems?"
5. "How do you typically budget for new fleet management technology?"

---

## **Phase 3: Cross-Stakeholder Validation (Week 4)**

### 🔄 **Synthesis Questions for All Groups:**
1. "Based on what we've learned, does this approach address your main concerns?"
2. "What potential conflicts do you see between different user needs?"
3. "How would you prioritize these features: [list top features from all groups]?"

### 📊 **Expected Deliverables:**
- **Dealership Requirements Document** (API specs, workflow needs, pricing expectations)
- **User Experience Guidelines** (approval preferences, communication channels, trust factors)
- **Fleet Management Specifications** (bulk operations, reporting, integration needs)
- **Feature Priority Matrix** (ranked by stakeholder impact and business value)
- **Go-to-Market Strategy** (tailored messaging for each stakeholder group)

### 🎯 **Success Metrics:**
- **Dealership adoption criteria** clearly defined
- **User acceptance requirements** validated
- **Fleet management needs** documented
- **Pricing strategy** validated across all groups
- **Technical requirements** prioritized by stakeholder value

**This complete questionnaire ensures you gather actionable insights from all stakeholders while maintaining focus on your primary business objectives.**`,
                          role: 'assistant',
                          timestamp: new Date()
                        };
                        setMessages(prev => [...prev, detailedPlanMessage]);
                      }}
                    />
                  ) : message.content === 'NEXT_STEPS_COMPONENT' ? (
                    <NextStepsChatMessage
                      onExportQuestions={() => {
                        exportQuestions('pdf').catch(console.error);
                      }}
                      onStartResearch={() => {
                        continueToAnalysis();
                      }}
                    />
                  ) : (
                    <div className="whitespace-pre-wrap">{message.content}</div>
                  )}
                  {message.content !== 'MULTI_STAKEHOLDER_COMPONENT' && message.content !== 'NEXT_STEPS_COMPONENT' && (
                    <div className="flex items-center justify-between mt-2">
                      <span className="text-xs opacity-70">
                        {message.timestamp.toLocaleTimeString()}
                      </span>
                      {message.role === 'assistant' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyMessage(message.content)}
                          className="h-6 w-6 p-0 opacity-70 hover:opacity-100"
                        >
                          <Copy className="h-3 w-3" />
                        </Button>
                      )}
                    </div>
                  )}
                </div>

                {message.role === 'user' && (
                  <div className="flex-shrink-0">
                    <div className="w-6 h-6 lg:w-8 lg:h-8 bg-muted rounded-full flex items-center justify-center">
                      <User className="h-3 w-3 lg:h-4 lg:w-4 text-muted-foreground" />
                    </div>
                  </div>
                )}
              </div>

              {/* Show suggestions after assistant messages */}
              {message.role === 'assistant' && index === messages.length - 1 && !isLoading && currentSuggestions.length > 0 && (
                <div className="mt-3 ml-8 lg:ml-11">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xs text-muted-foreground">💡 Quick replies:</span>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {currentSuggestions.map((suggestion, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        size="sm"
                        className="h-auto py-1 px-2 text-xs hover:bg-muted"
                        onClick={() => handleSuggestionClick(suggestion)}
                      >
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-2 lg:gap-3 justify-start">
              <div className="flex-shrink-0">
                <div className="w-6 h-6 lg:w-8 lg:h-8 bg-primary/10 rounded-full flex items-center justify-center">
                  <Bot className="h-3 w-3 lg:h-4 lg:w-4 text-primary" />
                </div>
              </div>
              <div className="bg-muted rounded-lg p-2 lg:p-3">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-muted-foreground rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          )}
        </div>
        <div ref={messagesEndRef} />
      </ScrollArea>

          {/* Input */}
          <div className="p-3 lg:p-4 border-t">
            <div className="flex gap-2">
              <Input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Describe your business idea or ask for help..."
                disabled={isLoading}
                className="flex-1 text-sm lg:text-base"
              />
              <Button
                onClick={() => handleSend()}
                disabled={!input.trim() || isLoading}
                size="sm"
              >
                <Send className="h-4 w-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </Card>

        {/* Context Panel - Hidden on mobile, shown on desktop */}
        <div className="hidden lg:block lg:col-span-1">
          <div className="h-[600px] overflow-y-auto space-y-4">
            <ContextPanel
              context={context}
              questions={questions || undefined}
              onExport={() => exportQuestions('pdf')}
              onContinueToAnalysis={continueToAnalysis}
            />
          </div>
        </div>
      </div>
    </div>
  );
}
