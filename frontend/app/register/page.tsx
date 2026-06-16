"use client";
import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/use-auth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Image from "next/image";
import { Bot, Mail, Lock, Loader2, AlertCircle, CheckCircle } from "lucide-react";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function RegisterPageContent() {
  const { register, loading, error, setError } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [localError, setLocalError] = useState("");
  const searchParams = useSearchParams();
  const registered = searchParams.get("registered");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirm) {
      setLocalError("Passwords do not match");
      return;
    }
    if (password.length < 8) {
      setLocalError("Password must be at least 8 characters");
      return;
    }
    setLocalError("");
    await register(email, password);
  };

  const displayError = localError || error;

  return (
    <div className="min-h-screen flex items-center justify-center p-4"
      style={{ background: "radial-gradient(ellipse at top right, oklch(0.14 0.05 25) 0%, oklch(0.09 0.01 25) 60%)" }}
    >
      <div className="absolute top-0 right-1/4 w-[500px] h-[300px] rounded-full blur-3xl opacity-15"
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
          <CardTitle className="text-2xl font-bold mt-2">Create account</CardTitle>
          <CardDescription>Join the Ticket Solver Pro AI Platform</CardDescription>
        </CardHeader>
        <CardContent>
          {registered && (
            <div className="flex items-center gap-2 text-sm text-green-400 bg-green-400/10 rounded-lg px-3 py-2 border border-green-400/20 mb-4">
              <CheckCircle className="w-4 h-4" />
              Account created! Please sign in.
            </div>
          )}
          <form onSubmit={handleSubmit} className="space-y-4">
            {displayError && (
              <div className="flex items-center gap-2 text-sm text-destructive bg-destructive/10 rounded-lg px-3 py-2 border border-destructive/20">
                <AlertCircle className="w-4 h-4 shrink-0" />
                {displayError}
              </div>
            )}
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground/80">Email</label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input id="reg-email" type="email" placeholder="you@company.com" value={email}
                  onChange={(e) => { setEmail(e.target.value); setError(null); setLocalError(""); }}
                  className="pl-10 bg-secondary/50 border-border/50" required />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground/80">Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input id="reg-password" type="password" placeholder="Min. 8 characters" value={password}
                  onChange={(e) => { setPassword(e.target.value); setLocalError(""); }}
                  className="pl-10 bg-secondary/50 border-border/50" required />
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-foreground/80">Confirm Password</label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <Input id="reg-confirm" type="password" placeholder="Repeat password" value={confirm}
                  onChange={(e) => { setConfirm(e.target.value); setLocalError(""); }}
                  className="pl-10 bg-secondary/50 border-border/50" required />
              </div>
            </div>
            <Button id="register-submit" type="submit" className="w-full h-11 font-semibold text-white hover:opacity-90 transition-opacity"
              style={{ background: "linear-gradient(135deg, oklch(0.58 0.23 25), oklch(0.65 0.21 40))" }}
              disabled={loading}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : "Create Account"}
            </Button>
            <div className="space-y-2 text-center text-sm text-muted-foreground">
              <p>
                Already have an account?{" "}
                <Link href="/login" className="text-primary hover:underline font-medium">Sign in</Link>
              </p>
              <p>
                Need to register an admin account?{" "}
                <Link href="/admin-register" className="text-red-500 hover:underline font-medium">
                  Register as Admin
                </Link>
              </p>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <Suspense>
      <RegisterPageContent />
    </Suspense>
  );
}
