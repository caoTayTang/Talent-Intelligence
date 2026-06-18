"use client";

import { useAuth } from "../../context/AuthContext";
import { 
  LogOut, 
  Briefcase, 
  FileText, 
  Bell, 
  Search, 
  MapPin, 
  Clock,
  ArrowRight,
  Loader2,
  Sparkles
} from "lucide-react";
import useSWR from "swr";
import Link from "next/link";
import { useState } from "react";
import { Pagination } from "../../components/Pagination";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";
const fetcher = (url: string) => fetch(url).then(res => res.json());

const PAGE_SIZE = 10;

export default function CandidateDashboard() {
  const { user, logout } = useAuth();
  const [jobPage, setJobPage] = useState(0);
  
  // Fetch paginated jobs
  const { data: jobsData, isLoading: jobsLoading } = useSWR(
    `${API_BASE}/jobs?skip=${jobPage * PAGE_SIZE}&limit=${PAGE_SIZE}`, 
    fetcher
  );

  // Fetch all applications for sidebar
  const { data: appsData, isLoading: appsLoading } = useSWR(`${API_BASE}/applications`, fetcher);

  const jobs = jobsData?.items || [];
  const totalJobs = jobsData?.total || 0;
  const applications = appsData?.items || [];

  const myApplications = applications.filter((a: any) => a.candidate_id === user?.id);

  return (
    <div className="min-h-screen bg-[#f3f5f0] text-[#18211d]">
      {/* Header */}
      <header className="border-b border-black/5 bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div className="flex items-center gap-8">
            <Link href="/candidate" className="text-xl font-bold tracking-tight">Talent Intelligence</Link>
            <nav className="hidden space-x-6 md:flex">
              <Link href="/candidate" className="text-sm font-bold text-[#e0563f]">Job Board</Link>
              <Link href="/candidate/applications" className="text-sm font-medium text-[#607063] hover:text-[#18211d]">My Applications</Link>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            <button className="relative text-[#607063] hover:text-[#18211d]">
              <Bell size={20} />
              {myApplications.length > 0 && (
                <span className="absolute -right-0.5 -top-0.5 h-2 w-2 rounded-full bg-[#e0563f]" />
              )}
            </button>
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

      <main className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-10 flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold italic tracking-tight">Discover your next role</h1>
            <p className="mt-2 text-[#607063]">Browse opportunities curated by our AI-powered matching engine.</p>
          </div>
          
          <div className="relative w-full max-w-sm">
            <Search className="absolute left-4 top-3.5 text-[#607063]" size={18} />
            <input 
              placeholder="Search by title, skill, or keyword..."
              className="w-full rounded-2xl border border-black/5 bg-white py-3.5 pl-12 pr-4 text-sm outline-none focus:border-[#e0563f] shadow-sm shadow-black/5"
            />
          </div>
        </div>

        <div className="grid gap-8 lg:grid-cols-3">
          {/* Main Job Feed */}
          <div className="lg:col-span-2 space-y-6">
            <h3 className="flex items-center gap-2 text-lg font-bold">
              <Briefcase size={20} className="text-[#e0563f]" />
              Featured Opportunities
            </h3>

            {jobsLoading || !Array.isArray(jobs) ? (
              <div className="flex h-64 items-center justify-center rounded-3xl border border-black/5 bg-white">
                <Loader2 className="animate-spin text-[#e0563f]" size={32} />
              </div>
            ) : jobs.length === 0 ? (
              <div className="rounded-3xl border border-dashed border-[#d8ded5] bg-white py-20 text-center">
                <p className="font-bold text-[#607063]">
                   {jobPage > 0 ? "No more jobs on this page." : "No open positions at the moment."}
                </p>
              </div>
            ) : (
              <>
                <div className="grid gap-4">
                  {jobs.filter(j => j.is_active).map((job: any) => (
                    <Link 
                      key={job.id} 
                      href={`/candidate/jobs/${job.id}`}
                      className="group block rounded-3xl border border-black/5 bg-white p-6 transition-all hover:border-[#e0563f]/30 hover:shadow-xl hover:shadow-[#e0563f]/5"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex gap-5">
                          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#f3f5f0] text-[#e0563f] group-hover:bg-[#e0563f] group-hover:text-white transition-colors">
                            <Briefcase size={28} />
                          </div>
                          <div>
                            <h4 className="text-xl font-bold group-hover:text-[#e0563f] transition-colors">{job.title}</h4>
                            <div className="mt-2 flex flex-wrap items-center gap-y-2 gap-x-4 text-xs font-medium text-[#607063]">
                              <span className="flex items-center gap-1.5"><MapPin size={14} /> Remote / Office</span>
                              <span className="flex items-center gap-1.5"><Clock size={14} /> Full-time</span>
                              <span className="flex items-center gap-1.5 rounded-full bg-[#f3f5f0] px-2 py-0.5 text-[10px] font-bold text-[#18211d]">
                                <Sparkles size={10} className="text-[#e0563f]" /> AI Verified
                              </span>
                            </div>
                            
                            <p className="mt-4 line-clamp-2 text-sm leading-relaxed text-[#607063]">
                              {job.description}
                            </p>

                            <div className="mt-6 flex flex-wrap gap-2">
                              {job.scorecard_json?.criteria?.slice(0, 4).map((c: any) => (
                                <span key={c.id} className="rounded-lg bg-[#edf3ea] px-2.5 py-1 text-[10px] font-bold text-[#48604f]">
                                  {c.label}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#f3f5f0] text-[#607063] transition-all group-hover:scale-110 group-hover:bg-[#e0563f] group-hover:text-white">
                          <ArrowRight size={20} />
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
                <Pagination 
                  currentPage={jobPage} 
                  pageSize={PAGE_SIZE} 
                  totalItems={totalJobs} 
                  onPageChange={setJobPage} 
                />
              </>
            )}
          </div>

          {/* Sidebar / My Activity */}
          <div className="space-y-8">
            <section className="rounded-3xl border border-black/5 bg-white p-8 shadow-sm">
              <h3 className="mb-6 text-lg font-bold">My Activity</h3>
              <div className="space-y-4">
                {appsLoading ? (
                  <div className="flex py-4 justify-center"><Loader2 className="animate-spin text-[#e0563f]" size={20} /></div>
                ) : myApplications.length === 0 ? (
                  <p className="text-sm text-[#607063]">You haven't applied to any jobs yet.</p>
                ) : (
                  myApplications.map((app: any) => (
                    <Link 
                      key={app.id} 
                      href={`/candidate/applications/${app.id}`}
                      className="flex items-center justify-between rounded-2xl bg-[#fbfcfa] p-4 border border-black/5 hover:border-[#e0563f]/30 hover:shadow-sm transition-all group/app"
                    >
                      <div>
                        <p className="text-xs font-bold truncate max-w-[120px] group-hover/app:text-[#e0563f] transition-colors">
                          {jobs?.find((j: any) => j.id === app.job_id)?.title || "Active Job"}
                        </p>
                        <p className="mt-0.5 text-[10px] font-medium text-[#607063] uppercase tracking-wider">{app.status.replace("_", " ")}</p>
                      </div>
                      <ArrowRight size={14} className="text-[#607063] group-hover/app:text-[#e0563f] transition-colors" />
                    </Link>
                  ))
                )}
              </div>
            </section>

            <section className="rounded-3xl bg-[#18211d] p-8 text-white shadow-xl shadow-black/10">
              <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-white/10 text-[#e0563f]">
                <FileText size={24} />
              </div>
              <h4 className="text-lg font-bold italic tracking-tight">AI Resume Feedback</h4>
              <p className="mt-2 text-sm leading-relaxed text-white/60">
                Apply to any job to unlock instant AI feedback and technical assessments tailored to your profile.
              </p>
              <button className="mt-6 w-full rounded-xl bg-white py-3 text-xs font-bold text-[#18211d] transition-transform hover:scale-[1.02] active:scale-[0.98]">
                Upgrade to Pro
              </button>
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}
