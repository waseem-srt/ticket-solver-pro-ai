"use client";
import { useState, useCallback } from "react";
import apiClient, { API_BASE } from "@/lib/api-client";
import { ChatMessage, ChatSession, ChatSessionDetail, Citation, SSEEvent } from "@/types/chat";

export function useChat() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSessionDetail | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState("");
  const [citations, setCitations] = useState<Citation[]>([]);
  const [usingWeb, setUsingWeb] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState("");

  const fetchSessions = useCallback(async () => {
    const res = await apiClient.get("/chat/sessions");
    setSessions(res.data);
  }, []);

  const createSession = useCallback(async (title = "New Chat") => {
    const res = await apiClient.post("/chat/sessions", { title });
    await fetchSessions();
    return res.data as ChatSession;
  }, [fetchSessions]);

  const loadSession = useCallback(async (sessionId: string) => {
    const res = await apiClient.get(`/chat/sessions/${sessionId}`);
    const detail = res.data as ChatSessionDetail;
    setCurrentSession(detail);
    setMessages(detail.messages);
  }, []);

  const deleteSession = useCallback(async (sessionId: string) => {
    await apiClient.delete(`/chat/sessions/${sessionId}`);
    await fetchSessions();
    if (currentSession?.id === sessionId) {
      setCurrentSession(null);
      setMessages([]);
    }
  }, [currentSession, fetchSessions]);

  const renameSession = useCallback(async (sessionId: string, title: string) => {
    await apiClient.patch(`/chat/sessions/${sessionId}`, { title });
    await fetchSessions();
  }, [fetchSessions]);

  const sendMessage = useCallback(async (sessionId: string, content: string) => {
    if (isStreaming) return;

    // Optimistic user message
    const tempUserMsg: ChatMessage = {
      id: `temp-${Date.now()}`,
      session_id: sessionId,
      role: "user",
      content,
      citations: [],
      confidence_score: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setIsStreaming(true);
    setStreamingContent("");
    setCitations([]);
    setUsingWeb(false);
    setLoadingStatus("Thinking...");

    const token = localStorage.getItem("access_token");
    const response = await fetch(
      `${API_BASE}/api/chat/sessions/${sessionId}/messages`,
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ content }),
      }
    );

    if (!response.ok) {
      setIsStreaming(false);
      setLoadingStatus("");
      return;
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();
    let fullContent = "";
    let finalCitations: Citation[] = [];

    while (reader) {
      const { done, value } = await reader.read();
      if (done) break;
      const text = decoder.decode(value, { stream: true });
      const lines = text.split("\n");
      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const event: SSEEvent = JSON.parse(line.slice(6));
          if (event.type === "start") {
            setUsingWeb(event.using_web);
            setLoadingStatus(event.using_web ? "Searching web..." : "Retrieving from knowledge base...");
          } else if (event.type === "status") {
            setLoadingStatus(event.message);
          } else if (event.type === "token") {
            fullContent += event.content;
            setStreamingContent(fullContent);
            setLoadingStatus("");
          } else if (event.type === "done") {
            finalCitations = event.citations;
            setCitations(finalCitations);
          }
        } catch { /* skip malformed */ }
      }
    }

    // Add final assistant message
    const assistantMsg: ChatMessage = {
      id: `assistant-${Date.now()}`,
      session_id: sessionId,
      role: "assistant",
      content: fullContent,
      citations: finalCitations,
      confidence_score: null,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, assistantMsg]);
    setStreamingContent("");
    setIsStreaming(false);
    setLoadingStatus("");

    // Update session list
    fetchSessions();
  }, [isStreaming, fetchSessions]);

  return {
    sessions, currentSession, messages, isStreaming, streamingContent,
    citations, usingWeb, loadingStatus,
    fetchSessions, createSession, loadSession, deleteSession, renameSession, sendMessage,
    setMessages,
  };
}
