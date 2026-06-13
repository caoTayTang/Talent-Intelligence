"use client";

import { useAuth } from "../../../context/AuthContext";
import { 
  Plus, 
  Briefcase,
  ExternalLink,
  Loader2,
  Users
} from "lucide-react";
import Link from "next/link";
import useSWR from "swr";
import { useState } from "react";
import { HrSidebar } from "../../../components/HrSidebar";
import { Pagination } from "../../../components/Pagination";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";
const fetcher = (url: string) => fetch(url).then(res => res.json());

const PAGE_SIZE = 10;

export default function HrJobsPage() {
  const [page, setPage] = useState(0);
  const { data: jobsData, isLoading } = useSWR(
    `${API_BASE}/jobs?skip=${page * PAGE_SIZE}&limit=${PAGE_SIZE}`, 
    fetcher
  );

  const jobs = jobsData?.items || [];
  const totalJobs = jobsData?.total || 0;

  return (
    <div className="flex min-h-screen bg-[#f3f5f0] text-[#18211d]">
      <HrSidebar />

      <main className="ml-64 flex-1 p-10">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Active Job Posts</h1>
            <p className="text-[#607063]">Manage and monitor all your current job listings.</p>
          </div>
          <Link 
            href="/hr/jobs/create"
            className="flex items-center gap-2 rounded-xl bg-[#e0563f] px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-[#e0563f]/20 hover:opacity-90 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Plus size={18} />
            New Job Post
          </Link>
        </header>

        <div className="grid gap-6">
          {isLoading || !Array.isArray(jobs) ? (
            <div className="flex h-64 items-center justify-center rounded-2xl border border-black/5 bg-white">
              <Loader2 className="animate-spin text-[#e0563f]" size={32} />
            </div>
          ) : jobs.length === 0 ? (
            <div className="flex flex-col items-center justify-center gap-4 rounded-2xl border border-dashed border-[#d8ded5] bg-white py-20">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-[#f3f5f0] text-[#607063]">
                <Briefcase size={32} />
              </div>
              <p className="font-bold text-[#607063]">
                {page > 0 ? "No more jobs on this page." : "No job posts yet."}
              </p>
              {page === 0 && (
                <Link href="/hr/jobs/create" className="text-sm font-bold text-[#e0563f] hover:underline">
                  Create your first job listing
                </Link>
              )}
            </div>
          ) : (
            <>
              {jobs.map((job: any) => (
                <div key={job.id} className="group relative rounded-2xl border border-black/5 bg-white p-6 transition-all hover:shadow-lg hover:shadow-black/5">
                  <div className="flex items-start justify-between">
                    <div className="flex gap-5">
                      <div className="flex h-14 w-14 items-center justify-center rounded-xl bg-[#f3f5f0] text-[#e0563f]">
                        <Briefcase size={28} />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold">{job.title}</h3>
                        <div className="mt-1 flex items-center gap-4 text-sm text-[#607063]">
                          <span className="flex items-center gap-1">
                            <Users size={14} />
                            Applicants: {job.applications?.length || 0}
                          </span>
                          <span>•</span>
                          <span>Posted on {new Date(job.created_at).toLocaleDateString()}</span>
                        </div>
                        <div className="mt-4 flex gap-2">
                          {job.scorecard_json?.criteria?.slice(0, 3).map((c: any) => (
                            <span key={c.id} className="rounded-md bg-[#edf3ea] px-2 py-0.5 text-[10px] font-bold text-[#48604f]">
                              {c.label}
                            </span>
                          ))}
                        </div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <Link 
                        href={`/hr/jobs/${job.id}/edit`}
                        className="rounded-lg border border-[#d8ded5] px-3 py-1.5 text-xs font-bold text-[#607063] hover:bg-[#f3f5f0] hover:text-[#18211d] transition-colors"
                      >
                        Edit Job
                      </Link>
                      <Link 
                        href={`/candidate/jobs/${job.id}`}
                        target="_blank"
                        className="rounded-lg p-2 text-[#607063] hover:bg-[#f3f5f0] hover:text-[#e0563f]"
                      >
                        <ExternalLink size={20} />
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
              <Pagination 
                currentPage={page} 
                pageSize={PAGE_SIZE} 
                totalItems={totalJobs} 
                onPageChange={setPage} 
              />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
