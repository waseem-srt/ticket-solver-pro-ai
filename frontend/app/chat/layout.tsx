"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useChat } from "@/hooks/use-chat";
import { useAuth } from "@/hooks/use-auth";
import { SessionSidebar } from "@/components/chat/session-sidebar";
import { Sheet, SheetContent } from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { Menu } from "lucide-react";

export default function ChatLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, mounted } = useAuth();
  const chat = useChat();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
      return;
    }
    chat.fetchSessions();
  }, []);

  if (!mounted) {
    return null; // Avoid hydration mismatch on initial render
  }

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex w-72 shrink-0 flex-col border-r border-border/50 bg-card/30">
        <SessionSidebar chat={chat} />
      </aside>

      {/* Mobile sidebar */}
      <Sheet open={sidebarOpen} onOpenChange={setSidebarOpen}>
        <SheetContent side="left" className="w-72 p-0 bg-card border-border/50">
          <SessionSidebar chat={chat} onSelect={() => setSidebarOpen(false)} />
        </SheetContent>
      </Sheet>

      {/* Main content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Mobile header */}
        <div className="md:hidden flex items-center gap-3 p-3 border-b border-border/50 bg-card/30">
          <Button id="mobile-menu-btn" variant="ghost" size="icon" onClick={() => setSidebarOpen(true)}>
            <Menu className="w-5 h-5" />
          </Button>
          <span className="font-semibold gradient-text">Ticket Solver Pro AI</span>
        </div>
        {children}
      </main>
    </div>
  );
}
