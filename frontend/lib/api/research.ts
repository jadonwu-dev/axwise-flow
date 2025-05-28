/**
 * Research API Client
 * Handles all customer research related API calls
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: string | Date;
  metadata?: Record<string, any>;
}

export interface ResearchContext {
  businessIdea?: string;
  targetCustomer?: string;
  problem?: string;
  stage?: string;
}

export interface ChatRequest {
  messages: Message[];
  input: string;
  context?: ResearchContext;
  session_id?: string;
  user_id?: string;
}

export interface ChatResponse {
  content: string;
  metadata?: {
    questionCategory?: string;
    researchStage?: string;
    suggestions?: string[];
    extracted_context?: Record<string, any>;
  };
  questions?: GeneratedQuestions;
  session_id?: string;
}

export interface GeneratedQuestions {
  problemDiscovery: string[];
  solutionValidation: string[];
  followUp: string[];
}

export interface ResearchSession {
  id: number;
  session_id: string;
  user_id?: string;
  business_idea?: string;
  target_customer?: string;
  problem?: string;
  industry: string;
  stage: string;
  status: string;
  questions_generated: boolean;
  created_at: string;
  updated_at: string;
  completed_at?: string;
  message_count?: number;
}

/**
 * Send a chat message to the research assistant
 */
export async function sendResearchChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/research/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Generate research questions based on context
 */
export async function generateResearchQuestions(
  context: ResearchContext,
  conversationHistory: Message[]
): Promise<GeneratedQuestions> {
  const response = await fetch(`${API_BASE_URL}/api/research/generate-questions`, {
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
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get list of research sessions
 */
export async function getResearchSessions(limit: number = 20, userId?: string): Promise<ResearchSession[]> {
  const params = new URLSearchParams({ limit: limit.toString() });
  if (userId) {
    params.append('user_id', userId);
  }

  const response = await fetch(`${API_BASE_URL}/api/research/sessions?${params}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get a specific research session by ID
 */
export async function getResearchSession(sessionId: string): Promise<ResearchSession> {
  const response = await fetch(`${API_BASE_URL}/api/research/sessions/${sessionId}`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Delete a research session
 */
export async function deleteResearchSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/research/sessions/${sessionId}`, {
    method: 'DELETE',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }
}

/**
 * Test Gemini connection
 */
export async function testGeminiConnection(): Promise<any> {
  const response = await fetch(`${API_BASE_URL}/api/research/test-gemini`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
  }

  return response.json();
}
