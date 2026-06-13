"use client";

import { useAuth } from "../../context/AuthContext";
import { 
  Plus, 
  Search,
  Filter,
  ArrowUpRight,
  Loader2
} from "lucide-react";
import Link from "next/link";
import useSWR from "swr";
import { useState } from "react";
import { applicationStatusLabels } from "@talent-intelligence/shared";
import { HrSidebar } from "../../components/HrSidebar";
import { Pagination } from "../../components/Pagination";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:4000";
const fetcher = (url: string) => fetch(url).then(res => res.json());

const PAGE_SIZE = 10;

export default function HrDashboard() {
  const { user } = useAuth();
  const [appPage, setAppPage] = useState(0);
  
  const { data: jobsData } = useSWR(`${API_BASE}/jobs`, fetcher);
  const { data: appsData, isLoading: appsLoading } = useSWR(
    `${API_BASE}/applications?skip=${appPage * PAGE_SIZE}&limit=${PAGE_SIZE}`, 
    fetcher
  );

  const jobs = jobsData?.items || [];
  const applications = appsData?.items || [];
  const totalApps = appsData?.total || 0;

  const activeJobsCount = jobs.filter((j: any) => j.is_active).length;

  return (
    <div className="flex min-h-screen bg-[#f3f5f0] text-[#18211d]">
      <HrSidebar />

      <main className="ml-64 flex-1 p-10">
        <header className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold">Welcome back, {user?.name}</h1>
            <p className="text-[#607063]">Manage your active roles and candidate pipelines.</p>
          </div>
          <Link 
            href="/hr/jobs/create"
            className="flex items-center gap-2 rounded-xl bg-[#e0563f] px-5 py-2.5 text-sm font-bold text-white shadow-lg shadow-[#e0563f]/20 hover:opacity-90 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <Plus size={18} />
            Create New Job
          </Link>
        </header>

        <div className="grid gap-6 md:grid-cols-3">
          <StatCard label="Active Jobs" value={activeJobsCount.toString()} />
          <StatCard label="Total Applications" value={totalApps.toString()} />
          <StatCard label="Pipeline Health" value="Good" />
        </div>

        <div className="mt-10 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-bold">Recent Applicants</h3>
            <div className="flex items-center gap-2">
              <div className="relative">
                <Search className="absolute left-3 top-2.5 text-[#607063]" size={14} />
                <input 
                  placeholder="Search candidates..." 
                  className="rounded-lg border border-[#d8ded5] bg-white py-2 pl-9 pr-4 text-xs outline-none focus:border-[#e0563f]"
                />
              </div>
              <button className="flex items-center gap-2 rounded-lg border border-[#d8ded5] bg-white px-3 py-2 text-xs font-bold text-[#607063] hover:bg-[#f3f5f0]">
                <Filter size={14} />
                Filter
              </button>
            </div>
          </div>

          <div className="overflow-hidden rounded-2xl border border-black/5 bg-white shadow-sm">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-black/5 bg-[#fbfcfa] text-[10px] font-bold uppercase tracking-wider text-[#607063]">
                <tr>
                  <th className="px-6 py-4">Candidate</th>
                  <th className="px-6 py-4">Job Title</th>
                  <th className="px-6 py-4 text-center">CV Score</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-black/5">
                {appsLoading ? (
                  <tr>
                    <td colSpan={5} className="py-20 text-center">
                      <Loader2 className="mx-auto animate-spin text-[#e0563f]" size={24} />
                    </td>
                  </tr>
                ) : applications.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-20 text-center text-[#607063]">
                      No applications found.
                    </td>
                  </tr>
                ) : (
                  applications.map((app: any) => (
                    <tr key={app.id} className="group hover:bg-[#f3f5f0]/50 transition-colors">
                      <td className="px-6 py-4">
                        <div>
                          <p className="font-bold">{app.candidate_name || "New Candidate"}</p>
                          <p className="text-[10px] text-[#607063]">{app.candidate_email || "Email hidden"}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-[#607063]">
                        {jobs.find((j: any) => j.id === app.job_id)?.title || "Unknown Job"}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {app.cv_score ? (
                          <span className={cn(
                            "inline-block rounded-md px-2 py-1 text-xs font-bold",
                            app.cv_score >= 80 ? "bg-green-100 text-green-700" : 
                            app.cv_score >= 60 ? "bg-yellow-100 text-yellow-700" : 
                            "bg-red-100 text-red-700"
                          )}>
                            {app.cv_score}%
                          </span>
                        ) : (
                          <span className="text-xs text-[#607063] italic">Processing...</span>
                        )}
                      </td>
                      <td className="px-6 py-4">
                        <StatusBadge status={app.status} />
                      </td>
                      <td className="px-6 py-4 text-right">
                        <Link 
                          href={`/hr/applications/${app.id}`}
                          className="inline-flex items-center gap-1 rounded-lg px-3 py-1.5 text-xs font-bold text-[#e0563f] hover:bg-[#fdf6f4] transition-colors"
                        >
                          View Details
                          <ArrowUpRight size={14} />
                        </Link>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <Pagination 
            currentPage={appPage} 
            pageSize={PAGE_SIZE} 
            totalItems={totalApps} 
            onPageChange={setAppPage} 
          />
        </div>
      </main>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const label = applicationStatusLabels[status as keyof typeof applicationStatusLabels] || status;
  const isFail = status.includes("failed");
  const isPass = status.includes("passed") || status.includes("scored") || status === "accepted";

  return (
    <span className={cn(
      "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[10px] font-bold uppercase tracking-wider",
      isFail ? "bg-red-50 text-red-600" :
      isPass ? "bg-green-50 text-green-600" :
      "bg-blue-50 text-blue-600"
    )}>
      {label}
    </span>
  );
}

function StatCard({ label, value }: { label: string, value: string }) {
  return (
    <div className="rounded-2xl border border-black/5 bg-white p-6 shadow-sm">
      <p className="text-sm font-medium text-[#607063]">{label}</p>
      <p className="mt-2 text-3xl font-bold">{value}</p>
    </div>
  );
}

function cn(...inputs: any[]) {
  return inputs.filter(Boolean).join(" ");
}
