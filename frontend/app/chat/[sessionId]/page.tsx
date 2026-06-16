"use client";
import { useEffect, useRef } from "react";
import { useParams } from "next/navigation";
import { useChat } from "@/hooks/use-chat";
import { ChatWindow } from "@/components/chat/chat-window";
import { ChatInput } from "@/components/chat/chat-input";

export default function ChatSessionPage() {
  const params = useParams();
  const sessionId = params.sessionId as string;
  const chat = useChat();
  const initialized = useRef(false);

  useEffect(() => {
    if (!initialized.current && sessionId) {
      initialized.current = true;
      chat.loadSession(sessionId);
    }
  }, [sessionId]);

  const handleSend = async (content: string) => {
    await chat.sendMessage(sessionId, content);
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <ChatWindow
        messages={chat.messages}
        isStreaming={chat.isStreaming}
        streamingContent={chat.streamingContent}
        citations={chat.citations}
        usingWeb={chat.usingWeb}
        loadingStatus={chat.loadingStatus}
      />
      <ChatInput onSend={handleSend} disabled={chat.isStreaming} />
    </div>
  );
}
