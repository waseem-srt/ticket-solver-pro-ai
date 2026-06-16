"use client";
import { useRef, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { SendHorizonal, Loader2 } from "lucide-react";

interface ChatInputProps {
  onSend: (content: string) => void;
  disabled?: boolean;
}

export function ChatInput({ onSend, disabled }: ChatInputProps) {
  const [value, setValue] = useState("");
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = useCallback(() => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
    }
  }, [value, disabled, onSend]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setValue(e.target.value);
    // Auto-resize
    const el = e.target;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 200)}px`;
  };

  return (
    <div className="p-4 border-t border-border/50">
      <div className="max-w-3xl mx-auto">
        <div className="flex gap-3 items-end glass rounded-2xl p-2">
          <Textarea
            id="chat-input"
            ref={textareaRef}
            value={value}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder="Ask about tickets, issues, or resolutions... (Enter to send, Shift+Enter for newline)"
            className="flex-1 min-h-[44px] max-h-[200px] resize-none bg-transparent border-none shadow-none focus-visible:ring-0 text-sm leading-relaxed"
            disabled={disabled}
            rows={1}
          />
          <Button
            id="send-btn"
            onClick={handleSend}
            disabled={disabled || !value.trim()}
            size="icon"
            className="h-9 w-9 rounded-xl shrink-0"
            style={{
              background: value.trim() && !disabled
                ? "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))"
                : undefined
            }}
          >
            {disabled ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <SendHorizonal className="w-4 h-4" />
            )}
          </Button>
        </div>
        <p className="text-xs text-muted-foreground text-center mt-2">
          Powered by Llama 3.1 + RAG · Web search fallback enabled
        </p>
      </div>
    </div>
  );
}
