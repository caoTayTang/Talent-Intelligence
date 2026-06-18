"use client";

import { useAuth } from "../../../context/AuthContext";
import { 
  LogOut, 
  Briefcase, 
  Bell, 
  Loader2,
  ChevronLeft,
  ChevronRight,
  Search,
  CheckCircle2,
  Clock,
  AlertCircle,
  ArrowRight,
  Sparkles
} from "lucide-react";
import useSWR from "swr";
import Link from "next/link";
import { useState } from "react";
import { applicationStatusLabels } from "@talent-intelligence/shared";
import { Pagination } from "../../../components/Pagination";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";
const fetcher = (url: string) => fetch(url).then(res => res.json());

const PAGE_SIZE = 10;

export default function MyApplicationsPage() {
  const { user, logout } = useAuth();
  const [page, setPage] = useState(0);
  
  // Fetch paginated applications
  const { data: appsData, isLoading: appsLoading } = useSWR(
    `${API_BASE}/applications?skip=${page * PAGE_SIZE}&limit=${PAGE_SIZE}`, 
    fetcher
  );

  // Fetch jobs to map titles
  const { data: jobsData } = useSWR(`${API_BASE}/jobs`, fetcher);

  const applications = appsData?.items || [];
  const totalApps = appsData?.total || 0;
  const jobs = jobsData?.items || [];

  const myApplications = applications.filter((a: any) => a.candidate_id === user?.id);

  return (
    <div className="min-h-screen bg-[#f3f5f0] text-[#18211d]">
      {/* Header */}
      <header className="border-b border-black/5 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-8">
            <Link href="/candidate" className="text-xl font-bold tracking-tight">Talent Intelligence</Link>
            <nav className="hidden space-x-6 md:flex">
              <Link href="/candidate" className="text-sm font-medium text-[#607063] hover:text-[#18211d]">Job Board</Link>
              <Link href="/candidate/applications" className="text-sm font-bold text-[#e0563f]">My Applications</Link>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3 rounded-full border border-black/5 bg-[#fbfcfa] py-1 pl-1 pr-3">
              <div className="flex h-7 w-7 items-center justify-center rounded-full bg-[#e0563f] text-[10px] font-bold text-white uppercase">
                {user?.name?.[0]}
              </div>
              <span className="text-xs font-bold">{user?.name}</span>
            </div>
            <button
              onClick={logout}
              className="rounded-lg p-2 text-[#607063] hover:bg-red-50 hover:text-red-600 transition-colors"
            >
              <LogOut size={18} />
            </button>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-6 py-10">
        <div className="mb-10">
          <h1 className="text-3xl font-bold italic tracking-tight">My Applications</h1>
          <p className="mt-2 text-[#607063]">Track your progress and access technical assessments.</p>
        </div>

        <div className="space-y-6">
          {appsLoading ? (
            <div className="flex h-64 items-center justify-center rounded-3xl border border-black/5 bg-white">
              <Loader2 className="animate-spin text-[#e0563f]" size={32} />
            </div>
          ) : myApplications.length === 0 ? (
            <div className="rounded-3xl border border-dashed border-[#d8ded5] bg-white py-20 text-center">
              <p className="font-bold text-[#607063]">You haven't applied to any jobs yet.</p>
              <Link href="/candidate" className="mt-4 inline-block text-sm font-bold text-[#e0563f] hover:underline">
                Browse Job Board
              </Link>
            </div>
          ) : (
            <>
              <div className="grid gap-4">
                {myApplications.map((app: any) => {
                  const job = jobs.find((j: any) => j.id === app.job_id);
                  const isPending = app.status === "pending_cv";
                  const isFailed = app.status.includes("failed");
                  const isPassed = app.status === "cv_passed" || app.status.includes("test") || app.status === "accepted";

                  return (
                    <div key={app.id} className="group rounded-3xl border border-black/5 bg-white p-6 transition-all hover:border-[#e0563f]/30 hover:shadow-xl hover:shadow-[#e0563f]/5">
                      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                        <div className="flex gap-5">
                          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#f3f5f0] text-[#e0563f]">
                            <Briefcase size={28} />
                          </div>
                          <div>
                            <h4 className="text-xl font-bold">{job?.title || "Active Role"}</h4>
                            <p className="text-xs font-medium text-[#607063]">Applied on {new Date(app.created_at).toLocaleDateString()}</p>
                            
                            <div className="mt-4 flex items-center gap-3">
                               <span className={`inline-flex items-center gap-1.5 rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-wider ${
                                  isFailed ? "bg-red-50 text-red-600" :
                                  isPassed ? "bg-green-50 text-green-600" :
                                  "bg-blue-50 text-blue-600"
                               }`}>
                                  {applicationStatusLabels[app.status as keyof typeof applicationStatusLabels] || app.status}
                               </span>
                               {isPending && <Loader2 className="animate-spin text-[#607063]" size={12} />}
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-4">
                          {app.cv_score && (
                            <div className="text-right hidden md:block">
                               <p className="text-[10px] font-bold uppercase text-[#607063]">AI Score</p>
                               <p className={`text-lg font-black ${
                                  app.cv_score >= 80 ? "text-green-600" :
                                  app.cv_score >= 60 ? "text-yellow-600" :
                                  "text-red-600"
                               }`}>{app.cv_score}%</p>
                            </div>
                          )}
                          <Link 
                            href={`/candidate/applications/${app.id}`}
                            className="flex items-center gap-2 rounded-xl bg-[#18211d] px-6 py-3 text-xs font-bold text-white transition-all hover:bg-[#e0563f]"
                          >
                            Track Application
                            <ArrowRight size={16} />
                          </Link>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              <Pagination 
                currentPage={page} 
                pageSize={PAGE_SIZE} 
                totalItems={totalApps} 
                onPageChange={setPage} 
              />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
