"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  LayoutDashboard, 
  Briefcase, 
  Users, 
  Settings, 
  LogOut 
} from "lucide-react";
import { useAuth } from "../context/AuthContext";

export function HrSidebar() {
  const pathname = usePathname();
  const { logout, user } = useAuth();

  const navItems = [
    { label: "Dashboard", href: "/hr", icon: LayoutDashboard },
    { label: "Jobs", href: "/hr/jobs", icon: Briefcase },
    { label: "Applicants", href: "/hr/applicants", icon: Users },
    { label: "Settings", href: "/hr/settings", icon: Settings },
  ];

  return (
    <aside className="fixed h-full w-64 border-r border-black/5 bg-white p-6">
      <div className="mb-10">
        <h2 className="text-xl font-bold tracking-tight">Talent Intelligence</h2>
        <p className="text-xs font-semibold uppercase tracking-wider text-[#e0563f]">Recruiter Pro</p>
      </div>

      <nav className="space-y-1">
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href !== "/hr" && pathname.startsWith(item.href));
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
                isActive 
                  ? "bg-[#f3f5f0] text-[#18211d]" 
                  : "text-[#607063] hover:bg-[#f3f5f0] hover:text-[#18211d]"
              }`}
            >
              <item.icon size={18} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="absolute bottom-6 left-6 right-6">
        <div className="mb-6 rounded-xl bg-[#f3f5f0] p-4">
          <p className="text-[10px] font-bold uppercase tracking-wider text-[#607063]">Account</p>
          <p className="mt-1 truncate text-xs font-bold">{user?.email}</p>
        </div>
        <button
          onClick={logout}
          className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-[#607063] transition-colors hover:bg-red-50 hover:text-red-600"
        >
          <LogOut size={18} />
          Logout
        </button>
      </div>
    </aside>
  );
}
