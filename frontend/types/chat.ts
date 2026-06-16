export interface ChatSession {
  id: string;
  title: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  message_count: number;
}

export interface Citation {
  title: string;
  url: string;
  snippet: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  citations: Citation[];
  confidence_score: number | null;
  created_at: string;
}

export interface ChatSessionDetail extends ChatSession {
  messages: ChatMessage[];
}

// SSE event types
export type SSEEvent =
  | { type: "start"; using_web: boolean }
  | { type: "status"; message: string }
  | { type: "token"; content: string }
  | { type: "done"; citations: Citation[] }
  | { type: "error"; error: string };
