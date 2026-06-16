"use client";
import { useState, useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import apiClient from "@/lib/api-client";
import { User } from "@/types/auth";

export function useAuth() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const getUser = useCallback((): User | null => {
    if (typeof window === "undefined") return null;
    const str = localStorage.getItem("user");
    return str ? JSON.parse(str) : null;
  }, []);

  const isAuthenticated = useCallback((): boolean => {
    if (typeof window === "undefined") return false;
    return !!localStorage.getItem("access_token");
  }, []);

  const isAdmin = useCallback((): boolean => {
    const user = getUser();
    return user?.role === "admin";
  }, [getUser]);

  const getErrorMessage = (e: any, defaultMsg: string): string => {
    const detail = e.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail.map((d: any) => `${d.loc[d.loc.length - 1]}: ${d.msg}`).join(", ");
    }
    return defaultMsg;
  };

  const _storeTokens = (access_token: string, refresh_token: string) => {
    localStorage.setItem("access_token", access_token);
    localStorage.setItem("refresh_token", refresh_token);
    const payload = JSON.parse(atob(access_token.split(".")[1]));
    localStorage.setItem(
      "user",
      JSON.stringify({ id: payload.sub, email: payload.email, role: payload.role })
    );
  };

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.post("/auth/login", { email, password });
      const { access_token, refresh_token } = res.data;
      _storeTokens(access_token, refresh_token);
      const payload = JSON.parse(atob(access_token.split(".")[1]));
      if (payload.role === "admin") {
        router.push("/admin");
      } else {
        router.push("/chat");
      }
    } catch (e: any) {
      setError(getErrorMessage(e, "Login failed"));
    } finally {
      setLoading(false);
    }
  }, [router]);

  const register = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.post("/auth/register", { email, password });
      router.push("/login?registered=1");
    } catch (e: any) {
      setError(getErrorMessage(e, "Registration failed"));
    } finally {
      setLoading(false);
    }
  }, [router]);

  const adminLogin = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await apiClient.post("/auth/admin/login", { email, password });
      const { access_token, refresh_token } = res.data;
      _storeTokens(access_token, refresh_token);
      router.push("/admin");
    } catch (e: any) {
      setError(getErrorMessage(e, "Admin login failed"));
    } finally {
      setLoading(false);
    }
  }, [router]);

  const adminRegister = useCallback(
    async (email: string, password: string, inviteCode: string) => {
      setLoading(true);
      setError(null);
      try {
        await apiClient.post("/auth/admin/register", {
          email,
          password,
          invite_code: inviteCode,
        });
        router.push("/login?registered=1");
      } catch (e: any) {
        setError(getErrorMessage(e, "Admin registration failed"));
      } finally {
        setLoading(false);
      }
    },
    [router]
  );

  const logout = useCallback(async () => {
    const refreshToken = localStorage.getItem("refresh_token");
    try {
      if (refreshToken) {
        await apiClient.post("/auth/logout", { refresh_token: refreshToken });
      }
    } catch { /* ignore */ }
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    router.push("/login");
  }, [router]);

  return {
    login, register, adminLogin, adminRegister, logout,
    getUser, isAuthenticated, isAdmin,
    loading, error, setError, mounted,
  };
}
