"use client";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { useChat } from "@/hooks/use-chat";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import { Bot, LogOut, LayoutDashboard, Ticket, FileText, Users, ChevronRight } from "lucide-react";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const { isAuthenticated, isAdmin, logout, getUser, mounted } = useAuth();

  useEffect(() => {
    if (!isAuthenticated()) {
      router.replace("/login");
    } else if (!isAdmin()) {
      router.replace("/chat");
    }
  }, []);

  const user = getUser();
  const navItems = [
    { href: "/admin", label: "Dashboard", icon: LayoutDashboard },
    { href: "/admin/tickets", label: "Tickets", icon: Ticket },
    { href: "/admin/documents", label: "Documents", icon: FileText },
    { href: "/admin/users", label: "Users", icon: Users },
  ];

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 shrink-0 flex flex-col border-r border-border/50 bg-card/30">
        <div className="p-4 border-b border-border/50">
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2">
              <div className="bg-white/95 px-2.5 py-1.5 rounded-lg flex items-center justify-center shrink-0 shadow-sm border border-white/10">
                <Image src="/logo.png" alt="Tech Mahindra Logo" width={110} height={30} className="object-contain" />
              </div>
            </div>
            <div>
              <div className="text-sm font-bold text-foreground/90 uppercase tracking-wide">Ticket Solver Pro</div>
              <div className="text-xs text-red-500 font-bold uppercase tracking-wider">Admin Panel</div>
            </div>
          </div>
        </div>
        <nav className="flex-1 p-3 space-y-1">
          {navItems.map(({ href, label, icon: Icon }) => (
            <Link key={href} href={href}
              className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm hover:bg-secondary/50 transition-colors text-muted-foreground hover:text-foreground">
              <Icon className="w-4 h-4" />
              {label}
            </Link>
          ))}
          <Link href="/chat"
            className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm hover:bg-secondary/50 transition-colors text-muted-foreground hover:text-foreground">
            <Bot className="w-4 h-4" />
            Back to Chat
          </Link>
        </nav>
        <div className="p-3 border-t border-border/50">
          <div className="flex items-center gap-2 px-2 py-1.5">
            <div className="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold text-white"
              style={{ background: "oklch(0.58 0.23 25)" }}>
              {mounted ? (user?.email?.[0]?.toUpperCase() || "A") : "A"}
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-xs font-medium truncate">{mounted ? user?.email : "Loading..."}</div>
              <div className="text-xs text-muted-foreground">Administrator</div>
            </div>
            <Button id="admin-logout" variant="ghost" size="icon" className="h-6 w-6" onClick={logout}>
              <LogOut className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-auto">
        {children}
      </main>
    </div>
  );
}
