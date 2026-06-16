"use client";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { ChatSession } from "@/types/chat";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Badge } from "@/components/ui/badge";
import Image from "next/image";
import {
  Bot, Plus, Trash2, LogOut, Settings, MessageSquare,
  ChevronRight, Shield
} from "lucide-react";
import { formatDistanceToNow } from "date-fns";

interface SessionSidebarProps {
  chat: any;
  onSelect?: () => void;
}

export function SessionSidebar({ chat, onSelect }: SessionSidebarProps) {
  const router = useRouter();
  const { logout, getUser, isAdmin } = useAuth();
  const user = getUser();
  const admin = isAdmin();
  const { mounted } = useAuth();

  const handleNewChat = async () => {
    const session = await chat.createSession("New Chat");
    router.push(`/chat/${session.id}`);
    onSelect?.();
  };

  const handleSelect = (session: ChatSession) => {
    router.push(`/chat/${session.id}`);
    onSelect?.();
  };

  const handleDelete = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    await chat.deleteSession(sessionId);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-4 border-b border-border/50">
        <div className="flex flex-col gap-2 mb-4">
          <div className="flex items-center gap-2">
            <div className="bg-white/95 px-2.5 py-1.5 rounded-lg flex items-center justify-center shrink-0 shadow-sm border border-white/10">
              <Image src="/logo.png" alt="Tech Mahindra Logo" width={110} height={30} className="object-contain" />
            </div>
            <Badge variant="outline" className="text-[9px] text-red-500 border-red-500/30 px-1 py-0 h-4 uppercase font-bold shrink-0">
              Pro AI
            </Badge>
          </div>
          <span className="font-bold text-xs text-foreground/80 tracking-wide uppercase">Ticket Solver Pro AI</span>
        </div>
        <Button id="sidebar-new-chat" onClick={handleNewChat} className="w-full gap-2 h-9 text-sm font-semibold text-white"
          style={{ background: "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))" }}>
          <Plus className="w-4 h-4" />
          New Chat
        </Button>
      </div>

      {/* Sessions */}
      <ScrollArea className="flex-1 p-2">
        <div className="space-y-1">
          {chat.sessions.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground text-xs">
              <MessageSquare className="w-6 h-6 mx-auto mb-2 opacity-50" />
              No conversations yet
            </div>
          ) : (
            chat.sessions.map((session: ChatSession) => (
              <div
                key={session.id}
                id={`session-${session.id}`}
                onClick={() => handleSelect(session)}
                className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-secondary/50 transition-colors group relative cursor-pointer"
              >
                <div className="flex items-start gap-2">
                  <MessageSquare className="w-3.5 h-3.5 text-muted-foreground mt-0.5 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium truncate">{session.title}</div>
                    <div className="text-xs text-muted-foreground flex items-center gap-1.5 mt-0.5">
                      <span>{session.message_count} msgs</span>
                      <span>·</span>
                      <span>{formatDistanceToNow(new Date(session.created_at), { addSuffix: true })}</span>
                    </div>
                  </div>
                  <button
                    onClick={(e) => handleDelete(e, session.id)}
                    className="opacity-0 group-hover:opacity-100 transition-opacity p-1 hover:text-destructive rounded"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </ScrollArea>

      {/* Footer */}
      <div className="p-3 border-t border-border/50 space-y-1">
        {mounted && admin && (
          <Button id="admin-link" variant="ghost" size="sm" className="w-full justify-start gap-2 text-xs"
            onClick={() => router.push("/admin")}>
            <Shield className="w-3.5 h-3.5 text-primary" />
            Admin Dashboard
          </Button>
        )}
        <div className="flex items-center gap-2 px-2 py-1.5">
          <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold shrink-0 text-white"
            style={{ background: "oklch(0.58 0.23 25)" }}>
            {mounted ? (user?.email?.[0]?.toUpperCase() || "?") : "?"}
          </div>
          <div className="flex-1 min-w-0">
            <div className="text-xs font-medium truncate">{mounted ? user?.email : "Loading..."}</div>
            <Badge variant="outline" className="text-[10px] h-4 px-1">{mounted ? user?.role : "user"}</Badge>
          </div>
          <Button id="logout-btn" variant="ghost" size="icon" className="h-6 w-6 shrink-0"
            onClick={logout}>
            <LogOut className="w-3.5 h-3.5" />
          </Button>
        </div>
      </div>
    </div>
  );
}
