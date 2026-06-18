"use client";

import { useState } from "react";
import { useAuth, UserRole } from "../../context/AuthContext";
import { Building2, UserRound, Loader2, Sparkles, Key, Mail, User as UserIcon } from "lucide-react";
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export default function LoginPage() {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [role, setRole] = useState<UserRole>("candidate");
  
  const { login, register, isLoading } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;
    
    if (isRegistering) {
      if (!name) return;
      await register(email, name, role, password);
    } else {
      await login(email, password, role);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f3f5f0] p-4 text-[#18211d]">
      <div className="w-full max-w-md rounded-2xl border border-black/5 bg-white p-8 shadow-xl shadow-black/5">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[#e0563f] text-white">
            <Sparkles size={24} />
          </div>
          <h1 className="text-2xl font-bold tracking-tight">Talent Intelligence</h1>
          <p className="mt-2 text-sm text-[#607063]">
            {isRegistering ? "Create your account" : "Sign in to your portal"}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegistering && (
            <div className="space-y-1.5">
              <label className="text-sm font-semibold">Full Name</label>
              <div className="relative">
                <UserIcon className="absolute left-3 top-3 text-[#607063]" size={18} />
                <input
                  type="text"
                  placeholder="Daniel Pham"
                  required
                  className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus:border-[#e0563f] focus:ring-1 focus:ring-[#e0563f]"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>
            </div>
          )}

          <div className="space-y-1.5">
            <label className="text-sm font-semibold">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3 text-[#607063]" size={18} />
              <input
                type="email"
                placeholder="name@company.dev"
                required
                className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus:border-[#e0563f] focus:ring-1 focus:ring-[#e0563f]"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-sm font-semibold">Password</label>
            <div className="relative">
              <Key className="absolute left-3 top-3 text-[#607063]" size={18} />
              <input
                type="password"
                placeholder="••••••••"
                required
                className="w-full rounded-lg border border-[#d8ded5] bg-[#fbfcfa] py-2.5 pl-10 pr-4 text-sm outline-none transition-colors focus:border-[#e0563f] focus:ring-1 focus:ring-[#e0563f]"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          {isRegistering ? (
            <div className="space-y-2 pt-2">
              <label className="text-sm font-semibold text-[#18211d]">Role</label>
              <div className="flex items-center gap-2 rounded-xl border border-[#d8ded5] bg-[#f3f5f0] p-3 text-[#607063]">
                <UserRound size={18} />
                <span className="text-xs font-semibold">Candidate (Public)</span>
              </div>
              <p className="text-[10px] text-[#607063]">
                Recruiter accounts must be authorized by an administrator.
              </p>
            </div>
          ) : (
            <div className="space-y-2 pt-2">
              <label className="text-sm font-semibold text-[#18211d]">Sign in as...</label>
              <div className="grid grid-cols-2 gap-4">
                <button
                  type="button"
                  onClick={() => setRole("candidate")}
                  className={cn(
                    "flex flex-col items-center gap-2 rounded-xl border p-3 transition-all",
                    role === "candidate"
                      ? "border-[#e0563f] bg-[#fdf6f4] text-[#e0563f]"
                      : "border-[#d8ded5] bg-white text-[#607063]"
                  )}
                >
                  <UserRound size={18} />
                  <span className="text-xs font-semibold">Candidate</span>
                </button>
                <button
                  type="button"
                  onClick={() => setRole("hr")}
                  className={cn(
                    "flex flex-col items-center gap-2 rounded-xl border p-3 transition-all",
                    role === "hr"
                      ? "border-[#e0563f] bg-[#fdf6f4] text-[#e0563f]"
                      : "border-[#d8ded5] bg-white text-[#607063]"
                  )}
                >
                  <Building2 size={18} />
                  <span className="text-xs font-semibold">Recruiter</span>
                </button>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={isLoading || !email || !password}
            className="flex w-full items-center justify-center gap-2 rounded-xl bg-[#18211d] py-3.5 text-sm font-bold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 mt-4"
          >
            {isLoading ? (
              <Loader2 className="animate-spin" size={18} />
            ) : (
              isRegistering ? "Create Account" : "Sign In"
            )}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={() => setIsRegistering(!isRegistering)}
            className="text-xs font-semibold text-[#e0563f] hover:underline"
          >
            {isRegistering ? "Already have an account? Sign in" : "New here? Create an account"}
          </button>
        </div>
      </div>
    </div>
  );
}
