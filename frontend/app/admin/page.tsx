"use client";
import { useEffect, useState } from "react";
import apiClient from "@/lib/api-client";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Ticket, FileText, Users, RefreshCw, Database, Loader2, CheckCircle } from "lucide-react";
import { toast } from "sonner";

export default function AdminDashboard() {
  const [stats, setStats] = useState({ tickets: 0, documents: 0, users: 0 });
  const [reindexing, setReindexing] = useState(false);
  const [reindexResult, setReindexResult] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const [ticketsRes, docsRes, usersRes] = await Promise.allSettled([
        apiClient.get("/tickets?page=1&page_size=1"),
        apiClient.get("/documents"),
        apiClient.get("/admin/users?limit=1"),
      ]);
      setStats({
        tickets: ticketsRes.status === "fulfilled" ? ticketsRes.value.data.total : 0,
        documents: docsRes.status === "fulfilled" ? docsRes.value.data.total : 0,
        users: usersRes.status === "fulfilled" ? usersRes.value.data.total : 0,
      });
    } catch { /* ignore */ }
  };

  const handleReindex = async () => {
    setReindexing(true);
    setReindexResult(null);
    try {
      const res = await apiClient.post("/tickets/reindex");
      setReindexResult(res.data.message);
      toast.success(res.data.message);
    } catch (e: any) {
      toast.error("Reindex failed: " + (e.response?.data?.detail || "Unknown error"));
    } finally {
      setReindexing(false);
    }
  };

  const statCards = [
    { label: "Total Tickets", value: stats.tickets, icon: Ticket, color: "oklch(0.58 0.23 25)" },
    { label: "Documents", value: stats.documents, icon: FileText, color: "oklch(0.65 0.2 150)" },
    { label: "Users", value: stats.users, icon: Users, color: "oklch(0.65 0.2 30)" },
  ];

  return (
    <div className="p-8 space-y-8">
      <div>
        <h1 className="text-3xl font-bold gradient-text">Dashboard</h1>
        <p className="text-muted-foreground mt-1">Manage your Ticket Solver Pro AI</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {statCards.map(({ label, value, icon: Icon, color }) => (
          <Card key={label} className="glass border-border/50">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl flex items-center justify-center"
                style={{ background: `${color}20`, border: `1px solid ${color}40` }}>
                <Icon className="w-6 h-6" style={{ color }} />
              </div>
              <div>
                <div className="text-2xl font-bold">{value.toLocaleString()}</div>
                <div className="text-sm text-muted-foreground">{label}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="glass border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Database className="w-4 h-4 text-primary" />
              Knowledge Base
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Re-index all tickets into ChromaDB vector store for updated RAG retrieval.
            </p>
            {reindexResult && (
              <div className="flex items-center gap-2 text-sm text-green-400 bg-green-400/10 rounded-lg px-3 py-2">
                <CheckCircle className="w-4 h-4" />
                {reindexResult}
              </div>
            )}
            <Button id="reindex-btn" onClick={handleReindex} disabled={reindexing}
              className="gap-2" variant="outline">
              {reindexing ? (
                <><Loader2 className="w-4 h-4 animate-spin" />Indexing...</>
              ) : (
                <><RefreshCw className="w-4 h-4" />Reindex Tickets</>
              )}
            </Button>
          </CardContent>
        </Card>

        <Card className="glass border-border/50">
          <CardHeader>
            <CardTitle className="text-base">Quick Links</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {[
              { href: "/admin/tickets", label: "Upload Ticket CSV" },
              { href: "/admin/documents", label: "Upload Documents" },
              { href: "/admin/users", label: "Manage Users" },
            ].map(({ href, label }) => (
              <a key={href} href={href}
                className="flex items-center justify-between px-3 py-2 rounded-lg hover:bg-secondary/50 transition-colors text-sm">
                {label}
                <span className="text-muted-foreground">→</span>
              </a>
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
