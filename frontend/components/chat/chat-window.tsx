"use client";
import { useEffect, useRef } from "react";
import { ChatMessage, Citation } from "@/types/chat";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, User, Globe, Database, ExternalLink, Loader2 } from "lucide-react";

interface ChatWindowProps {
  messages: ChatMessage[];
  isStreaming: boolean;
  streamingContent: string;
  citations: Citation[];
  usingWeb: boolean;
  loadingStatus: string;
}

export function ChatWindow({
  messages, isStreaming, streamingContent, citations, usingWeb, loadingStatus
}: ChatWindowProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingContent]);

  return (
    <ScrollArea className="flex-1 min-h-0">
      <div className="max-w-3xl mx-auto p-4 space-y-6">
        {messages.map((msg, i) => (
          <MessageBubble key={msg.id || i} message={msg} />
        ))}

        {/* Streaming message */}
        {isStreaming && (
          <div className="flex gap-3 msg-animate">
            <Avatar className="w-8 h-8 shrink-0">
              <AvatarFallback className="text-xs"
                style={{ background: "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))" }}>
                <Bot className="w-4 h-4 text-white" />
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 space-y-2">
              {loadingStatus && !streamingContent && (
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  {loadingStatus}
                </div>
              )}
              {usingWeb && (
                <Badge variant="outline" className="text-xs gap-1 border-blue-500/30 text-blue-400">
                  <Globe className="w-3 h-3" />
                  Using web search
                </Badge>
              )}
              {streamingContent && (
                <div className="prose prose-invert prose-sm max-w-none typing-cursor">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>{streamingContent}</ReactMarkdown>
                </div>
              )}
              {!streamingContent && (
                <div className="flex gap-1">
                  {[0, 1, 2].map(i => (
                    <div key={i} className="w-2 h-2 rounded-full bg-primary pulse-dot"
                      style={{ animationDelay: `${i * 0.2}s` }} />
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>
    </ScrollArea>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div className={`flex gap-3 msg-animate ${isUser ? "flex-row-reverse" : ""}`}>
      <Avatar className="w-8 h-8 shrink-0">
        <AvatarFallback className="text-xs"
          style={{
            background: isUser
              ? "oklch(0.3 0.02 25)"
              : "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))"
          }}>
          {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-white" />}
        </AvatarFallback>
      </Avatar>

      <div className={`flex-1 max-w-[85%] space-y-2 ${isUser ? "items-end flex flex-col" : ""}`}>
        {isUser ? (
          <div className="rounded-2xl rounded-tr-sm px-4 py-2.5 text-sm"
            style={{ background: "oklch(0.2 0.03 25)", border: "1px solid oklch(0.28 0.03 25)" }}>
            {message.content}
          </div>
        ) : (
          <>
            <div className="glass rounded-2xl rounded-tl-sm px-4 py-3">
              <div className="prose prose-invert prose-sm max-w-none">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
              </div>
            </div>
            {message.citations && message.citations.length > 0 && (
              <CitationList citations={message.citations} />
            )}
          </>
        )}
      </div>
    </div>
  );
}

function CitationList({ citations }: { citations: Citation[] }) {
  return (
    <div className="space-y-1.5">
      <div className="text-xs text-muted-foreground flex items-center gap-1">
        <Globe className="w-3 h-3" />
        Web sources
      </div>
      {citations.map((c, i) => (
        <a key={i} href={c.url} target="_blank" rel="noopener noreferrer"
          className="flex items-start gap-2 text-xs text-muted-foreground hover:text-foreground p-2 rounded-lg hover:bg-secondary/30 transition-colors border border-border/30 group">
          <span className="text-primary font-bold shrink-0">[{i + 1}]</span>
          <div className="flex-1 min-w-0">
            <div className="font-medium text-foreground/80 truncate group-hover:text-foreground">{c.title}</div>
            <div className="truncate opacity-60">{c.snippet}</div>
          </div>
          <ExternalLink className="w-3 h-3 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity" />
        </a>
      ))}
    </div>
  );
}
