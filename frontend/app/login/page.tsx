"use client";
import { useState, Suspense } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/use-auth";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Image from "next/image";
import { Bot, Mail, Lock, Loader2, AlertCircle, CheckCircle } from "lucide-react";

function LoginPageContent() {
  const { login, loading, error, setError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const searchParams = useSearchParams();
  const registered = searchParams.get("registered");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await login(email, password);
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4"
      style={{
        background: "radial-gradient(ellipse at top left, oklch(0.14 0.05 25) 0%, oklch(0.09 0.01 25) 60%)"
      }}
    >
      {/* Background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[300px] rounded-full blur-3xl opacity-15"
        style={{ background: "oklch(0.58 0.23 25)" }} />

      <Card className="w-full max-w-md glass border-border/50 relative z-10">
        <CardHeader className="text-center pb-6">
          <div className="flex flex-col items-center justify-center gap-3 mb-2">
            <div className="bg-white/95 px-4 py-2.5 rounded-xl shadow-lg border border-white/10 flex items-center justify-center">
              <Image src="/logo.png" alt="Tech Mahindra Logo" width={140} height={39} className="object-contain" />
            </div>
            <div className="text-xs font-bold uppercase tracking-wider text-red-500 flex items-center gap-1.5 mt-1">
              <span>Ticket Solver Pro AI</span>
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
            </div>
          </div>
          <CardTitle className="text-2xl font-bold mt-2">Welcome back</CardTitle>
          <CardDescription className="text-muted-foreground">
            Sign in to your Ticket Solver Pro AI account
          </CardDescription>
        </CardHeader>
        <CardContent>
          {registered && (
            <div className="flex items-center gap-2 text-sm text-green-400 bg-green-400/10 rounded-lg px-3 py-2 border border-green-400/20 mb-4">
              <CheckCircle className="w-4 h-4 shrink-0" />
              Account created successfully! Please sign in.
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 rounded-lg px-3 py-2 border border-destructive/20">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {error}
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground/80">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  placeholder="admin@platform.local"
                  value={email}
                  onChange={(e) => { setEmail(e.target.value); setError(null); }}
                  className="pl-10 bg-secondary/50 border-border/50 focus:border-primary"
                  required
                />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground/80">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setError(null); }}
                  className="pl-10 bg-secondary/50 border-border/50 focus:border-primary"
                  required
                />
              </div>
            </div>
            <Button
              id="login-submit"
              type="submit"
              className="w-full h-11 font-semibold text-white hover:opacity-90 transition-opacity"
              style={{ background: "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))" }}
              disabled={loading}
            >
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Sign In"}
            </Button>
            <div className="space-y-2 text-center text-sm text-muted-foreground">
              <p>
                Don&apos;t have an account?{" "}
                <Link href="/register" className="text-primary hover:underline font-medium">
                  Sign up
                </Link>
              </p>
              <p>
                Are you an administrator?{" "}
                <Link href="/admin" className="text-red-500 hover:underline font-medium">
                  Admin portal
                </Link>
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginPageContent />
    </Suspense>
  );
}
