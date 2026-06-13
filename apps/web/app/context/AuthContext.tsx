"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export type UserRole = "hr" | "candidate";

interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string, role: UserRole) => Promise<void>;
  register: (email: string, name: string, role: UserRole, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    const stored = localStorage.getItem("ti_user");
    if (stored) {
      try {
        setUser(JSON.parse(stored));
      } catch (e) {
        console.error("Failed to parse stored user", e);
      }
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string, role: UserRole) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/users/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, role }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Login failed");
      }

      const userData = await res.json();
      setUser(userData);
      localStorage.setItem("ti_user", JSON.stringify(userData));
      
      router.push(userData.role === "hr" ? "/hr" : "/candidate");
    } catch (error) {
      console.error("Login error:", error);
      alert(error instanceof Error ? error.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, name: string, role: UserRole, password: string) => {
    setIsLoading(true);
    try {
      const res = await fetch(`${API_BASE}/users`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, name, role, password }),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Registration failed");
      }

      const userData = await res.json();
      setUser(userData);
      localStorage.setItem("ti_user", JSON.stringify(userData));
      
      router.push(role === "hr" ? "/hr" : "/candidate");
    } catch (error) {
      console.error("Registration error:", error);
      alert(error instanceof Error ? error.message : "Registration failed");
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("ti_user");
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
