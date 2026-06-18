"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "./context/AuthContext";
import { Loader2 } from "lucide-react";

export default function Home() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (isLoading) return;

    if (!user) {
      router.push("/login");
    } else if (user.role === "hr") {
      router.push("/hr");
    } else {
      router.push("/candidate");
    }
  }, [user, isLoading, router]);

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#f3f5f0]">
      <div className="text-center">
        <Loader2 className="mx-auto animate-spin text-[#e0563f]" size={40} />
        <p className="mt-4 font-medium text-[#607063]">Redirecting...</p>
      </div>
    </div>
  );
}
