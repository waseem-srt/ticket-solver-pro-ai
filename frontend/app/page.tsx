"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function Home() {
  const router = useRouter();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const token = localStorage.getItem("access_token");
    if (token) {
      try {
        const payload = JSON.parse(atob(token.split(".")[1]));
        router.replace(payload.role === "admin" ? "/admin" : "/chat");
      } catch {
        router.replace("/login");
      }
    } else {
      router.replace("/login");
    }
  }, [router]);

  if (!mounted) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-2 border-primary rounded-full border-t-transparent animate-spin" />
      </div>
    );
  }
  return (
    <div className="flex items-center justify-center min-h-screen">
      <div className="w-8 h-8 border-2 border-primary rounded-full border-t-transparent animate-spin" />
    </div>
  );
}
