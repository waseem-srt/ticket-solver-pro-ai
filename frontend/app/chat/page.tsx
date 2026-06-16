"use client";
import { useRouter } from "next/navigation";
import { useChat } from "@/hooks/use-chat";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { Bot, Plus, Sparkles, MessageSquare } from "lucide-react";

export default function ChatIndexPage() {
  const router = useRouter();
  const { createSession } = useChat();

  const handleNewChat = async () => {
    const session = await createSession("New Chat");
    router.push(`/chat/${session.id}`);
  };

  return (
    <div className="flex-1 flex items-center justify-center p-8"
      style={{ background: "radial-gradient(ellipse at center, oklch(0.12 0.03 25) 0%, oklch(0.09 0.01 25) 70%)" }}
    >
      <div className="text-center max-w-xl space-y-8">
        <div className="flex justify-center">
          <div className="bg-white/95 px-6 py-3.5 rounded-2xl shadow-2xl border border-white/10 flex items-center justify-center">
            <Image src="/logo.png" alt="Tech Mahindra Logo" width={180} height={50} className="object-contain" />
          </div>
        </div>
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-3">Ticket Solver Pro AI</h1>
          <p className="text-muted-foreground text-lg leading-relaxed">
            Ask questions about support tickets, known issues, and resolutions.
            I&apos;ll search the knowledge base and the web if needed.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-left">
          {[
            { icon: MessageSquare, label: "Ask about tickets", desc: "Query resolved issues" },
            { icon: Sparkles, label: "AI-powered answers", desc: "Llama 3.1 + RAG" },
            { icon: Bot, label: "Web fallback", desc: "Searches web if needed" },
          ].map(({ icon: Icon, label, desc }) => (
            <div key={label} className="glass rounded-xl p-4 space-y-1 hover:border-primary/30 transition-colors">
              <Icon className="w-5 h-5 text-primary mb-2" />
              <div className="text-sm font-medium">{label}</div>
              <div className="text-xs text-muted-foreground">{desc}</div>
            </div>
          ))}
        </div>

        <Button id="new-chat-btn" onClick={handleNewChat} size="lg"
          className="h-12 px-8 text-base font-semibold gap-2 text-white animate-pulse"
          style={{ background: "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))" }}
        >
          <Plus className="w-5 h-5" />
          Start New Chat
        </Button>
      </div>
    </div>
  );
}
